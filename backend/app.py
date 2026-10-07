import os
import uuid
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from database import fetch_one, fetch_all, execute
from currency import inr_to_foreign, get_rate
from ai_service import analyze_payment, answer_question
from price_advisor import live_price_advisor

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = Flask(__name__)
CORS(app)


def _frontend_file(filename):
    path = FRONTEND_DIR / filename
    if path.is_file():
        return send_from_directory(FRONTEND_DIR, filename)
    return jsonify({"error": "Frontend file not found"}), 404


@app.get("/")
def home():
    return _frontend_file("login.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "TravelPay AI"})


@app.get("/api/test")
def test():
    return jsonify({"status": "ok", "message": "TravelPay AI backend is running"})


@app.get("/api/mysql-test")
def mysql_test():
    row = fetch_one("SELECT 1 AS ok")
    return jsonify({"mysql": "connected", "result": row["ok"] if row else None})


@app.get("/api/profile/<int:user_id>")
def profile(user_id):
    row = fetch_one("""
        SELECT u.user_id,u.name,u.country,u.home_currency,
               b.total_budget,b.spent_amount,b.remaining_amount
        FROM users u JOIN budgets b ON b.user_id=u.user_id
        WHERE u.user_id=%s
    """, (user_id,))
    if not row:
        return jsonify({"error": "User not found"}), 404
    return jsonify(row)


@app.post("/api/profile")
def create_profile():
    data = request.get_json() or {}
    try:
        name = str(data["name"]).strip()
        country = str(data["country"]).strip()
        currency = str(data["home_currency"]).upper().strip()
        budget = float(data["total_budget"])
        if not name or not country or budget <= 0:
            raise ValueError("Enter valid profile details")
        user_id = execute(
            "INSERT INTO users(name,country,home_currency) VALUES(%s,%s,%s)",
            (name, country, currency),
        )
        execute(
            "INSERT INTO budgets(user_id,total_budget,spent_amount,remaining_amount) VALUES(%s,%s,0,%s)",
            (user_id, budget, budget),
        )
        return jsonify({"user_id": user_id, "message": "Traveler profile created"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.get("/api/dashboard/<int:user_id>")
def dashboard(user_id):
    profile = fetch_one("""
        SELECT u.name,u.country,u.home_currency,b.total_budget,b.spent_amount,b.remaining_amount
        FROM users u JOIN budgets b ON b.user_id=u.user_id WHERE u.user_id=%s
    """, (user_id,))
    if not profile:
        return jsonify({"error": "User not found"}), 404
    tx = fetch_all("""
        SELECT transaction_id,merchant_name,upi_id,amount_inr,amount_foreign,
               foreign_currency,category,risk_level,ai_recommendation,status,
               reference_code,transaction_date
        FROM transactions WHERE user_id=%s ORDER BY transaction_date DESC
    """, (user_id,))
    return jsonify({"profile": profile, "transactions": tx})


@app.post("/api/analyze-payment")
def analyze_payment_route():
    data = request.get_json() or {}
    try:
        user_id = int(data["user_id"])
        merchant = str(data.get("merchant", "")).strip()
        amount_inr = float(data["amount_inr"])
        if not merchant or amount_inr <= 0:
            raise ValueError("Merchant and valid amount are required")
        profile = fetch_one("""
            SELECT u.home_currency,b.total_budget,b.spent_amount
            FROM users u JOIN budgets b ON b.user_id=u.user_id WHERE u.user_id=%s
        """, (user_id,))
        if not profile:
            return jsonify({"error": "User not found"}), 404
        currency = str(data.get("currency") or profile["home_currency"]).upper()
        converted = inr_to_foreign(amount_inr, currency)
        insight = analyze_payment(
            merchant,
            amount_inr,
            converted,
            currency,
            float(profile["spent_amount"]),
            float(profile["total_budget"]),
        )
        city = str(data.get("city", "")).strip()
        item = str(data.get("item", "")).strip()
        price_check = None
        if city and item:
            price_check = live_price_advisor(city, item, amount_inr)
            if price_check.get("found") and price_check.get("assessment") == "EXPENSIVE":
                insight["risk_level"] = "MEDIUM"
                insight["recommendation"] += " Live price evidence also suggests this offer is above the observed market range."
        return jsonify({
            "merchant": merchant,
            "amount_inr": amount_inr,
            "amount_foreign": converted,
            "currency": currency,
            "exchange_rate": get_rate(currency),
            "price_check": price_check,
            **insight,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.post("/api/price-advisor")
def price_advisor_route():
    data = request.get_json() or {}
    try:
        city = str(data["city"]).strip()
        item = str(data["item"]).strip()
        offered = float(data["offered_price"])
        if not city or not item or offered <= 0:
            raise ValueError("City, item/service and offered price are required")
        return jsonify(live_price_advisor(city, item, offered))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.get("/api/price-status")
def price_status():
    from price_advisor import provider_status
    return jsonify(provider_status())


@app.post("/api/transactions")
def create_transaction():
    data = request.get_json() or {}
    try:
        user_id = int(data["user_id"])
        amount_inr = float(data["amount_inr"])
        amount_foreign = float(data["amount_foreign"])
        ref = "TPAI-" + uuid.uuid4().hex[:10].upper()
        txid = execute("""
          INSERT INTO transactions
          (user_id,merchant_name,upi_id,amount_inr,amount_foreign,foreign_currency,
           category,risk_level,ai_recommendation,status,reference_code)
          VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,'SUCCESS',%s)
        """, (
            user_id, data["merchant"], data.get("upi_id", ""), amount_inr, amount_foreign,
            data["currency"], data.get("category", "Other"), data.get("risk_level", "LOW"),
            data.get("recommendation", ""), ref,
        ))
        execute("""UPDATE budgets SET spent_amount=spent_amount+%s,
                   remaining_amount=total_budget-(spent_amount+%s) WHERE user_id=%s""",
                (amount_foreign, amount_foreign, user_id))
        return jsonify({"status": "success", "transaction_id": txid, "reference_code": ref,
                        "message": "Simulated payment recorded"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.post("/api/assistant")
def assistant():
    data = request.get_json() or {}
    try:
        user_id = int(data["user_id"])
        profile = fetch_one("""SELECT u.name,u.home_currency,b.total_budget,b.spent_amount
          FROM users u JOIN budgets b ON b.user_id=u.user_id WHERE u.user_id=%s""", (user_id,))
        if not profile:
            return jsonify({"error": "User not found"}), 404
        transactions = fetch_all("""SELECT merchant_name,amount_foreign,foreign_currency,category
          FROM transactions WHERE user_id=%s ORDER BY transaction_date DESC""", (user_id,))
        return jsonify({"answer": answer_question(str(data.get("question", "")), profile, transactions)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.get("/<path:filename>")
def frontend_files(filename):
    # Keep API routes above this catch-all. This serves the complete frontend
    # from the same origin as the Flask API, which is required for Railway.
    return _frontend_file(filename)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
