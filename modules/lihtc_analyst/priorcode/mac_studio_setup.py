#!/usr/bin/env python3
"""
Mac Studio Development Environment Setup
Prepares Mac Studio for production RAG deployment with optimal configuration
"""

import os
import subprocess
import sys
from pathlib import Path
import json
from datetime import datetime

class MacStudioSetup:
    """Setup Mac Studio environment for production QAP RAG system"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG")
        self.data_dir = Path("/Users/williamrice/HERR Dropbox/Bill Rice/Data_Sets")
        self.mac_studio_dir = self.base_dir / "mac_studio_rag"
        self.mac_studio_dir.mkdir(exist_ok=True)
        
        # System specifications for Mac Studio optimization
        self.mac_specs = {
            "recommended_memory": "128GB",
            "minimum_memory": "64GB", 
            "storage": "2TB SSD",
            "processor": "M2 Ultra (24-core CPU, 76-core GPU)",
            "target_performance": "20-50 tokens/second local inference"
        }
        
        # Required packages for Mac Studio deployment
        self.required_packages = [
            "fastapi>=0.104.0",
            "uvicorn>=0.24.0",
            "chromadb>=0.4.15",
            "sentence-transformers>=2.2.2",
            "transformers>=4.35.0",
            "torch>=2.1.0",
            "pandas>=2.1.0",
            "numpy>=1.24.0",
            "pydantic>=2.4.0",
            "python-multipart>=0.0.6",
            "jinja2>=3.1.2",
            "aiofiles>=23.2.1",
            "python-jose[cryptography]>=3.3.0",
            "passlib[bcrypt]>=1.7.4",
            "redis>=5.0.0",
            "psycopg2-binary>=2.9.7",
            "sqlalchemy>=2.0.0",
            "alembic>=1.12.0"
        ]
        
        # Optional packages for local LLM support
        self.llm_packages = [
            "llama-cpp-python>=0.2.20",
            "bitsandbytes>=0.41.0",
            "accelerate>=0.24.0",
            "einops>=0.7.0",
            "xformers>=0.0.22"
        ]

    def check_system_requirements(self) -> dict:
        """Check Mac Studio system requirements and capabilities"""
        print("🔍 Checking Mac Studio system requirements...")
        
        system_info = {}
        
        try:
            # Check macOS version
            result = subprocess.run(['sw_vers'], capture_output=True, text=True)
            system_info['macos_version'] = result.stdout
            
            # Check available memory
            result = subprocess.run(['sysctl', 'hw.memsize'], capture_output=True, text=True)
            if result.returncode == 0:
                mem_bytes = int(result.stdout.split(':')[1].strip())
                mem_gb = mem_bytes / (1024**3)
                system_info['memory_gb'] = round(mem_gb, 1)
                
                if mem_gb >= 128:
                    print(f"  ✅ Memory: {mem_gb:.1f}GB (Excellent for large LLMs)")
                elif mem_gb >= 64:
                    print(f"  ⚠️  Memory: {mem_gb:.1f}GB (Good, recommend upgrade to 128GB)")
                else:
                    print(f"  ❌ Memory: {mem_gb:.1f}GB (Insufficient for local LLM inference)")
            
            # Check available storage
            result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    storage_info = lines[1].split()
                    system_info['storage_available'] = storage_info[3]
                    print(f"  ✅ Storage available: {storage_info[3]}")
            
            # Check Python version
            python_version = sys.version
            system_info['python_version'] = python_version
            print(f"  ✅ Python: {python_version.split()[0]}")
            
            # Check if this is an Apple Silicon Mac
            result = subprocess.run(['uname', '-m'], capture_output=True, text=True)
            if result.returncode == 0:
                arch = result.stdout.strip()
                system_info['architecture'] = arch
                if 'arm64' in arch:
                    print(f"  ✅ Architecture: {arch} (Apple Silicon - Optimal for local inference)")
                else:
                    print(f"  ⚠️  Architecture: {arch} (Intel - May have performance limitations)")
            
        except Exception as e:
            print(f"  ❌ Error checking system: {e}")
        
        return system_info

    def setup_python_environment(self):
        """Setup Python virtual environment with required packages"""
        print("\n🐍 Setting up Python environment...")
        
        venv_path = self.mac_studio_dir / "venv"
        
        # Create virtual environment if it doesn't exist
        if not venv_path.exists():
            print("  Creating virtual environment...")
            subprocess.run([sys.executable, '-m', 'venv', str(venv_path)])
            print(f"  ✅ Virtual environment created at {venv_path}")
        else:
            print(f"  ✅ Virtual environment exists at {venv_path}")
        
        # Create requirements.txt
        requirements_path = self.mac_studio_dir / "requirements.txt"
        with open(requirements_path, 'w') as f:
            for package in self.required_packages:
                f.write(f"{package}\n")
        
        # Create optional LLM requirements
        llm_requirements_path = self.mac_studio_dir / "requirements_llm.txt"
        with open(llm_requirements_path, 'w') as f:
            for package in self.llm_packages:
                f.write(f"{package}\n")
        
        print(f"  ✅ Requirements files created")
        print(f"     - Core: {requirements_path}")
        print(f"     - LLM:  {llm_requirements_path}")
        
        # Create activation script
        activate_script = self.mac_studio_dir / "activate_env.sh"
        with open(activate_script, 'w') as f:
            f.write(f"""#!/bin/bash
# Mac Studio RAG Environment Activation Script
echo "🚀 Activating Mac Studio RAG environment..."
source {venv_path}/bin/activate
echo "✅ Environment activated"
echo "📦 Installing/updating core packages..."
pip install --upgrade pip
pip install -r {requirements_path}
echo "🎯 Ready for development!"
echo ""
echo "Optional: Install LLM packages for local inference:"
echo "pip install -r {llm_requirements_path}"
""")
        
        # Make script executable
        os.chmod(activate_script, 0o755)
        print(f"  ✅ Activation script created: {activate_script}")

    def create_directory_structure(self):
        """Create optimal directory structure for Mac Studio deployment"""
        print("\n📁 Creating Mac Studio directory structure...")
        
        directories = [
            "backend",
            "frontend", 
            "docker",
            "config",
            "logs",
            "data/cache",
            "data/models",
            "data/exports",
            "scripts",
            "tests",
            "docs"
        ]
        
        for dir_name in directories:
            dir_path = self.mac_studio_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Created: {dir_path}")

    def create_configuration_files(self):
        """Create configuration files optimized for Mac Studio"""
        print("\n⚙️  Creating configuration files...")
        
        # Main configuration
        config = {
            "environment": "mac_studio_production",
            "data_sources": {
                "qap_base_path": str(self.data_dir / "QAP" / "_processed"),
                "federal_base_path": str(self.data_dir / "federal" / "LIHTC_Federal_Sources" / "_processed"),
                "cache_path": str(self.mac_studio_dir / "data" / "cache"),
                "export_path": str(self.mac_studio_dir / "data" / "exports")
            },
            "vector_database": {
                "type": "chroma",
                "path": str(self.mac_studio_dir / "data" / "chroma_db"),
                "collection_name": "qap_lihtc_unified",
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "similarity_threshold": 0.7,
                "max_results": 100
            },
            "local_llm": {
                "enabled": True,
                "model_path": str(self.mac_studio_dir / "data" / "models"),
                "recommended_model": "llama-2-70b-chat.ggmlv3.q4_0.bin",
                "context_length": 4096,
                "temperature": 0.1,
                "max_tokens": 512
            },
            "api_settings": {
                "host": "127.0.0.1",
                "port": 8000,
                "workers": 4,
                "cors_origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
                "rate_limit": "100/minute"
            },
            "search_settings": {
                "default_limit": 20,
                "max_limit": 100,
                "enable_federal_state_integration": True,
                "authority_hierarchy_scoring": True,
                "cross_state_comparison": True
            },
            "performance": {
                "embedding_batch_size": 32,
                "vector_search_threads": 8,
                "cache_ttl_seconds": 3600,
                "max_concurrent_requests": 50
            },
            "mac_studio_optimizations": {
                "use_metal_performance_shaders": True,
                "optimize_for_m2_ultra": True,
                "memory_mapping": True,
                "gpu_acceleration": True
            }
        }
        
        config_path = self.mac_studio_dir / "config" / "mac_studio_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"  ✅ Main configuration: {config_path}")
        
        # Docker configuration for optional containerization
        docker_compose = """version: '3.8'

services:
  rag_backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile.mac_studio
    ports:
      - "8000:8000"
    volumes:
      - ../data:/app/data
      - ../config:/app/config
      - ../logs:/app/logs
    environment:
      - ENVIRONMENT=mac_studio_production
      - CONFIG_PATH=/app/config/mac_studio_config.json
    restart: unless-stopped
    
  rag_frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - rag_backend
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    restart: unless-stopped
    
  redis_cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    
volumes:
  redis_data:
"""
        
        docker_path = self.mac_studio_dir / "docker" / "docker-compose.yml"
        with open(docker_path, 'w') as f:
            f.write(docker_compose)
        print(f"  ✅ Docker configuration: {docker_path}")

    def create_startup_scripts(self):
        """Create startup scripts for easy Mac Studio deployment"""
        print("\n🚀 Creating startup scripts...")
        
        # Development startup script
        dev_script = self.mac_studio_dir / "start_development.sh"
        with open(dev_script, 'w') as f:
            f.write(f"""#!/bin/bash
# Mac Studio RAG Development Startup Script

echo "🍎 Starting Mac Studio LIHTC RAG System (Development Mode)"
echo "============================================================"

# Activate environment
source {self.mac_studio_dir}/venv/bin/activate

# Start backend
echo "🔧 Starting FastAPI backend..."
cd {self.mac_studio_dir}/backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start frontend (if available)
if [ -d "{self.mac_studio_dir}/frontend" ]; then
    echo "🌐 Starting React frontend..."
    cd {self.mac_studio_dir}/frontend
    npm start &
    FRONTEND_PID=$!
fi

echo "✅ Mac Studio RAG System is running!"
echo "   - Backend:  http://localhost:8000"
echo "   - Frontend: http://localhost:3000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap 'echo "Stopping services..."; kill $BACKEND_PID $FRONTEND_PID; exit 0' INT
wait
""")
        os.chmod(dev_script, 0o755)
        print(f"  ✅ Development script: {dev_script}")
        
        # Production startup script
        prod_script = self.mac_studio_dir / "start_production.sh"
        with open(prod_script, 'w') as f:
            f.write(f"""#!/bin/bash
# Mac Studio RAG Production Startup Script

echo "🏭 Starting Mac Studio LIHTC RAG System (Production Mode)"
echo "========================================================="

# Activate environment
source {self.mac_studio_dir}/venv/bin/activate

# Start production backend with gunicorn
echo "🔧 Starting production backend..."
cd {self.mac_studio_dir}/backend
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000 --daemon

# Start Redis cache
echo "📦 Starting Redis cache..."
redis-server --daemonize yes

echo "✅ Mac Studio RAG System is running in production mode!"
echo "   - Backend:  http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Health:   http://localhost:8000/health"
echo ""
echo "To stop: ./stop_production.sh"
""")
        os.chmod(prod_script, 0o755)
        print(f"  ✅ Production script: {prod_script}")

    def verify_data_access(self):
        """Verify access to existing QAP and federal data"""
        print("\n🔍 Verifying data access...")
        
        # Check QAP data
        qap_processed = self.data_dir / "QAP" / "_processed"
        if qap_processed.exists():
            master_index = qap_processed / "master_chunk_index.json"
            if master_index.exists():
                with open(master_index, 'r') as f:
                    data = json.load(f)
                    total_chunks = data.get('total_chunks', 0)
                    print(f"  ✅ QAP data: {total_chunks:,} chunks across {len(data.get('states_processed', []))} states")
            else:
                print(f"  ⚠️  QAP master index not found: {master_index}")
        else:
            print(f"  ❌ QAP processed data not found: {qap_processed}")
        
        # Check federal data
        federal_processed = self.data_dir / "federal" / "LIHTC_Federal_Sources" / "_processed"
        if federal_processed.exists():
            federal_chunks = list(federal_processed.glob("chunks/*.json"))
            print(f"  ✅ Federal data: {len(federal_chunks)} chunk files")
        else:
            print(f"  ⚠️  Federal processed data not found: {federal_processed}")
        
        # Check existing indexes
        qap_indexes = qap_processed / "_indexes"
        if qap_indexes.exists():
            index_files = list(qap_indexes.glob("*.json"))
            print(f"  ✅ Existing indexes: {len(index_files)} files")
        else:
            print(f"  ⚠️  QAP indexes not found: {qap_indexes}")

    def create_integration_guide(self):
        """Create integration guide for existing federal system"""
        print("\n📚 Creating integration guide...")
        
        guide_content = f"""# Mac Studio RAG Integration Guide

## Overview
This guide explains how to integrate the Mac Studio RAG system with the existing Federal LIHTC RAG system that provides 27,344 total chunks (96 federal + 27,248 state).

## System Integration Points

### 1. Data Sources (Read-Only)
- **QAP Data**: `{self.data_dir}/QAP/_processed/`
- **Federal Data**: `{self.data_dir}/federal/LIHTC_Federal_Sources/_processed/`
- **Unified Indexes**: Available through existing system

### 2. Existing Federal Integration (DO NOT DUPLICATE)
The following components are already complete and operational:
- ✅ `federal_lihtc_processor.py` - Federal document processing
- ✅ `federal_rag_indexer.py` - Federal indexing system  
- ✅ `master_rag_integrator.py` - Federal + state integration
- ✅ `unified_lihtc_rag_query.py` - Cross-jurisdictional queries

### 3. Mac Studio RAG Focus Areas
Build NEW components that complement (don't duplicate) existing work:

#### A. Production Query Interface
- **FastAPI Backend**: RESTful API for query processing
- **React Frontend**: Professional user interface
- **Caching Layer**: Redis for performance optimization
- **Export Tools**: PDF/Excel report generation

#### B. Local LLM Integration
- **Model**: Llama 2 70B for semantic understanding
- **Purpose**: Enhanced query processing and result summarization
- **Integration**: Use existing federal authority hierarchy

#### C. Mac Studio Optimizations
- **Performance**: M2 Ultra GPU acceleration
- **Memory**: 128GB+ unified memory optimization
- **Storage**: Local SSD caching for fast access

## Integration Architecture

```
Existing Federal System (READ-ONLY)
├── 27,344 total chunks
├── Authority hierarchy (statutory → regulatory → guidance)
├── Cross-jurisdictional search
└── Conflict resolution

New Mac Studio System (BUILDS ON TOP)
├── FastAPI query interface
├── React user interface  
├── Local LLM processing
├── Caching layer
└── Export capabilities
```

## Development Approach

### Phase 1: API Integration
1. Create FastAPI wrapper around existing unified query system
2. Implement caching layer for performance
3. Add authentication and rate limiting

### Phase 2: User Interface
1. Build React frontend with professional UX
2. Implement advanced filtering and search
3. Add export and reporting capabilities

### Phase 3: Local LLM Enhancement
1. Integrate Llama 2 70B for semantic processing
2. Add result summarization and explanation
3. Implement query suggestion and refinement

## Performance Targets
- **Query Response**: <500ms for cached results
- **Cold Queries**: <2 seconds with LLM processing
- **Concurrent Users**: 50+ simultaneous queries
- **Memory Usage**: <32GB typical, <64GB peak

## File Locations
- **Mac Studio Code**: `{self.mac_studio_dir}/`
- **Configuration**: `{self.mac_studio_dir}/config/`
- **Local Cache**: `{self.mac_studio_dir}/data/cache/`
- **Models**: `{self.mac_studio_dir}/data/models/`

## Next Steps
1. Complete Mac Studio environment setup
2. Build FastAPI integration with existing system
3. Create React frontend for user queries
4. Test integration with federal authority hierarchy
5. Deploy on Mac Studio for production use

*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        guide_path = self.mac_studio_dir / "docs" / "integration_guide.md"
        with open(guide_path, 'w') as f:
            f.write(guide_content)
        print(f"  ✅ Integration guide: {guide_path}")

    def run_setup(self):
        """Run complete Mac Studio setup process"""
        print("🍎 Mac Studio LIHTC RAG Setup")
        print("=" * 50)
        
        # Check system requirements
        system_info = self.check_system_requirements()
        
        # Setup Python environment
        self.setup_python_environment()
        
        # Create directory structure
        self.create_directory_structure()
        
        # Create configuration files
        self.create_configuration_files()
        
        # Create startup scripts
        self.create_startup_scripts()
        
        # Verify data access
        self.verify_data_access()
        
        # Create integration guide
        self.create_integration_guide()
        
        print("\n🎉 Mac Studio setup complete!")
        print(f"📁 Setup location: {self.mac_studio_dir}")
        print("\nNext steps:")
        print(f"1. Activate environment: source {self.mac_studio_dir}/activate_env.sh")
        print(f"2. Review configuration: {self.mac_studio_dir}/config/mac_studio_config.json")
        print(f"3. Start development: {self.mac_studio_dir}/start_development.sh")
        print(f"4. Read integration guide: {self.mac_studio_dir}/docs/integration_guide.md")
        
        return {
            "setup_directory": str(self.mac_studio_dir),
            "system_info": system_info,
            "status": "complete"
        }

if __name__ == "__main__":
    setup = MacStudioSetup()
    result = setup.run_setup()
    print(f"\n✅ Setup result: {result['status']}")