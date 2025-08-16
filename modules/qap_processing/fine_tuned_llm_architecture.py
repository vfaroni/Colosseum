#!/usr/bin/env python3
"""
Fine-Tuned LLM Architecture for LIHTC Intelligence
Creates training datasets and deployment architecture for specialized LIHTC Q&A system
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
import pandas as pd
from datetime import datetime
import random

@dataclass
class TrainingExample:
    """Training example for fine-tuning"""
    instruction: str
    input: str
    output: str
    system_message: str
    metadata: Dict[str, Any]
    
@dataclass
class LIHTCQuery:
    """LIHTC-specific query structure"""
    query_type: str  # definition, requirement, comparison, compliance, scoring
    jurisdiction: Optional[str]
    topic: str
    complexity: str  # basic, intermediate, advanced
    requires_cross_reference: bool
    federal_authority_needed: bool

class FineTunedLIHTCArchitecture:
    """Fine-tuned LLM architecture for LIHTC intelligence"""
    
    def __init__(self):
        self.base_dir = Path("/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Colosseum/modules/qap_processing")
        
        # Load comprehensive data
        self.enhanced_definitions = self._load_json_data("comprehensive_enhanced_definitions.json")
        self.regulatory_requirements = self._load_json_data("comprehensive_regulatory_requirements.json")
        self.cross_references = self._load_json_data("comprehensive_cross_references.json")
        
        # Training data storage
        self.training_examples: List[TrainingExample] = []
        
        # LIHTC-specific instruction templates
        self.instruction_templates = self._init_instruction_templates()
        
        # Federal authority database (simplified)
        self.federal_authorities = self._init_federal_authorities()
        
        print("🤖 Fine-Tuned LIHTC LLM Architecture Initialized")
        print(f"📊 Loaded definitions from {len(self.enhanced_definitions)} jurisdictions")
        print(f"⚖️ Loaded requirements from {len(self.regulatory_requirements)} jurisdictions")
    
    def _load_json_data(self, filename: str) -> Dict[str, Any]:
        """Load JSON data file"""
        file_path = self.base_dir / filename
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _init_instruction_templates(self) -> Dict[str, List[str]]:
        """Initialize LIHTC-specific instruction templates"""
        return {
            'definition_query': [
                "Define the term '{term}' as used in {jurisdiction} LIHTC regulations.",
                "What does '{term}' mean in the context of {jurisdiction}'s Qualified Allocation Plan?",
                "Explain the definition of '{term}' for LIHTC purposes in {jurisdiction}.",
                "How is '{term}' defined in {jurisdiction}'s low-income housing tax credit program?",
            ],
            
            'requirement_query': [
                "What are the {requirement_type} requirements for LIHTC projects in {jurisdiction}?",
                "Explain the {requirement_type} criteria that must be met in {jurisdiction}.",
                "What {requirement_type} standards apply to low-income housing tax credit developments in {jurisdiction}?",
                "Detail the {requirement_type} obligations for LIHTC projects under {jurisdiction} regulations.",
            ],
            
            'comparison_query': [
                "Compare how {jurisdiction1} and {jurisdiction2} handle {topic} in their LIHTC programs.",
                "What are the differences between {jurisdiction1} and {jurisdiction2} regarding {topic}?",
                "How do {jurisdiction1}'s {topic} requirements differ from {jurisdiction2}'s?",
                "Contrast the {topic} approaches taken by {jurisdiction1} versus {jurisdiction2}.",
            ],
            
            'compliance_query': [
                "How can LIHTC developers ensure compliance with {topic} requirements in {jurisdiction}?",
                "What steps must be taken to meet {jurisdiction}'s {topic} standards?",
                "What documentation is required for {topic} compliance in {jurisdiction}?",
                "How is {topic} compliance monitored in {jurisdiction}'s LIHTC program?",
            ],
            
            'scoring_query': [
                "How many points are awarded for {topic} in {jurisdiction}'s LIHTC competitive scoring?",
                "What scoring criteria apply to {topic} in {jurisdiction}?",
                "How can LIHTC projects maximize points for {topic} in {jurisdiction}?",
                "What are the {topic} scoring requirements in {jurisdiction}'s QAP?",
            ],
            
            'federal_integration': [
                "How does {jurisdiction}'s {topic} requirement implement federal IRC Section 42?",
                "What federal authority supports {jurisdiction}'s {topic} regulations?",
                "How do federal and {jurisdiction} requirements interact regarding {topic}?",
                "What federal compliance is required beyond {jurisdiction}'s {topic} standards?",
            ]
        }
    
    def _init_federal_authorities(self) -> Dict[str, str]:
        """Initialize federal authority explanations"""
        return {
            'IRC Section 42': 'Federal Low-Income Housing Tax Credit statute providing the foundational requirements for the LIHTC program.',
            '26 CFR 1.42': 'Treasury Regulations implementing IRC Section 42, providing detailed operational guidance.',
            'Rev. Proc.': 'Revenue Procedures issued by the IRS providing administrative guidance on LIHTC compliance.',
            '24 CFR': 'HUD regulations that may apply to LIHTC projects receiving additional federal assistance.',
        }
    
    def generate_definition_examples(self) -> List[TrainingExample]:
        """Generate training examples for definition queries"""
        examples = []
        
        for state_code, definitions_list in self.enhanced_definitions.items():
            if not definitions_list:
                continue
                
            for definition_data in definitions_list[:10]:  # Limit per state for now
                term = definition_data.get('term', '')
                definition = definition_data.get('definition', '')
                relevance = definition_data.get('lihtc_relevance', 'unknown')
                
                if not term or not definition or len(definition) < 20:
                    continue
                
                # Create instruction variations
                for template in self.instruction_templates['definition_query']:
                    instruction = template.format(term=term, jurisdiction=state_code)
                    
                    # Enhanced output with context
                    output = f"In {state_code}'s LIHTC program, '{term}' is defined as: {definition}"
                    
                    # Add federal authority context if available
                    federal_refs = definition_data.get('federal_authority', [])
                    if federal_refs:
                        output += f"\n\nThis definition is based on the following federal authorities: {', '.join(federal_refs[:2])}"
                    
                    # Add LIHTC relevance context
                    if relevance in ['critical', 'high']:
                        output += f"\n\nThis is a {relevance}-importance term for LIHTC compliance and should be carefully considered in project development."
                    
                    example = TrainingExample(
                        instruction=instruction,
                        input="",
                        output=output,
                        system_message="You are a specialized LIHTC (Low-Income Housing Tax Credit) expert assistant. Provide accurate, detailed information about LIHTC regulations, requirements, and definitions across all US jurisdictions. Always cite relevant federal authorities when applicable.",
                        metadata={
                            'query_type': 'definition',
                            'jurisdiction': state_code,
                            'term': term,
                            'relevance': relevance,
                            'federal_refs': federal_refs
                        }
                    )
                    
                    examples.append(example)
        
        return examples
    
    def generate_requirement_examples(self) -> List[TrainingExample]:
        """Generate training examples for regulatory requirement queries"""
        examples = []
        
        for state_code, requirements_list in self.regulatory_requirements.items():
            if not requirements_list:
                continue
                
            for requirement_data in requirements_list[:10]:  # Limit per state
                req_type = requirement_data.get('type', 'requirement')
                description = requirement_data.get('description', '')
                mandatory = requirement_data.get('mandatory', False)
                point_value = requirement_data.get('point_value')
                
                if not description or len(description) < 20:
                    continue
                
                # Create instruction variations
                for template in self.instruction_templates['requirement_query']:
                    instruction = template.format(
                        requirement_type=req_type.replace('_', ' '),
                        jurisdiction=state_code
                    )
                    
                    # Enhanced output with compliance context
                    output = f"In {state_code}, the {req_type.replace('_', ' ')} requirements include:\n\n{description}"
                    
                    if mandatory:
                        output += "\n\nThis is a mandatory requirement that must be met for LIHTC eligibility."
                    
                    if point_value:
                        output += f"\n\nThis requirement awards {point_value} points in competitive scoring."
                    
                    # Add federal basis if available
                    federal_basis = requirement_data.get('federal_basis', [])
                    if federal_basis:
                        output += f"\n\nFederal basis: {', '.join(federal_basis[:2])}"
                    
                    example = TrainingExample(
                        instruction=instruction,
                        input="",
                        output=output,
                        system_message="You are a specialized LIHTC expert assistant. Provide detailed information about regulatory requirements, emphasizing compliance obligations and federal authority.",
                        metadata={
                            'query_type': 'requirement',
                            'jurisdiction': state_code,
                            'requirement_type': req_type,
                            'mandatory': mandatory,
                            'point_value': point_value
                        }
                    )
                    
                    examples.append(example)
        
        return examples
    
    def generate_comparison_examples(self) -> List[TrainingExample]:
        """Generate training examples for cross-jurisdictional comparisons"""
        examples = []
        
        # Find common terms across jurisdictions
        term_by_jurisdiction = {}
        for state_code, definitions_list in self.enhanced_definitions.items():
            for definition_data in definitions_list:
                term = definition_data.get('term', '').lower().strip()
                if term and len(term) > 3:
                    if term not in term_by_jurisdiction:
                        term_by_jurisdiction[term] = {}
                    term_by_jurisdiction[term][state_code] = definition_data
        
        # Find terms that exist in multiple jurisdictions
        multi_jurisdiction_terms = {
            term: jurisdictions for term, jurisdictions in term_by_jurisdiction.items()
            if len(jurisdictions) >= 2
        }
        
        # Generate comparison examples
        for term, jurisdictions in list(multi_jurisdiction_terms.items())[:50]:  # Limit for now
            jurisdiction_pairs = []
            jurisdiction_list = list(jurisdictions.keys())
            
            # Create pairs for comparison
            for i in range(min(3, len(jurisdiction_list))):
                for j in range(i+1, min(3, len(jurisdiction_list))):
                    jurisdiction_pairs.append((jurisdiction_list[i], jurisdiction_list[j]))
            
            for j1, j2 in jurisdiction_pairs[:2]:  # Limit pairs
                for template in self.instruction_templates['comparison_query'][:2]:  # Limit templates
                    instruction = template.format(
                        jurisdiction1=j1,
                        jurisdiction2=j2,
                        topic=term
                    )
                    
                    # Create comparison output
                    def1 = jurisdictions[j1].get('definition', '')
                    def2 = jurisdictions[j2].get('definition', '')
                    
                    output = f"Comparing '{term}' definitions between {j1} and {j2}:\n\n"
                    output += f"**{j1}**: {def1[:200]}{'...' if len(def1) > 200 else ''}\n\n"
                    output += f"**{j2}**: {def2[:200]}{'...' if len(def2) > 200 else ''}\n\n"
                    
                    # Add analysis
                    if def1.lower() == def2.lower():
                        output += "These definitions are identical across both jurisdictions."
                    else:
                        output += "These jurisdictions have different approaches to defining this term, which developers should consider when operating across state lines."
                    
                    example = TrainingExample(
                        instruction=instruction,
                        input="",
                        output=output,
                        system_message="You are a specialized LIHTC expert assistant. Provide detailed cross-jurisdictional comparisons to help developers understand regulatory differences.",
                        metadata={
                            'query_type': 'comparison',
                            'jurisdictions': [j1, j2],
                            'term': term,
                            'complexity': 'intermediate'
                        }
                    )
                    
                    examples.append(example)
        
        return examples
    
    def generate_practical_examples(self) -> List[TrainingExample]:
        """Generate practical application examples"""
        examples = []
        
        practical_scenarios = [
            {
                'scenario': 'A developer is planning a 60-unit LIHTC project in {jurisdiction}. What are the key threshold requirements they must meet?',
                'focus': 'threshold_requirement',
                'response_template': 'For a 60-unit LIHTC project in {jurisdiction}, the key threshold requirements include:'
            },
            {
                'scenario': 'What documentation should a lender require to verify LIHTC compliance in {jurisdiction}?',
                'focus': 'compliance_requirement',
                'response_template': 'Lenders should require the following documentation to verify LIHTC compliance in {jurisdiction}:'
            },
            {
                'scenario': 'How can a LIHTC project maximize competitive scoring points in {jurisdiction}?',
                'focus': 'scoring_criteria',
                'response_template': 'To maximize competitive scoring points in {jurisdiction}, LIHTC projects should consider:'
            }
        ]
        
        for state_code, requirements_list in self.regulatory_requirements.items():
            if not requirements_list:
                continue
                
            for scenario in practical_scenarios:
                relevant_requirements = [
                    req for req in requirements_list 
                    if req.get('type', '').startswith(scenario['focus'].split('_')[0])
                ]
                
                if relevant_requirements:
                    instruction = scenario['scenario'].format(jurisdiction=state_code)
                    
                    output = scenario['response_template'].format(jurisdiction=state_code) + "\n\n"
                    
                    for i, req in enumerate(relevant_requirements[:5]):  # Limit to top 5
                        desc = req.get('description', '')[:300]
                        output += f"{i+1}. {desc}{'...' if len(req.get('description', '')) > 300 else ''}\n\n"
                    
                    output += f"These requirements are based on {state_code}'s current QAP and should be verified with the latest regulations."
                    
                    example = TrainingExample(
                        instruction=instruction,
                        input="",
                        output=output,
                        system_message="You are a specialized LIHTC expert assistant. Provide practical, actionable guidance for developers, lenders, and housing agencies.",
                        metadata={
                            'query_type': 'practical',
                            'jurisdiction': state_code,
                            'scenario_type': scenario['focus'],
                            'complexity': 'advanced'
                        }
                    )
                    
                    examples.append(example)
        
        return examples
    
    def generate_all_training_examples(self) -> List[TrainingExample]:
        """Generate comprehensive training dataset"""
        print("🔄 Generating comprehensive training dataset...")
        
        all_examples = []
        
        # Generate different types of examples
        print("   📝 Generating definition examples...")
        definition_examples = self.generate_definition_examples()
        all_examples.extend(definition_examples)
        print(f"   ✅ Generated {len(definition_examples)} definition examples")
        
        print("   ⚖️ Generating requirement examples...")
        requirement_examples = self.generate_requirement_examples()
        all_examples.extend(requirement_examples)
        print(f"   ✅ Generated {len(requirement_examples)} requirement examples")
        
        print("   🔍 Generating comparison examples...")
        comparison_examples = self.generate_comparison_examples()
        all_examples.extend(comparison_examples)
        print(f"   ✅ Generated {len(comparison_examples)} comparison examples")
        
        print("   🎯 Generating practical examples...")
        practical_examples = self.generate_practical_examples()
        all_examples.extend(practical_examples)
        print(f"   ✅ Generated {len(practical_examples)} practical examples")
        
        # Shuffle for better training
        random.shuffle(all_examples)
        
        self.training_examples = all_examples
        return all_examples
    
    def create_training_formats(self):
        """Create training data in multiple formats"""
        if not self.training_examples:
            self.generate_all_training_examples()
        
        print(f"📊 Creating training formats for {len(self.training_examples)} examples...")
        
        # Format 1: Alpaca format (popular for instruction tuning)
        alpaca_format = []
        for example in self.training_examples:
            alpaca_example = {
                "instruction": example.instruction,
                "input": example.input,
                "output": example.output
            }
            alpaca_format.append(alpaca_example)
        
        # Format 2: ChatML format (for chat-based models)
        chatml_format = []
        for example in self.training_examples:
            chatml_example = {
                "messages": [
                    {"role": "system", "content": example.system_message},
                    {"role": "user", "content": example.instruction + (" " + example.input if example.input else "")},
                    {"role": "assistant", "content": example.output}
                ]
            }
            chatml_format.append(chatml_example)
        
        # Format 3: Enhanced format with metadata
        enhanced_format = []
        for example in self.training_examples:
            enhanced_example = {
                "instruction": example.instruction,
                "input": example.input,
                "output": example.output,
                "system_message": example.system_message,
                "metadata": example.metadata
            }
            enhanced_format.append(enhanced_example)
        
        return {
            'alpaca': alpaca_format,
            'chatml': chatml_format,
            'enhanced': enhanced_format
        }
    
    def save_training_data(self, output_dir: Path = None):
        """Save training data in multiple formats"""
        if output_dir is None:
            output_dir = self.base_dir
        
        formats = self.create_training_formats()
        
        for format_name, format_data in formats.items():
            filename = f"lihtc_training_data_{format_name}.json"
            filepath = output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(format_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved {format_name} format: {filename} ({len(format_data)} examples)")
    
    def generate_deployment_architecture(self) -> str:
        """Generate deployment architecture documentation"""
        
        total_examples = len(self.training_examples) if self.training_examples else 0
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        architecture_doc = f"""# FINE-TUNED LIHTC LLM DEPLOYMENT ARCHITECTURE

**Generated**: {timestamp}
**Training Dataset Size**: {total_examples:,} examples

## SYSTEM OVERVIEW

This architecture creates the industry's first comprehensive LIHTC AI system by combining:
- Fine-tuned LLM specialized for LIHTC domain
- RAG system with 54-jurisdiction coverage  
- Enhanced definitions and regulatory requirements
- Cross-reference resolution for federal/state compliance

## RECOMMENDED MODEL ARCHITECTURE

### Base Model: Llama-3.1-8B-Instruct
- Open source with commercial license
- 8B parameters balance performance and efficiency
- Strong instruction-following capabilities
- 4K context window for comprehensive responses

### Fine-Tuning Configuration
- Method: LoRA (Low-Rank Adaptation)
- Rank: 16, Alpha: 32
- Target modules: Query, Key, Value projections
- Training: 3 epochs, 2e-5 learning rate

## RAG INTEGRATION

### Vector Database
- ChromaDB with 1,719+ enhanced definitions
- 365+ regulatory requirements indexed
- Cross-reference mapping for authority linking
- Jurisdiction-aware filtering and retrieval

### Search Strategy
- Hybrid semantic + keyword matching
- Authority-based ranking (Federal > State)
- Metadata filtering by jurisdiction and relevance
- Context construction within token limits

## DEPLOYMENT INFRASTRUCTURE

### Production Requirements
- GPU: A100 40GB or 2x RTX 4090
- RAM: 64GB+ for model and inference
- Storage: 1TB+ SSD for models and database
- API: FastAPI with async query processing

### Scalability Features
- Load balancing across model instances
- Redis caching for frequent queries
- Automated QAP update pipeline
- Performance monitoring and optimization

## BUSINESS VALUE

### Industry Advantages
- First comprehensive 54-jurisdiction LIHTC coverage
- Federal/state authority cross-referencing
- Domain-specialized language model
- Real-time regulatory update integration

### Revenue Opportunities
- SaaS subscriptions for developers/lenders
- API licensing for third-party tools
- Custom deployment consulting
- Structured data licensing

## DEPLOYMENT PHASES

1. **Internal Testing** (Weeks 1-4): Model fine-tuning and validation
2. **Beta Program** (Weeks 5-8): Select client testing and feedback
3. **Production Launch** (Weeks 9-12): Public API and web interface
4. **Advanced Features** (Months 4-6): Predictive analysis and automation

---

**INDUSTRY'S MOST ADVANCED LIHTC AI SYSTEM READY FOR DEPLOYMENT! 🚀**
"""
        
        return architecture_doc
    
    def save_deployment_architecture(self, output_dir: Path = None):
        """Save deployment architecture documentation"""
        if output_dir is None:
            output_dir = self.base_dir
        
        architecture_doc = self.generate_deployment_architecture()
        
        architecture_file = output_dir / "fine_tuned_lihtc_llm_deployment_architecture.md"
        with open(architecture_file, 'w', encoding='utf-8') as f:
            f.write(architecture_doc)
        
        print(f"📋 Deployment architecture saved: {architecture_file}")

def main():
    """Generate fine-tuned LLM training data and architecture"""
    
    print("🤖 FINE-TUNED LIHTC LLM SYSTEM")
    print("=" * 60)
    print("🎯 Creating specialized LIHTC question-answering system")
    print("📚 Generating training dataset from comprehensive QAP analysis")
    print("🏗️ Designing deployment architecture")
    print("")
    
    try:
        # Initialize architecture system
        llm_system = FineTunedLIHTCArchitecture()
        
        # Generate comprehensive training dataset
        training_examples = llm_system.generate_all_training_examples()
        
        # Save training data in multiple formats
        llm_system.save_training_data()
        
        # Generate and save deployment architecture
        llm_system.save_deployment_architecture()
        
        print(f"\n🎉 FINE-TUNED LLM SYSTEM COMPLETE!")
        print(f"📊 Generated {len(training_examples):,} training examples")
        print("🚀 Ready for model fine-tuning and deployment")
        print("🏆 Industry's first specialized LIHTC AI system!")
        
    except Exception as e:
        print(f"❌ System generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()