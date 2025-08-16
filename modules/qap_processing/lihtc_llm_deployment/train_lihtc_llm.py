#!/usr/bin/env python3
"""
LIHTC Fine-Tuning Script
Generated: 2025-08-01T13:01:16.107748
"""

import os
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_dataset
import json

def main():
    # Configuration
    model_name = "meta-llama/Llama-3.1-8B-Instruct"
    output_dir = "./lihtc_finetuned_model"
    training_data = "./lihtc_training_data_alpaca.json"
    
    print("🚀 Starting LIHTC LLM Fine-Tuning...")
    print(f"Base Model: {model_name}")
    print(f"Training Data: {training_data}")
    
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto"
    )
    
    # LoRA Configuration
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=16,
        lora_alpha=32,
        lora_dropout=0.1,
        target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj']
    )
    
    # Apply LoRA
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    # Load and prepare dataset
    def format_instruction(example):
        if "instruction" in example and "response" in example:
            text = f"### Instruction:\n{example['instruction']}\n\n### Response:\n{example['response']}"
        elif "text" in example:
            text = example["text"]
        else:
            text = str(example)
        return {"text": text}
    
    # Load training data
    dataset = load_dataset("json", data_files=training_data, split="train")
    dataset = dataset.map(format_instruction)
    
    def tokenize_function(examples):
        return tokenizer(examples["text"], truncation=True, padding=False, max_length=2048)
    
    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-05,
        warmup_steps=100,
        fp16=true,
        gradient_checkpointing=true,
        dataloader_num_workers=4,
        save_strategy="epoch",
        evaluation_strategy="no",
        logging_steps=10,
        logging_dir=f"{output_dir}/logs",
        report_to="none"
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer
    )
    
    # Start training
    print("🔥 Starting fine-tuning process...")
    trainer.train()
    
    # Save the model
    trainer.save_model()
    tokenizer.save_pretrained(output_dir)
    
    print(f"✅ Fine-tuning complete! Model saved to {output_dir}")

if __name__ == "__main__":
    main()
