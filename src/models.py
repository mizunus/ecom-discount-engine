"""
Data models for the discount service.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime
from decimal import Decimal
from enum import Enum


class BrandTier(Enum):
    """Enumeration for different brand quality tiers."""
    PREMIUM = "premium"
    REGULAR = "regular"
    BUDGET = "budget"


@dataclass
class Product:
    """Represents a single product in the e-commerce catalog."""
    id: str
    brand: str
    brand_tier: BrandTier
    category: str
    base_price: Decimal
    current_price: Decimal  # After brand/category discount


@dataclass
class CartItem:
    """Represents a product item within a shopping cart."""
    product: Product
    quantity: int
    size: str


@dataclass
class PaymentInfo:
    """Contains information about the payment method used."""
    method: str  # CARD, UPI, etc
    bank_name: Optional[str]
    card_type: Optional[str]  # CREDIT, DEBIT


@dataclass
class DiscountedPrice:
    """Represents the final price summary after all discounts are applied."""
    original_price: Decimal
    final_price: Decimal
    applied_discounts: Dict[str, Decimal]  # discount_name -> amount
    message: str


@dataclass
class AppliedDiscount:
    """Represents a single discount application."""
    name: str
    amount: Decimal
    description: Optional[str] = None


@dataclass
class CustomerProfile:
    """Represents the profile of the customer making the purchase."""
    id: str
    tier: str  # e.g., 'gold', 'silver', 'bronze'
    voucher_code: Optional[str] = None  # Optional voucher code to apply

