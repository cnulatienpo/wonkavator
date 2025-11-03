// client/provider.llama.ts
// Minimal provider wired to the Llama RAG server (or fallback oracle)

export interface ChatMessage { role: "system"|"user"|"assistant"; content: string; }
export interface ChatContext {
  boardSummary: string;
  tiles: any[];
  lockedIds: string[];
  preferences: { voice: "do"|"ask"|"whatif"; spice: 1|2|3 };
}

export interface LLMProvider {
  name: string;
  chat(ctx: ChatContext, msgs: ChatMessage[]): Promise<ChatMessage[]>;
}

export class LlamaRagProvider implements LLMProvider {
  name = "llama-rag";
  constructor(private baseUrl = "http://localhost:3080"){}
  async chat(ctx: ChatContext, msgs: ChatMessage[]): Promise<ChatMessage[]> {
    const r = await fetch(`${this.baseUrl}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ctx, msgs })
    });
    const data = await r.json();
    return [{ role: "assistant", content: data.content }];
  }
}
