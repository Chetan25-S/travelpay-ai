let chart;
function money(v,c){try{return new Intl.NumberFormat("en-US",{style:"currency",currency:c}).format(Number(v));}catch{return `${Number(v).toFixed(2)} ${c}`;}}
async function loadDashboard(){
 try{
  const d=await api(`/dashboard/${getUserId()}`),p=d.profile;
  hello.textContent=`Hello ${p.name} 👋`; budget.textContent=money(p.total_budget,p.home_currency);
  spent.textContent=money(p.spent_amount,p.home_currency); remaining.textContent=money(p.remaining_amount,p.home_currency); count.textContent=d.transactions.length;
  transactions.innerHTML=d.transactions.map(t=>`<tr><td>${escapeHtml(t.merchant_name)}</td><td>${escapeHtml(t.category)}</td><td>₹${Number(t.amount_inr).toLocaleString("en-IN")}</td><td>${money(t.amount_foreign,t.foreign_currency)}</td><td class="risk-${String(t.risk_level).toLowerCase()}">${escapeHtml(t.risk_level)}</td><td>${escapeHtml(t.status)}</td></tr>`).join("")||'<tr><td colspan="6">No transactions yet.</td></tr>';
  const totals={}; d.transactions.forEach(t=>totals[t.category]=(totals[t.category]||0)+Number(t.amount_foreign));
  if(chart)chart.destroy(); chart=new Chart(document.getElementById("categoryChart"),{type:"doughnut",data:{labels:Object.keys(totals),datasets:[{data:Object.values(totals)}]},options:{responsive:true,plugins:{legend:{position:"bottom"}}}});
  const pct=p.total_budget?(Number(p.spent_amount)/Number(p.total_budget))*100:0;
  aiInsight.innerHTML=pct>=75?`⚠️ You have used <b>${pct.toFixed(1)}%</b> of your travel budget.`:`✅ You have used <b>${pct.toFixed(1)}%</b> of your travel budget.`;
 }catch(e){aiInsight.textContent=e.message;}
}
loadDashboard();