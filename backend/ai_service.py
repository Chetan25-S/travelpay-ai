def classify_category(merchant):
    m=merchant.lower()
    groups={
      "Food & Dining":["restaurant","cafe","food","pizza","hotel restaurant","thali","coffee","bakery"],
      "Hotel":["hotel","resort","stay","hostel","room"],
      "Transport":["uber","ola","taxi","cab","metro","bus","rapido","auto"],
      "Shopping":["mall","store","market","shopping","retail"],
      "Entertainment":["movie","cinema","park","museum","ticket"]
    }
    for cat,words in groups.items():
        if any(w in m for w in words): return cat
    return "Other"

def analyze_payment(merchant,amount_inr,amount_foreign,currency,current_spent,total_budget):
    category=classify_category(merchant)
    impact=round((amount_foreign/total_budget)*100,2) if total_budget else 0
    remaining=round(total_budget-current_spent-amount_foreign,2)
    if remaining<0:
        risk="HIGH"; recommendation="This payment would exceed your travel budget. Consider reducing or postponing it."
    elif impact>=15:
        risk="MEDIUM"; recommendation="This payment uses a significant part of your travel budget. Review it before proceeding."
    else:
        risk="LOW"; recommendation="This payment is within your current travel-budget limits."
    return {"category":category,"risk_level":risk,"budget_impact":impact,
            "remaining_after":remaining,"recommendation":recommendation,
            "explanation":f"AI classified this as {category}. It uses about {impact}% of your total travel budget."}

def answer_question(question,profile,transactions):
    q=question.lower(); total=float(profile["total_budget"]); spent=float(profile["spent_amount"])
    cur=profile["home_currency"]; remaining=total-spent
    if "food" in q or "dining" in q:
        x=sum(float(t["amount_foreign"]) for t in transactions if t.get("category")=="Food & Dining")
        return f"You have spent about {x:.2f} {cur} on Food & Dining."
    if "remaining" in q or "left" in q: return f"You have about {remaining:.2f} {cur} remaining."
    if "afford" in q or "budget" in q: return f"You spent {spent:.2f} {cur} of {total:.2f}. Remaining: {remaining:.2f} {cur}."
    if "spend" in q or "spent" in q: return f"Your current total spending is {spent:.2f} {cur}."
    if "expensive" in q or "price" in q:
        return "Use Smart Price Advisor with the city, item/service and offered INR price. It checks configured live price sources and does not invent a market price."
    return "I can help with your travel budget, spending, categories, remaining balance and price decisions."
