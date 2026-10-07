let scanner=null,scanning=false;
function parseUpi(text){
 try{const u=new URL(text);if(u.protocol.toLowerCase()!=="upi:")return false;const p=u.searchParams;
  if(p.get("pa"))upi.value=p.get("pa"); if(p.get("pn"))merchant.value=p.get("pn"); if(p.get("am"))amount.value=p.get("am");
  scanStatus.textContent="QR decoded. Review the details.";return true;
 }catch{return false;}
}
async function startScanner(){if(scanning)return;scanner=new Html5Qrcode("reader");
 try{await scanner.start({facingMode:"environment"},{fps:10,qrbox:{width:250,height:250}},t=>{if(parseUpi(t))stopScanner();},()=>{});scanning=true;scanStatus.textContent="Scanning...";}catch{scanStatus.textContent="Camera unavailable. Use manual entry.";}}
async function stopScanner(){if(scanner&&scanning){try{await scanner.stop();await scanner.clear();}catch{}scanning=false;}}
startCamera.onclick=startScanner;stopCamera.onclick=stopScanner;
paymentForm.addEventListener("submit",async e=>{e.preventDefault();result.classList.remove("hidden");result.innerHTML="<p>🤖 Analyzing payment + live price evidence...</p>";
 try{const payload={user_id:Number(getUserId()),merchant:merchant.value,upi_id:upi.value,amount_inr:Number(amount.value),city:city.value,item:item.value};
  const d=await api("/analyze-payment",{method:"POST",body:JSON.stringify(payload)});sessionStorage.setItem("pendingPayment",JSON.stringify({...d,upi_id:upi.value,city:city.value,item:item.value}));
  const pc=d.price_check;
  result.innerHTML=`<p class="eyebrow">AI PAYMENT INSIGHT</p><h2>₹${Number(d.amount_inr).toLocaleString("en-IN")} ≈ ${d.amount_foreign} ${d.currency}</h2>
  <div class="row"><span>Merchant</span><b>${escapeHtml(d.merchant)}</b></div><div class="row"><span>Category</span><b>${escapeHtml(d.category)}</b></div>
  <div class="row"><span>Budget impact</span><b>${d.budget_impact}%</b></div><div class="row"><span>AI Risk</span><b class="risk-${d.risk_level.toLowerCase()}">${d.risk_level}</b></div>
  ${pc&&pc.found?`<div class="price-mini"><b>${pc.emoji} ${escapeHtml(pc.assessment)}</b><br>Observed median ₹${Number(pc.average_price).toLocaleString("en-IN")} · ${pc.observations} prices from ${pc.source_count} sources</div>`:pc?`<div class="price-mini">⚠️ ${escapeHtml(pc.message)}</div>`:""}
  <div class="insight">🤖 ${escapeHtml(d.explanation)}<br><br><b>${escapeHtml(d.recommendation)}</b></div><a class="btn full" href="payment.html">Continue to Payment Review</a>`;
 }catch(e){result.innerHTML=`<p>${escapeHtml(e.message)}</p>`;}
});