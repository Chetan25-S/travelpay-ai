const chat=document.getElementById("chat"),form=document.getElementById("chatForm"),input=document.getElementById("question"),voiceBtn=document.getElementById("voiceBtn"),voiceStatus=document.getElementById("voiceStatus");
let recognition=null,listening=false;
function addMessage(t,c){const d=document.createElement("div");d.className=`message ${c}`;d.textContent=t;chat.appendChild(d);chat.scrollTop=chat.scrollHeight;}
function speak(t){if("speechSynthesis"in window){speechSynthesis.cancel();speechSynthesis.speak(new SpeechSynthesisUtterance(t));}}
async function ask(q){if(!q)return;addMessage(q,"user");try{const d=await api("/assistant",{method:"POST",body:JSON.stringify({user_id:Number(getUserId()),question:q})});addMessage(d.answer,"bot");speak(d.answer);}catch(e){addMessage(e.message,"bot");}}
form.addEventListener("submit",e=>{e.preventDefault();const q=input.value.trim();input.value="";ask(q);});
document.querySelectorAll(".chip").forEach(b=>b.onclick=()=>{input.value=b.textContent;form.requestSubmit();});
if("SpeechRecognition"in window||"webkitSpeechRecognition"in window){
 const SR=window.SpeechRecognition||window.webkitSpeechRecognition; recognition=new SR(); recognition.lang="en-IN"; recognition.interimResults=false;
 recognition.onstart=()=>{listening=true;voiceBtn.textContent="🛑 Stop Listening";voiceStatus.textContent="Listening...";};
 recognition.onresult=e=>{input.value=e.results[0][0].transcript;ask(input.value);};
 recognition.onerror=()=>voiceStatus.textContent="Voice input failed. Try again.";
 recognition.onend=()=>{listening=false;voiceBtn.textContent="🎤 Start Voice";};
 voiceBtn.onclick=()=>listening?recognition.stop():recognition.start();
}else{voiceBtn.disabled=true;voiceStatus.textContent="Use Chrome/Edge for voice input.";}
