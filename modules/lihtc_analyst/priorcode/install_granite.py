
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

print("🔥 Loading granite-3.1-8b-instruct from Hugging Face...")

# Set cache directory
cache_dir = os.path.expanduser("~/.cache/huggingface/transformers")
os.makedirs(cache_dir, exist_ok=True)

try:
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        "ibm-granite/granite-3.1-8b-instruct",
        cache_dir=cache_dir
    )
    
    # Load model with appropriate precision for M4 Beast
    model = AutoModelForCausalLM.from_pretrained(
        "ibm-granite/granite-3.1-8b-instruct",
        torch_dtype=torch.float16,  # Use half precision for memory efficiency
        device_map="auto",  # Auto-assign to available devices
        cache_dir=cache_dir
    )
    
    print("✅ Model loaded successfully!")
    print(f"Model device: {model.device}")
    print(f"Model dtype: {model.dtype}")
    
    # Save model info
    model_info = {
        "model_name": "granite-3.1-8b-instruct",
        "huggingface_id": "ibm-granite/granite-3.1-8b-instruct",
        "loaded": True,
        "device": str(model.device),
        "memory_footprint": "16GB"
    }
    
    with open("granite_model_info.json", "w") as f:
        import json
        json.dump(model_info, f, indent=2)
    
    print("💾 Model info saved to granite_model_info.json")
    
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    exit(1)
