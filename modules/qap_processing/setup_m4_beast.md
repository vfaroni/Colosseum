# LIHTC Definition Intelligence System - M4 Beast Setup

## System Requirements ✅
- **Apple M4 Beast**: 128GB unified memory (Perfect!)
- **Storage**: ~20GB for models + data
- **Python**: 3.9+ (already installed)

## Quick Setup (5 minutes)

### 1. Install Dependencies
```bash
cd /Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill\ Rice/Colosseum/modules/qap_processing
pip3 install -r requirements_m4_beast.txt
```

### 2. Test ChromaDB + Search (No Model Download)
```bash
python3 lihtc_definition_intelligence_system.py
```
This will:
- ✅ Load all 2,159 definitions from 54 jurisdictions
- ✅ Initialize ChromaDB with vector search
- ✅ Launch Gradio interface on http://localhost:7860
- ⚠️ LLAMA model features disabled (search-only mode)

## Full Setup with LLAMA 34B (Optional)

### 3. Download LLAMA 34B Model (Recommended)
```bash
# Option 1: Hugging Face (recommended)
wget https://huggingface.co/TheBloke/Llama-2-34B-Chat-GGUF/resolve/main/llama-2-34b-chat.q4_K_M.gguf

# Option 2: Alternative quantized version (faster)
wget https://huggingface.co/TheBloke/Llama-2-34B-Chat-GGUF/resolve/main/llama-2-34b-chat.q5_K_M.gguf
```

### 4. Update Model Path
Edit `lihtc_definition_intelligence_system.py` line ~X:
```python
# Update this path to your downloaded model
model_path = "/path/to/llama-2-34b-chat.q4_K_M.gguf"
```

### 5. Launch Full System
```bash
python3 lihtc_definition_intelligence_system.py
```

## M4 Beast Performance Optimization

### Memory Configuration
- **ChromaDB**: ~2GB for 2,159 definitions
- **LLAMA 34B**: ~25GB (Q4 quantization)
- **Available**: ~100GB remaining for processing
- **Result**: Plenty of headroom for fast performance

### CPU Configuration
- **ChromaDB queries**: 2-4 cores
- **LLAMA inference**: 6-8 cores  
- **Background**: 2-4 cores
- **Result**: Optimal utilization of M4 Beast cores

## Expected Performance

### Search Performance
- **Definition search**: <100ms for 2,159 definitions
- **Vector similarity**: <200ms with metadata filters
- **Jurisdiction filtering**: <50ms

### LLAMA 34B Performance (M4 Beast)
- **First token**: ~2-3 seconds
- **Subsequent tokens**: ~100-150 tokens/second
- **Context window**: 8,192 tokens (perfect for LIHTC definitions)

## Test Queries to Try

1. **Basic Definition Search:**
   - "What is qualified basis?"
   - "Define AMI limits"
   - "Compliance period requirements"

2. **Cross-Jurisdictional:**
   - "How do different states define difficult development areas?"
   - "Which jurisdictions have the most definitions?"
   
3. **LIHTC Relevance:**
   - Filter by "Critical" relevance
   - Compare "High" vs "Medium" relevance definitions

4. **Complex Analysis (with LLAMA):**
   - "Compare Texas vs California approach to tax credit allocation"
   - "What are the common themes in QCT definitions across states?"

## System Architecture

```
M4 Beast (128GB) Architecture:
├── ChromaDB Vector Store (2,159 definitions)
│   ├── Semantic search with embeddings
│   ├── Metadata filtering (jurisdiction, relevance)
│   └── Cross-reference intelligence
├── LLAMA 34B Model (Optional)
│   ├── Context-aware analysis
│   ├── Cross-jurisdictional comparison
│   └── LIHTC expertise simulation
└── Gradio Web Interface
    ├── Real-time search
    ├── Interactive filtering
    └── System monitoring
```

## Troubleshooting

### ChromaDB Issues
```bash
# Reset ChromaDB if needed
rm -rf lihtc_definitions_chromadb/
python3 lihtc_definition_intelligence_system.py
```

### LLAMA Model Issues
```bash
# Check model file
ls -la /path/to/your/model.gguf

# Test model loading
python3 -c "from llama_cpp import Llama; print('LLAMA available')"
```

### Memory Issues (Unlikely on M4 Beast)
```bash
# Monitor memory usage
python3 -c "import psutil; print(f'Available RAM: {psutil.virtual_memory().available / (1024**3):.1f}GB')"
```

## Next Steps After Setup

1. **Test basic search functionality**
2. **Validate all 54 jurisdictions loaded**
3. **Try complex cross-jurisdictional queries**
4. **Explore definition intelligence features**
5. **Consider API development for integration**

## Production Deployment Options

- **Local Gradio Interface**: Development & testing
- **FastAPI REST API**: Integration with other systems
- **Streamlit Dashboard**: Executive reporting
- **Jupyter Notebooks**: Advanced analysis

The M4 Beast is perfectly suited for this workload with room for expansion!