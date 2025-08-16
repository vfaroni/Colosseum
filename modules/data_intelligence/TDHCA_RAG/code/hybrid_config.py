#!/usr/bin/env python3
"""
Hybrid Extraction Configuration

Configuration settings for the Llama + Claude hybrid extraction system.
Adjust these settings based on your needs and infrastructure.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class HybridConfig:
    """Configuration for hybrid extraction system"""
    
    # Ollama Configuration
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.3:70b"  # Adjust based on your Ollama model name
    ollama_timeout: int = 60  # seconds
    ollama_temperature: float = 0.1  # Low temperature for consistent extraction
    
    # Claude Configuration (if using API)
    claude_api_key: Optional[str] = None  # Set if using Claude API
    claude_model_sonnet: str = "claude-3-sonnet-20240229"
    claude_model_opus: str = "claude-3-opus-20240229"
    
    # Extraction Thresholds
    confidence_thresholds: Dict[str, float] = None
    
    # Escalation Rules
    escalation_rules: Dict[str, List[str]] = None
    
    # Performance Settings
    batch_size: int = 5  # Process N files at a time
    max_retries: int = 3  # Retry failed extractions
    enable_caching: bool = True  # Cache extraction results
    
    # Quality Settings
    require_financial_validation: bool = True
    require_address_validation: bool = True
    min_acceptable_confidence: float = 0.7
    
    # Cost Controls
    max_claude_calls_per_file: int = 3  # Limit API calls
    prefer_llama_for: List[str] = None  # Field types to always use Llama for
    
    def __post_init__(self):
        """Initialize default values for complex fields"""
        
        if self.confidence_thresholds is None:
            self.confidence_thresholds = {
                'minimum': 0.7,      # Below this, always escalate
                'target': 0.85,      # Target confidence level
                'high': 0.95,        # High confidence, no review needed
                'financial': 0.9,    # Financial data threshold
                'address': 0.85      # Address data threshold
            }
        
        if self.escalation_rules is None:
            self.escalation_rules = {
                'always_escalate': [
                    'ami_matrix',  # Complex AMI calculations
                    'financial_validation',  # Cross-check financials
                ],
                'escalate_if_low_confidence': [
                    'complex_addresses',
                    'developer_fee_calculation',
                    'equity_pricing'
                ],
                'never_escalate': [
                    'application_number',
                    'state',
                    'property_type'
                ]
            }
        
        if self.prefer_llama_for is None:
            self.prefer_llama_for = [
                'basic_info',
                'unit_counts', 
                'simple_dates',
                'developer_name'
            ]


# Preset configurations for different use cases
class PresetConfigs:
    """Preset configurations for common scenarios"""
    
    @staticmethod
    def development() -> HybridConfig:
        """Configuration for development/testing"""
        return HybridConfig(
            batch_size=1,
            max_claude_calls_per_file=5,
            min_acceptable_confidence=0.6
        )
    
    @staticmethod
    def production() -> HybridConfig:
        """Configuration for production use"""
        return HybridConfig(
            batch_size=10,
            max_claude_calls_per_file=3,
            min_acceptable_confidence=0.75,
            enable_caching=True
        )
    
    @staticmethod
    def cost_optimized() -> HybridConfig:
        """Configuration optimized for minimum cost"""
        config = HybridConfig(
            batch_size=20,
            max_claude_calls_per_file=1,
            min_acceptable_confidence=0.7
        )
        # Only escalate the most critical fields
        config.escalation_rules['always_escalate'] = ['ami_matrix']
        return config
    
    @staticmethod
    def quality_optimized() -> HybridConfig:
        """Configuration optimized for maximum quality"""
        config = HybridConfig(
            batch_size=5,
            max_claude_calls_per_file=5,
            min_acceptable_confidence=0.9
        )
        # Lower thresholds for more escalation
        config.confidence_thresholds['minimum'] = 0.8
        config.confidence_thresholds['target'] = 0.95
        return config


# Model capability mapping
MODEL_CAPABILITIES = {
    'llama3.3:70b': {
        'strengths': [
            'pattern_matching',
            'structured_data_extraction', 
            'numeric_extraction',
            'simple_text_parsing'
        ],
        'weaknesses': [
            'complex_address_parsing',
            'financial_calculations',
            'regulatory_compliance_checks'
        ],
        'optimal_chunk_size': 4000,  # tokens
        'max_chunk_size': 8000
    },
    'claude-sonnet': {
        'strengths': [
            'address_parsing',
            'data_validation',
            'error_correction',
            'complex_patterns'
        ],
        'optimal_chunk_size': 100000,
        'cost_per_1k_tokens': 0.003
    },
    'claude-opus': {
        'strengths': [
            'financial_validation',
            'regulatory_compliance',
            'complex_reasoning',
            'quality_assurance'
        ],
        'optimal_chunk_size': 200000,
        'cost_per_1k_tokens': 0.015
    }
}


def get_config(preset: str = 'production') -> HybridConfig:
    """Get configuration by preset name"""
    
    presets = {
        'development': PresetConfigs.development,
        'production': PresetConfigs.production,
        'cost_optimized': PresetConfigs.cost_optimized,
        'quality_optimized': PresetConfigs.quality_optimized
    }
    
    if preset in presets:
        return presets[preset]()
    else:
        return HybridConfig()


if __name__ == "__main__":
    # Example: Show different configurations
    
    print("🔧 HYBRID EXTRACTION CONFIGURATIONS")
    print("="*60)
    
    for preset_name in ['development', 'production', 'cost_optimized', 'quality_optimized']:
        config = get_config(preset_name)
        print(f"\n{preset_name.upper()} Configuration:")
        print(f"  Batch Size: {config.batch_size}")
        print(f"  Max Claude Calls: {config.max_claude_calls_per_file}")
        print(f"  Min Confidence: {config.min_acceptable_confidence}")
        print(f"  Confidence Thresholds: {config.confidence_thresholds['minimum']}-{config.confidence_thresholds['target']}")
        print(f"  Always Escalate: {', '.join(config.escalation_rules['always_escalate'])}")