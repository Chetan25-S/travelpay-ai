document.getElementById("profileForm").addEventListener("submit",async e=>{
 e.preventDefault(); const msg=document.getElementById("setupMessage"); msg.textContent="Creating traveler profile...";
 try{const d=await api("/profile",{method:"POST",body:JSON.stringify({
 name:name.value,country:country.value,home_currency:currency.value,total_budget:Number(budget.value)
 })}); setUserId(d.user_id); msg.textContent="Profile created. Opening dashboard..."; setTimeout(()=>location.href="dashboard.html",500);}
 catch(err){msg.textContent=err.message;}
});