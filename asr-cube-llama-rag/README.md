# Llama RAG — Local Chat Provider for ASR Cube

Date: 2025-11-02

This is a minimal Retrieval‑Augmented “oracle chat” you can run locally **without cloud AI**.
If you have **Ollama** (or llama.cpp) running a model like `llama3.1:8b`, the server will proxy to it;
otherwise it will fall back to a **templated oracle** that uses your three voices.

## What you get
- `server/index.ts` — Express server exposing `/chat` and `/embed`
- `client/provider.llama.ts` — Implements the `LLMProvider` interface you asked for
- `prompts/` — System + voice templates (You could do this, I wonder,, What if)
- `rag/` — Tiny vector store (hashed BoW + cosine) with `ingest.py` to add docs
- `rag/docs/` — Sample docs (you can drop more `.md`/`.txt` here)
- Works offline; when Ollama is available it improves phrasing, but **logic stays local**.

## Quick start
1. Install Node 18+ and Python 3.10+
2. `cd server && npm init -y && npm i express cors node-fetch@2`
3. `npm i -D typescript ts-node @types/node @types/express`
4. `npx tsc --init`  (accept defaults)
5. `npx ts-node index.ts`
6. Optional: run **Ollama** with `ollama run llama3.1:8b` (default host http://localhost:11434)

The server listens on `http://localhost:3080`:
- `POST /chat` → RAG‑augmented chat (falls back to templated oracle if no model)
- `POST /embed` → simple hashed embedding for local store (debug)

## Client wiring
Import `client/provider.llama.ts` in your app and register it as the current provider.
It matches your `LLMProvider` shape:

```ts
interface LLMProvider { name: string; chat(ctx: ChatContext, msgs: ChatMessage[]): Promise<ChatMessage[]>; }
```

## RAG
- `rag/ingest.py` builds a tiny vector store from `rag/docs/*.md` to `rag/store/index.json`
- Retrieval uses cosine on hashed bag-of-words; no external models required.
- You can swap this for real embeddings later; API shape remains the same.
