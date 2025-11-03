import express from "express";
import cors from "cors";
import fetch from "node-fetch";
import fs from "fs";
import path from "path";

const app = express();
app.use(cors());
app.use(express.json({ limit: "10mb" }));

const OLLAMA_URL = process.env.OLLAMA_URL || "http://localhost:11434";
const MODEL = process.env.LLAMA_MODEL || "llama3.1:8b";

// ---- tiny RAG ----
type Doc = { id: string; title: string; text: string; vec: number[] };
const STORE = path.join(__dirname, "../rag/store/index.json");

function loadStore(): Doc[] {
  try { return JSON.parse(fs.readFileSync(STORE, "utf-8")); } catch { return []; }
}

function tokenize(s: string): string[] {
  return (s.toLowerCase().replace(/[^a-z0-9\s]/g," ").split(/\s+/).filter(Boolean));
}

function hashVec(s: string, dim: number = 512): number[] {
  const vec = new Array(dim).fill(0);
  for (const tok of tokenize(s)) {
    let h = 2166136261;
    for (let i=0;i<tok.length;i++){ h ^= tok.charCodeAt(i); h = Math.imul(h,16777619); }
    const idx = Math.abs(h) % dim;
    vec[idx] += 1;
  }
  // l2 normalize
  const norm = Math.sqrt(vec.reduce((a,b)=>a+b*b,0)) || 1;
  return vec.map(v=>v/norm);
}

function cosine(a:number[], b:number[]): number {
  let s=0;
  for (let i=0;i<Math.min(a.length,b.length);i++) s += a[i]*b[i];
  return s;
}

function retrieve(query: string, k: number = 5){
  const docs = loadStore();
  const qv = hashVec(query);
  return docs
    .map(d => ({...d, score: cosine(qv, d.vec)}))
    .sort((a,b)=>b.score-a.score)
    .slice(0,k);
}

// ---- oracle templates ----
const systemPrompt = fs.readFileSync(path.join(__dirname,"../prompts/system.txt"),"utf-8");
const tplDo = fs.readFileSync(path.join(__dirname,"../prompts/voice_do.txt"),"utf-8");
const tplAsk = fs.readFileSync(path.join(__dirname,"../prompts/voice_ask.txt"),"utf-8");
const tplWhatIf = fs.readFileSync(path.join(__dirname,"../prompts/voice_whatif.txt"),"utf-8");

function buildPrompt(ctx:any, msgs:any[], retrieved: any[]){
  const voice = ctx?.preferences?.voice || "do";
  const tpl = voice==="do" ? tplDo : voice==="ask" ? tplAsk : tplWhatIf;
  const context = retrieved.map(r=>`[${r.title}] ${r.text.substring(0,500)}`).join("\n---\n");
  const last = msgs[msgs.length-1]?.content || "";
  return `${systemPrompt}\n\n[CONTEXT]\n${context}\n\n[VOICE]\n${tpl}\n\n[USER]\n${last}`;
}

async function callOllama(prompt: string){
  try {
    const r = await fetch(`${OLLAMA_URL}/api/generate`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ model: MODEL, prompt })
    });
    if (!r.ok) throw new Error("ollama error");
    const text = await r.text();
    const lines = text.trim().split(/\r?\n/);
    const body = lines.map(l=>{ try { return JSON.parse(l).response || "" } catch { return "" } }).join("");
    return body || text;
  } catch(e){
    return null;
  }
}

// fallback oracle (no model)
function fallbackOracle(ctx:any, retrieved:any[], userLast:string){
  const voice = ctx?.preferences?.voice || "do";
  const items = [
    {title:"Try the smallest complete version", how:"Pick one tile. Do one precise step. Stop."},
    {title:"Crown one thing", how:"Choose the star. Everything else supports it."},
    {title:"Reverse the view", how:"Describe the same tile from its opposite role."},
    {title:"Distill to one line", how:"Say the whole idea in 12 words. Act accordingly."},
    {title:"Multiply softly", how:"Repeat one element 3 times with tiny variation."}
  ];
  if (voice==="ask"){
    return items.map(i=>`which ${i.title.lower ? i.title.toLowerCase() : i.title}?`).join("\n");
  }
  if (voice==="whatif"){
    return items.map(i=>`What if ${i.title.toLowerCase()}?`).join("\n");
  }
  // "do"
  return items.map(i=>`- **${i.title}** — ${i.how}`).join("\n");
}

app.post("/chat", async (req,res)=>{
  const { ctx, msgs } = req.body || {};
  const userLast = msgs?.[msgs.length-1]?.content || "";
  const retrieved = retrieve(userLast, 5);
  const prompt = buildPrompt(ctx || {}, msgs || [], retrieved);
  const out = await callOllama(prompt);
  if (out){
    res.json({ role:"assistant", content: out, retrieved });
  } else {
    res.json({ role:"assistant", content: fallbackOracle(ctx, retrieved, userLast), retrieved });
  }
});

app.post("/embed", async (req,res)=>{
  const { text } = req.body || {};
  const vec = hashVec(text || "");
  res.json({ vec });
});

app.listen(3080, ()=>console.log("Llama RAG server on http://localhost:3080"));
