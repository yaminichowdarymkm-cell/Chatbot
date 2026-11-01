const categorySelect=document.getElementById("category");
const list=document.getElementById("faq-list");
async function loadCategories(){
 const cats=await fetch("/api/categories").then(r=>r.json());
 categorySelect.innerHTML=cats.map(c=>`<option value="${c.id}">${c.name}</option>`).join("");
}
async function loadStats(){
 const s=await fetch("/api/admin/stats").then(r=>r.json());
 document.getElementById("stat-total").textContent=s.faqs;
 document.getElementById("stat-verified").textContent=s.verified;
 document.getElementById("stat-chats").textContent=s.chats;
}
async function loadFaqs(){
 const rows=await fetch("/api/admin/faqs").then(r=>r.json());
 list.innerHTML="";
 rows.forEach(f=>{
  const item=document.createElement("div");item.className="faq-item";
  const info=document.createElement("div");
  const q=document.createElement("b");q.textContent=f.question;
  const p=document.createElement("p");p.textContent=`${f.category} · ${f.answer}`;
  const tag=document.createElement("span");tag.className="tag";tag.textContent=f.verified_status;
  info.append(q,p,tag);
  const del=document.createElement("button");del.className="delete-btn";del.textContent="Delete";
  del.onclick=async()=>{if(confirm("Delete this FAQ?")){await fetch(`/api/admin/faqs/${f.id}`,{method:"DELETE"});loadFaqs();loadStats();}};
  item.append(info,del);list.append(item);
 });
 if(!rows.length)list.textContent="No FAQs yet.";
}
document.getElementById("faq-form").addEventListener("submit",async e=>{
 e.preventDefault();
 const payload={category_id:categorySelect.value,question:document.getElementById("faq-question").value,answer:document.getElementById("faq-answer").value,verified_status:document.getElementById("faq-status").value};
 const r=await fetch("/api/admin/faqs",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
 const data=await r.json();
 document.getElementById("form-status").textContent=data.error||"FAQ added successfully.";
 if(r.ok){e.target.reset();loadCategories();loadFaqs();loadStats();}
});
loadCategories().then(()=>{loadFaqs();loadStats();});
