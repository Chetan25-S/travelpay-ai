const form=document.getElementById("priceForm"),result=document.getElementById("priceResult");
async function status(){try{const s=await api("/price-status");document.getElementById("providerStatus").innerHTML=s.mode==="live"?'<span class="live-dot">● LIVE SOURCES CONFIGURED</span>':'<span class="warn-dot">● NO LIVE PRICE PROVIDER</span>'; }catch{}}
form.addEventListener("submit",async e=>{
 e.preventDefault(); result.classList.remove("hidden"); result.innerHTML="<p>🔎 Searching current price evidence...</p>";
 try{
  const d=await api("/price-advisor",{method:"POST",body:JSON.stringify({city:city.value,item:item.value,offered_price:Number(offered.value)})});
  if(!d.found){result.innerHTML=`<p class="eyebrow">LIVE PRICE INTELLIGENCE</p><h2>⚠️ Not enough verified data</h2><p>${escapeHtml(d.message)}</p><div class="insight">Sources checked: ${d.source_count||0} · Real places found: ${d.places_found||0}<br><small>${escapeHtml(d.checked_at||"")}</small></div>`;return;}
  const sources=(d.sources||[]).filter(x=>x.url).slice(0,6).map(x=>`<li><a href="${escapeHtml(x.url)}" target="_blank" rel="noopener">${escapeHtml(x.name)}</a></li>`).join("");
  result.innerHTML=`<p class="eyebrow">LIVE PRICE INTELLIGENCE</p><h2>${d.emoji} ${escapeHtml(d.assessment)}</h2>
   <div class="price-score"><strong>${d.fairness_score}/100</strong><span>Price Fairness</span></div>
   <div class="row"><span>City / Item</span><b>${escapeHtml(d.city)} · ${escapeHtml(d.item)}</b></div>
   <div class="row"><span>Your offered price</span><b>₹${Number(d.offered_price).toLocaleString("en-IN")}</b></div>
   <div class="row"><span>Observed range</span><b>₹${Number(d.min_price).toLocaleString("en-IN")} – ₹${Number(d.max_price).toLocaleString("en-IN")}</b></div>
   <div class="row"><span>Observed median</span><b>₹${Number(d.average_price).toLocaleString("en-IN")}</b></div>
   <div class="row"><span>Evidence</span><b>${d.observations} prices · ${d.source_count} sources</b></div>
   <div class="insight">🤖 <b>${escapeHtml(d.comparison)}</b><br>${escapeHtml(d.note)}</div>
   ${sources?`<h3>Sources</h3><ul>${sources}</ul>`:""}`;
 }catch(e){result.innerHTML=`<p>${escapeHtml(e.message)}</p>`;}
});
status();