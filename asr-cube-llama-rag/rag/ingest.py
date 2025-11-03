# Tiny RAG ingester: builds a hashed BoW vector store from rag/docs/*.md
import os, json, math, re

root = os.path.dirname(__file__)
docs_dir = os.path.join(root, "docs")
store_path = os.path.join(root, "store", "index.json")

def tokenize(s):
    return re.sub(r"[^a-z0-9\s]"," ",s.lower()).split()

def hash_vec(text, dim=512):
    vec = [0.0]*dim
    for tok in tokenize(text):
        h = 2166136261
        for ch in tok:
            h ^= ord(ch)
            h = (h * 16777619) & 0xFFFFFFFF
        idx = abs(h) % dim
        vec[idx] += 1.0
    norm = math.sqrt(sum(v*v for v in vec)) or 1.0
    return [v/norm for v in vec]

def read_docs():
    docs = []
    for fn in os.listdir(docs_dir):
        if fn.lower().endswith((".md",".txt")):
            p = os.path.join(docs_dir, fn)
            with open(p,"r",encoding="utf-8",errors="ignore") as f:
                text = f.read()
            title = fn.rsplit(".",1)[0]
            docs.append({"id":fn,"title":title,"text":text,"vec":hash_vec(text)})
    return docs

def main():
    os.makedirs(os.path.dirname(store_path), exist_ok=True)
    docs = read_docs()
    with open(store_path,"w",encoding="utf-8") as f:
        json.dump(docs,f,indent=2)
    print(f"Wrote {len(docs)} docs → {store_path}")

if __name__ == "__main__":
    main()
