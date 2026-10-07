import os, re, statistics, requests
from datetime import datetime, timezone
from dotenv import load_dotenv
load_dotenv()

def provider_status():
    return {
      "google_places_configured": bool(os.getenv("GOOGLE_PLACES_API_KEY")),
      "serper_configured": bool(os.getenv("SERPER_API_KEY")),
      "mode": "live" if (os.getenv("GOOGLE_PLACES_API_KEY") or os.getenv("SERPER_API_KEY")) else "no-live-provider",
      "message":"Live evidence enabled." if (os.getenv("GOOGLE_PLACES_API_KEY") or os.getenv("SERPER_API_KEY")) else "Add a provider API key to enable live price evidence. No demo prices are used."
    }

def _headers():
    return {"X-API-KEY":os.getenv("SERPER_API_KEY",""),"Content-Type":"application/json"}

def _money_numbers(text):
    # Finds INR-like values: ₹1,200 / Rs 1200 / INR 1200
    nums=[]
    for m in re.finditer(r'(?:₹|rs\.?|inr)\s*([0-9]{2,6}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?)',text.lower()):
        try: nums.append(float(m.group(1).replace(",","")))
        except: pass
    return nums

def serper_search(city,item):
    key=os.getenv("SERPER_API_KEY")
    if not key: return []
    queries=[
      f"{item} price {city} India",
      f"{item} menu price {city} India",
      f"{item} cost {city} India"
    ]
    out=[]
    for q in queries:
        try:
            r=requests.post("https://google.serper.dev/search",headers=_headers(),
                             json={"q":q,"num":10},timeout=8)
            r.raise_for_status()
            data=r.json()
            for x in data.get("organic",[]):
                snippet=(x.get("title","")+" "+x.get("snippet",""))
                prices=_money_numbers(snippet)
                if prices:
                    out.append({"title":x.get("title",""),"url":x.get("link",""),"snippet":x.get("snippet",""),"prices":prices})
        except Exception:
            continue
    return out

def google_places(city,item):
    key=os.getenv("GOOGLE_PLACES_API_KEY")
    if not key: return []
    url="https://places.googleapis.com/v1/places:searchText"
    headers={"X-Goog-Api-Key":key,"X-Goog-FieldMask":"places.displayName,places.formattedAddress,places.googleMapsUri,places.priceLevel,places.websiteUri"}
    try:
        r=requests.post(url,headers=headers,json={"textQuery":f"{item} in {city}, India","pageSize":10},timeout=8)
        r.raise_for_status()
        return r.json().get("places",[])
    except Exception:
        return []

def live_price_advisor(city,item,offered):
    city=city.strip(); item=item.strip(); offered=float(offered)
    serper=serper_search(city,item)
    values=[p for row in serper for p in row["prices"] if 20 <= p <= 100000]
    places=google_places(city,item)
    sources=[]
    for row in serper[:8]:
        sources.append({"name":row["title"],"url":row["url"],"type":"web price evidence"})
    for p in places[:8]:
        sources.append({"name":p.get("displayName",{}).get("text","Google Place"),
                         "url":p.get("websiteUri") or p.get("googleMapsUri",""),
                         "type":"real place","price_level":p.get("priceLevel")})
    if len(values)<2:
        return {
          "found":False,"mode":"live","city":city,"item":item,"offered_price":offered,
          "observed_prices":values,"source_count":len(sources),
          "places_found":len(places),"sources":sources[:10],
          "message":"Not enough verified exact price evidence was found for this item/service. TravelPay AI will not invent an average price.",
          "checked_at":datetime.now(timezone.utc).isoformat()
        }
    median=statistics.median(values)
    low=min(values); high=max(values)
    # Robust displayed range: use observed min/max, capped to avoid one extreme dominating.
    q1=statistics.quantiles(values,n=4,method="inclusive")[0] if len(values)>=4 else low
    q3=statistics.quantiles(values,n=4,method="inclusive")[2] if len(values)>=4 else high
    if offered <= q1: label,emoji,score="CHEAP / GOOD DEAL","🟢",95
    elif offered <= median*1.10: label,emoji,score="REASONABLE","🔵",82
    elif offered <= q3: label,emoji,score="ABOVE AVERAGE","🟠",55
    else: label,emoji,score="EXPENSIVE","🔴",25
    diff=offered-median
    comparison=(f"₹{abs(diff):,.0f} above the observed median." if diff>0
                else f"₹{abs(diff):,.0f} below the observed median." if diff<0
                else "Exactly at the observed median.")
    return {
      "found":True,"mode":"live","city":city,"item":item,"offered_price":offered,
      "min_price":round(low,2),"average_price":round(median,2),"max_price":round(high,2),
      "observed_prices":sorted(set(round(x,2) for x in values))[:30],
      "observations":len(values),"source_count":len(sources),"places_found":len(places),
      "fairness_score":score,"assessment":label,"emoji":emoji,"comparison":comparison,
      "note":"This estimate is derived from current search evidence. Prices can vary by merchant, quantity, quality, time and location. Google Places priceLevel is treated only as business context, not as an exact item price.",
      "sources":sources[:10],"checked_at":datetime.now(timezone.utc).isoformat()
    }
