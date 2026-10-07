import os, requests
from dotenv import load_dotenv
load_dotenv()

FALLBACK_RATES={"USD":84.8,"EUR":98.5,"GBP":114.2,"AUD":55.2,"CAD":61.5,"JPY":0.57,"SGD":65.2}

def get_rate(currency):
    currency=currency.upper()
    if currency=="INR": return 1.0
    # Frankfurter uses ECB reference rates. We request INR -> target by using EUR as base.
    # The public endpoint may not support INR as a base consistently, so use EUR cross rates.
    try:
        r=requests.get("https://api.frankfurter.app/latest?from=EUR&to=INR,"+currency,timeout=5)
        r.raise_for_status()
        rates=r.json().get("rates",{})
        inr_per_eur=float(rates["INR"])
        if currency=="EUR": return inr_per_eur
        target_per_eur=float(rates[currency])
        return inr_per_eur/target_per_eur
    except Exception:
        if currency in FALLBACK_RATES: return FALLBACK_RATES[currency]
        raise ValueError(f"Unsupported currency: {currency}")

def inr_to_foreign(amount_inr,currency):
    return round(float(amount_inr)/get_rate(currency),2)
