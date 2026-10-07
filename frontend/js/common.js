const API="/api";
const USER_KEY="travelpay_user_id";
function getUserId(){return localStorage.getItem(USER_KEY)||"1";}
const AUTH_KEY="travelpay_demo_auth";
function isAuthenticated(){return sessionStorage.getItem(AUTH_KEY)==="true";}
function requireAuth(){if(!isAuthenticated()) location.replace("login.html");}
function logout(){sessionStorage.removeItem(AUTH_KEY); localStorage.removeItem(USER_KEY); location.replace("login.html");}
function setUserId(id){localStorage.setItem(USER_KEY,id);}
function escapeHtml(v){return String(v??"").replace(/[&<>\'"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\'":"&#39;",'"':"&quot;"}[c]));}
async function api(path,options={}){
 const res=await fetch(API+path,{headers:{"Content-Type":"application/json",...(options.headers||{})},...options});
 let data={}; try{data=await res.json();}catch{}
 if(!res.ok)throw new Error(data.error||"Request failed");
 return data;
}
