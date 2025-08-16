"""
🏛️ COLOSSEUM Email Management - Shared Components
Built to Roman Engineering Standards

Shared email infrastructure for both Vitor and Bill's email management systems.
Designed for imperial scale with systematic excellence.
"""

__version__ = "1.0.0"
__author__ = "Colosseum Development Team"

from .email_base_classes import BaseEmailHandler, BaseDealClassifier
from .deal_templates import DealTemplates
from .broker_database import BrokerDatabase

__all__ = [
    "BaseEmailHandler",
    "BaseDealClassifier", 
    "DealTemplates",
    "BrokerDatabase"
]