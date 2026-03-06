function toggleChat(){

let box=document.getElementById("chat-box");

if(box.style.display==="flex"){
box.style.display="none";
}else{
box.style.display="flex";
}

}

function quickAction(type){

if(type==="jobs"){
window.location="/jobs";
}

if(type==="tools"){
window.location="/tools";
}

if(type==="workers"){
window.location="/employer/dashboard";
}

}

function sendChat(){

let input=document.getElementById("chatInput");
let msg=input.value.trim();

if(msg==="") return;

let chat=document.getElementById("chat-messages");

chat.innerHTML+=`<div><b>You:</b> ${msg}</div>`;

fetch("/chatbot",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({message:msg})
})
.then(res=>res.json())
.then(data=>{
chat.innerHTML+=`<div class="bot-msg">${data.reply}</div>`;
chat.scrollTop=chat.scrollHeight;
});

input.value="";
}