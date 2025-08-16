#!/usr/bin/env python3
"""
Pipeline Manager - OpenAI Client Integration
Roman Engineering Standard: Built for 2000+ year reliability

Centralized OpenAI API client with advanced error handling, rate limiting,
and specialized prompt management for real estate document processing.
"""

import os
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib

# OpenAI imports
import openai
from openai import OpenAI
from openai.types.chat import ChatCompletion

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Available OpenAI model types"""
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4O = "gpt-4o"

@dataclass
class OpenAIConfig:
    """OpenAI client configuration"""
    api_key: Optional[str] = None
    model: ModelType = ModelType.GPT_4
    max_tokens: int = 4000
    temperature: float = 0.1
    timeout_seconds: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0
    rate_limit_rpm: int = 3000  # Requests per minute
    rate_limit_tpm: int = 40000  # Tokens per minute
    enable_caching: bool = True
    cache_ttl_hours: int = 24

@dataclass
class APIUsageStats:
    """Track API usage statistics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens_used: int = 0
    total_cost_usd: float = 0.0
    average_response_time: float = 0.0
    last_reset: datetime = None

class RateLimiter:
    """Rate limiting for OpenAI API calls"""
    
    def __init__(self, requests_per_minute: int, tokens_per_minute: int):
        self.rpm_limit = requests_per_minute
        self.tpm_limit = tokens_per_minute
        self.request_times = []
        self.token_usage = []
        
    def can_make_request(self, estimated_tokens: int = 1000) -> Tuple[bool, float]:
        """Check if request can be made within rate limits"""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old entries
        self.request_times = [t for t in self.request_times if t > minute_ago]
        self.token_usage = [(t, tokens) for t, tokens in self.token_usage if t > minute_ago]
        
        # Check request rate limit
        if len(self.request_times) >= self.rpm_limit:
            oldest_request = min(self.request_times)
            wait_time = (oldest_request + timedelta(minutes=1) - now).total_seconds()
            return False, max(wait_time, 0)
        
        # Check token rate limit
        current_tokens = sum(tokens for _, tokens in self.token_usage)
        if current_tokens + estimated_tokens > self.tpm_limit:
            # Find when we can make the request
            oldest_token_time = min([t for t, _ in self.token_usage]) if self.token_usage else now
            wait_time = (oldest_token_time + timedelta(minutes=1) - now).total_seconds()
            return False, max(wait_time, 0)
        
        return True, 0.0
    
    def record_request(self, tokens_used: int):
        """Record a successful request"""
        now = datetime.now()
        self.request_times.append(now)
        self.token_usage.append((now, tokens_used))

class ResponseCache:
    """Simple response caching system"""
    
    def __init__(self, ttl_hours: int = 24):
        self.cache = {}
        self.ttl = timedelta(hours=ttl_hours)
    
    def _generate_key(self, prompt: str, model: str, temperature: float) -> str:
        """Generate cache key from request parameters"""
        content = f"{prompt}|{model}|{temperature}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, prompt: str, model: str, temperature: float) -> Optional[Dict[str, Any]]:
        """Get cached response"""
        key = self._generate_key(prompt, model, temperature)
        
        if key in self.cache:
            cached_data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                logger.debug(f"Cache hit for prompt hash: {key[:8]}...")
                return cached_data
            else:
                # Remove expired entry
                del self.cache[key]
        
        return None
    
    def set(self, prompt: str, model: str, temperature: float, response: Dict[str, Any]):
        """Cache response"""
        key = self._generate_key(prompt, model, temperature)
        self.cache[key] = (response, datetime.now())
        logger.debug(f"Cached response for prompt hash: {key[:8]}...")
    
    def clear_expired(self):
        """Clear expired cache entries"""
        now = datetime.now()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items() 
            if now - timestamp >= self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")

class OpenAIClient:
    """Enhanced OpenAI client with real estate document processing optimizations"""
    
    def __init__(self, config: Optional[OpenAIConfig] = None):
        """Initialize OpenAI client with configuration"""
        self.config = config or OpenAIConfig()
        self.client = self._initialize_client()
        self.rate_limiter = RateLimiter(self.config.rate_limit_rpm, self.config.rate_limit_tpm)
        self.cache = ResponseCache(self.config.cache_ttl_hours) if self.config.enable_caching else None
        self.usage_stats = APIUsageStats(last_reset=datetime.now())
        self.pricing = self._initialize_pricing()
        
        logger.info(f"OpenAI client initialized with model: {self.config.model.value}")
    
    def _initialize_client(self) -> OpenAI:
        """Initialize OpenAI client with API key"""
        api_key = self.config.api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key must be provided via config or OPENAI_API_KEY environment variable")
        
        return OpenAI(api_key=api_key, timeout=self.config.timeout_seconds)
    
    def _initialize_pricing(self) -> Dict[str, Dict[str, float]]:
        """Initialize token pricing for cost tracking"""
        return {
            "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
            "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "gpt-4o": {"input": 0.005, "output": 0.015}
        }
    
    def extract_with_prompt(self, content: str, extraction_prompt: str, 
                           model: Optional[ModelType] = None,
                           temperature: Optional[float] = None) -> Dict[str, Any]:
        """Extract data using custom prompt with error handling and retries"""
        model = model or self.config.model
        temperature = temperature if temperature is not None else self.config.temperature
        
        # Build full prompt
        full_prompt = f"{extraction_prompt}\n\nDocument content:\n{content}"
        
        # Check cache first
        if self.cache:
            cached_response = self.cache.get(full_prompt, model.value, temperature)
            if cached_response:
                return cached_response
        
        # Estimate token count for rate limiting
        estimated_tokens = len(full_prompt.split()) * 1.3  # Rough estimation
        
        for attempt in range(self.config.max_retries):
            try:
                # Check rate limits
                can_proceed, wait_time = self.rate_limiter.can_make_request(int(estimated_tokens))
                if not can_proceed:
                    logger.info(f"Rate limit reached, waiting {wait_time:.1f} seconds")
                    time.sleep(wait_time)
                
                # Make API call
                start_time = time.time()
                response = self._make_api_call(full_prompt, model.value, temperature)
                response_time = time.time() - start_time
                
                # Parse response
                parsed_response = self._parse_response(response)
                
                # Update statistics
                self._update_usage_stats(response, response_time, success=True)
                
                # Record for rate limiting
                tokens_used = response.usage.total_tokens if response.usage else int(estimated_tokens)
                self.rate_limiter.record_request(tokens_used)
                
                # Cache response
                if self.cache:
                    self.cache.set(full_prompt, model.value, temperature, parsed_response)
                
                logger.debug(f"Successful extraction in {response_time:.2f}s, {tokens_used} tokens")
                return parsed_response
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing error on attempt {attempt + 1}: {e}")
                if attempt == self.config.max_retries - 1:
                    self._update_usage_stats(None, 0, success=False)
                    raise Exception(f"Failed to parse JSON response after {self.config.max_retries} attempts")
                
            except openai.RateLimitError as e:
                wait_time = self.config.retry_delay * (2 ** attempt)
                logger.warning(f"Rate limit error, waiting {wait_time:.1f}s before retry {attempt + 1}")
                time.sleep(wait_time)
                
            except openai.APITimeoutError as e:
                logger.warning(f"API timeout on attempt {attempt + 1}")
                if attempt == self.config.max_retries - 1:
                    self._update_usage_stats(None, 0, success=False)
                    raise Exception(f"API timeout after {self.config.max_retries} attempts")
                
            except Exception as e:
                logger.error(f"API error on attempt {attempt + 1}: {str(e)}")
                if attempt == self.config.max_retries - 1:
                    self._update_usage_stats(None, 0, success=False)
                    raise Exception(f"API call failed after {self.config.max_retries} attempts: {str(e)}")
                
                time.sleep(self.config.retry_delay * (2 ** attempt))
        
        raise Exception("Extraction failed after all retry attempts")
    
    def _make_api_call(self, prompt: str, model: str, temperature: float) -> ChatCompletion:
        """Make the actual API call to OpenAI"""
        return self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a precise real estate document extraction specialist. Return only valid JSON with accurate data extraction."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.config.max_tokens,
            temperature=temperature,
            timeout=self.config.timeout_seconds
        )
    
    def _parse_response(self, response: ChatCompletion) -> Dict[str, Any]:
        """Parse OpenAI response and extract JSON data"""
        response_text = response.choices[0].message.content.strip()
        
        # Clean response (remove markdown formatting if present)
        if response_text.startswith('```json'):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith('```'):
            response_text = response_text[3:-3].strip()
        
        # Parse JSON
        parsed_data = json.loads(response_text)
        
        # Add metadata
        parsed_data["_api_metadata"] = {
            "model_used": response.model,
            "tokens_used": response.usage.total_tokens if response.usage else None,
            "prompt_tokens": response.usage.prompt_tokens if response.usage else None,
            "completion_tokens": response.usage.completion_tokens if response.usage else None,
            "response_timestamp": datetime.now().isoformat()
        }
        
        return parsed_data
    
    def _update_usage_stats(self, response: Optional[ChatCompletion], response_time: float, success: bool):
        """Update usage statistics"""
        self.usage_stats.total_requests += 1
        
        if success:
            self.usage_stats.successful_requests += 1
            
            if response and response.usage:
                self.usage_stats.total_tokens_used += response.usage.total_tokens
                
                # Calculate cost
                model_pricing = self.pricing.get(response.model, {"input": 0, "output": 0})
                input_cost = (response.usage.prompt_tokens / 1000) * model_pricing["input"]
                output_cost = (response.usage.completion_tokens / 1000) * model_pricing["output"]
                self.usage_stats.total_cost_usd += input_cost + output_cost
            
            # Update average response time
            total_successful = self.usage_stats.successful_requests
            current_avg = self.usage_stats.average_response_time
            self.usage_stats.average_response_time = ((current_avg * (total_successful - 1)) + response_time) / total_successful
            
        else:
            self.usage_stats.failed_requests += 1
    
    def batch_extract(self, content_list: List[str], extraction_prompt: str,
                     max_concurrent: int = 3) -> List[Dict[str, Any]]:
        """Process multiple documents concurrently"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            # Submit all tasks
            future_to_content = {
                executor.submit(self.extract_with_prompt, content, extraction_prompt): content 
                for content in content_list
            }
            
            # Collect results
            for future in future_to_content:
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Batch extraction failed for one document: {str(e)}")
                    results.append({"error": str(e), "success": False})
        
        logger.info(f"Batch extraction completed: {len(results)} documents processed")
        return results
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        return {
            "total_requests": self.usage_stats.total_requests,
            "successful_requests": self.usage_stats.successful_requests,
            "failed_requests": self.usage_stats.failed_requests,
            "success_rate": self.usage_stats.successful_requests / max(self.usage_stats.total_requests, 1),
            "total_tokens_used": self.usage_stats.total_tokens_used,
            "total_cost_usd": self.usage_stats.total_cost_usd,
            "average_response_time": self.usage_stats.average_response_time,
            "cache_enabled": self.cache is not None,
            "cache_size": len(self.cache.cache) if self.cache else 0,
            "last_reset": self.usage_stats.last_reset.isoformat()
        }
    
    def reset_usage_statistics(self):
        """Reset usage statistics"""
        self.usage_stats = APIUsageStats(last_reset=datetime.now())
        logger.info("Usage statistics reset")
    
    def optimize_prompt(self, base_prompt: str, document_type: str) -> str:
        """Optimize prompt for specific document type"""
        optimizations = {
            "offering_memorandum": {
                "focus_areas": ["property details", "financial metrics", "market data"],
                "precision_instructions": "Pay special attention to financial figures and property specifications.",
                "format_guidance": "Ensure all monetary values are in numeric format without currency symbols."
            },
            "financial_statement": {
                "focus_areas": ["income statement", "expense breakdown", "ratios"],
                "precision_instructions": "Extract all financial line items with precise amounts.",
                "format_guidance": "Convert percentages to decimal format (e.g., 5.5% = 0.055)."
            },
            "rent_roll": {
                "focus_areas": ["unit details", "tenant information", "lease terms"],
                "precision_instructions": "Capture individual unit data and occupancy status.",
                "format_guidance": "Structure unit data as arrays with consistent field names."
            },
            "property_report": {
                "focus_areas": ["condition assessment", "valuation", "improvements needed"],
                "precision_instructions": "Focus on condition ratings and improvement cost estimates.",
                "format_guidance": "Normalize condition descriptions to standard categories."
            }
        }
        
        doc_optimization = optimizations.get(document_type, {})
        
        if doc_optimization:
            optimized_prompt = f"{base_prompt}\n\nDOCUMENT TYPE OPTIMIZATION:\n"
            optimized_prompt += f"Focus Areas: {', '.join(doc_optimization.get('focus_areas', []))}\n"
            optimized_prompt += f"Special Instructions: {doc_optimization.get('precision_instructions', '')}\n"
            optimized_prompt += f"Format Guidance: {doc_optimization.get('format_guidance', '')}\n"
            return optimized_prompt
        
        return base_prompt
    
    def validate_api_key(self) -> bool:
        """Validate API key with a simple test call"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            logger.info("API key validation successful")
            return True
        except Exception as e:
            logger.error(f"API key validation failed: {str(e)}")
            return False
    
    def cleanup_cache(self):
        """Clean up expired cache entries"""
        if self.cache:
            self.cache.clear_expired()

# Specialized prompt templates for different document types
class PromptTemplates:
    """Pre-defined prompt templates optimized for real estate documents"""
    
    @staticmethod
    def offering_memorandum_extraction() -> str:
        """Optimized prompt for offering memorandum extraction"""
        return """
You are a real estate document extraction specialist. Extract structured data from this offering memorandum with maximum accuracy.

Extract the following information in JSON format:

{
  "property_details": {
    "name": "Property name",
    "address": "Full property address",
    "city": "City",
    "state": "State (2-letter code)",
    "zip_code": "ZIP code",
    "unit_count": "Total number of units (integer)",
    "square_footage": "Total square footage (number)",
    "year_built": "Year built (integer)",
    "property_type": "Property type",
    "property_class": "Property class (A, B, C, D)"
  },
  "financial_metrics": {
    "purchase_price": "Purchase price (number only, no commas or $)",
    "net_operating_income": "Annual NOI (number)",
    "cap_rate": "Cap rate as decimal (e.g., 0.055 for 5.5%)",
    "occupancy_rate": "Occupancy as decimal (e.g., 0.95 for 95%)",
    "gross_rent_multiplier": "GRM (number)"
  },
  "rent_information": {
    "average_rent": "Average rent per unit (number)",
    "rent_per_sqft": "Average rent per square foot (number)"
  },
  "market_data": {
    "submarket": "Submarket or neighborhood",
    "median_household_income": "Area median income (number)"
  },
  "transaction_details": {
    "listing_broker": "Listing broker name",
    "broker_company": "Broker company",
    "days_on_market": "Days on market (integer)"
  }
}

CRITICAL REQUIREMENTS:
1. Extract ONLY information explicitly stated in the document
2. For missing information, use null
3. Convert all financial figures to numbers (remove $, commas)
4. Express percentages as decimals (5.5% = 0.055)
5. Ensure data type consistency (integers for counts, floats for rates)
6. Return valid JSON only
"""
    
    @staticmethod
    def financial_statement_extraction() -> str:
        """Optimized prompt for financial statement extraction"""
        return """
Extract financial data from this financial statement or operating report.

Return data in this JSON structure:

{
  "income_statement": {
    "rental_income": "Rental income amount (number)",
    "other_income": "Other income amount (number)",
    "total_income": "Total income (number)"
  },
  "expense_statement": {
    "management_fees": "Management fees (number)",
    "maintenance": "Maintenance costs (number)",
    "utilities": "Utility costs (number)",
    "insurance": "Insurance costs (number)",
    "taxes": "Property taxes (number)",
    "total_expenses": "Total operating expenses (number)",
    "net_operating_income": "Net operating income (number)"
  },
  "financial_ratios": {
    "expense_ratio": "Operating expense ratio as decimal",
    "occupancy_rate": "Occupancy rate as decimal"
  },
  "period_information": {
    "reporting_year": "Reporting year (integer)",
    "period_type": "Period type (annual, quarterly, monthly, ytd, t12)"
  }
}

REQUIREMENTS:
- Extract only explicitly stated financial data
- Convert all amounts to numbers (no $, commas)
- Convert percentages to decimals
- Use null for missing data
- Return valid JSON only
"""

# Example usage and testing
if __name__ == "__main__":
    # Initialize client
    config = OpenAIConfig(
        model=ModelType.GPT_4,
        temperature=0.1,
        enable_caching=True
    )
    
    client = OpenAIClient(config)
    
    # Validate API key
    if client.validate_api_key():
        logger.info("OpenAI client ready for use")
        
        # Example extraction
        sample_content = "Sample offering memorandum content..."
        prompt = PromptTemplates.offering_memorandum_extraction()
        
        try:
            # result = client.extract_with_prompt(sample_content, prompt)
            # print(f"Extraction successful: {len(result)} fields extracted")
            pass
        except Exception as e:
            logger.error(f"Example extraction failed: {str(e)}")
        
        # Display usage stats
        stats = client.get_usage_statistics()
        logger.info(f"Usage stats: {stats['total_requests']} requests, ${stats['total_cost_usd']:.4f} spent")
    else:
        logger.error("API key validation failed - check configuration")