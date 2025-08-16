#!/usr/bin/env python3
"""
LIHTC Fine-Tuned LLM Inference Interface
Professional interface for LIHTC Q&A with RAG integration
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import json
import chromadb
from pathlib import Path
from typing import List, Dict, Optional

class LIHTCInferenceEngine:
    """Professional LIHTC Q&A system with fine-tuned LLM + RAG"""
    
    def __init__(self, model_path: str, chromadb_path: str = "./lihtc_definitions_chromadb"):
        self.model_path = model_path
        self.chromadb_path = chromadb_path
        
        # Load fine-tuned model
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"
        )
        
        # Load ChromaDB for RAG
        self.chroma_client = chromadb.PersistentClient(path=chromadb_path)
        self.collection = self.chroma_client.get_collection("lihtc_definitions")
        
        print("✅ LIHTC Inference Engine Ready")
        print(f"Model: {model_path}")
        print(f"ChromaDB: {chromadb_path}")
    
    def retrieve_context(self, query: str, n_results: int = 5) -> List[Dict]:
        """Retrieve relevant context from RAG system"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas"]
        )
        
        context_items = []
        for i, doc in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][i]
            context_items.append({
                "content": doc,
                "jurisdiction": metadata.get("jurisdiction", "Unknown"),
                "source": metadata.get("source", "QAP"),
                "relevance_score": 1.0 - (i / n_results)  # Simple relevance scoring
            })
        
        return context_items
    
    def generate_response(self, query: str, context: Optional[List[Dict]] = None, max_length: int = 1024) -> str:
        """Generate response using fine-tuned model with context"""
        
        # Prepare context if provided
        context_text = ""
        if context:
            context_text = "\n\nRelevant LIHTC Information:\n"
            for item in context[:3]:  # Use top 3 results
                context_text += f"- {item['jurisdiction']}: {item['content'][:200]}...\n"
        
        # Format prompt
        prompt = f"""### Instruction:
Answer this LIHTC (Low-Income Housing Tax Credit) question based on your specialized knowledge and the provided context. Be specific, accurate, and cite relevant jurisdictions when applicable.

Question: {query}{context_text}

### Response:"""
        
        # Tokenize and generate
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1800)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_length,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = response.split("### Response:")[-1].strip()
        
        return response
    
    def lihtc_qa(self, question: str) -> Dict:
        """Complete LIHTC Q&A with RAG integration"""
        print(f"🔍 Processing: {question}")
        
        # Retrieve context
        context = self.retrieve_context(question)
        
        # Generate response
        response = self.generate_response(question, context)
        
        return {
            "question": question,
            "response": response,
            "context_sources": [
                {"jurisdiction": item["jurisdiction"], "relevance": item["relevance_score"]}
                for item in context[:3]
            ],
            "context_count": len(context)
        }

def main():
    """Interactive LIHTC Q&A session"""
    engine = LIHTCInferenceEngine("./lihtc_finetuned_model")
    
    print("🏢 LIHTC Expert Assistant Ready!")
    print("Ask questions about Low-Income Housing Tax Credits, QAPs, and compliance requirements.")
    print("Type 'quit' to exit.\n")
    
    while True:
        question = input("❓ Your LIHTC Question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not question:
            continue
        
        try:
            result = engine.lihtc_qa(question)
            print(f"\n💡 Response:")
            print(result["response"])
            print(f"\n📚 Sources: {len(result['context_sources'])} jurisdictions referenced")
            print("-" * 80 + "\n")
            
        except Exception as e:
            print(f"❌ Error: {e}\n")

if __name__ == "__main__":
    main()
