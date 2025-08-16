"""
🏛️ COLOSSEUM Email Management - Bill Email Secretary
Built to Roman Engineering Standards

This module provides LIHTC-focused email management for Bill's deal flow.
Designed for imperial scale with systematic excellence.
"""

__version__ = "1.0.0"
__author__ = "Colosseum Development Team"

from .bill_email_handler import BillEmailHandler
from .bill_email_config import BillEmailConfig
from .bill_deal_classifier import BillDealClassifier

__all__ = [
    "BillEmailHandler",
    "BillEmailConfig",
    "BillDealClassifier"
]