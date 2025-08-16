# LIHTC Fine-Tuned Model

## Model Information
- Base Model: meta-llama/Llama-3.1-8B-Instruct
- Fine-tuning Method: LoRA (Low-Rank Adaptation)
- Training Data: 3027 LIHTC-specific examples
- Specialization: Low-Income Housing Tax Credit regulations and compliance

## Training Details
- Training Date: 2025-08-01T13:02:02.367611
- Epochs: 3
- Learning Rate: 2e-5
- LoRA Configuration: rank=16, alpha=32

## Usage
This model is specialized for LIHTC Q&A and should be used with the RAG system for optimal results.
