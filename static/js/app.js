const form=document.getElementById("chat-form");
const input=document.getElementById("question");
const messages=document.getElementById("messages");
function addMessage(text,who,notice){
  const el=document.createElement("div");el.className=`message ${who}`;
  if(who==="bot"){const sender=document.createElement("span");sender.className="sender";sender.textContent="RISE AI";el.appendChild(sender);}
  const body=document.createElement("div");body.textContent=text;el.appendChild(body);
  if(notice){const n=document.createElement("div");n.className="notice";n.textContent=notice;el.appendChild(n);}
  messages.appendChild(el);messages.scrollTop=messages.scrollHeight;
}
async function ask(question){
  addMessage(question,"user");
  input.value="";input.disabled=true;
  try{
    const response=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({question})});
    const data=await response.json();
    addMessage(data.answer,"bot",data.notice);
  }catch(e){addMessage("The server could not be reached. Check that the Flask application is running.","bot");}
  finally{input.disabled=false;input.focus();}
}
form.addEventListener("submit",e=>{e.preventDefault();const q=input.value.trim();if(q)ask(q);});
document.querySelectorAll(".suggestions button").forEach(b=>b.addEventListener("click",()=>ask(b.dataset.question)));
