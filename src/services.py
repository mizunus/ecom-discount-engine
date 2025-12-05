"""
Discount Service implementation for e-commerce discount calculations.
"""

from typing import List, Optional, Dict
from decimal import Decimal
from src.models import (
    CartItem,
    CustomerProfile,
    PaymentInfo,
    DiscountedPrice,
    Product,
)
from src.rules import IDiscountRule, DiscountContext


class DiscountService:
    """
    Service for calculating discounts by applying a series of rules.
    """
    def __init__(self, rules: List[IDiscountRule]):
        """
        Initializes the service with a list of discount rules.
        The order of rules in the list determines their application order.
        """
        self.rules = rules

    async def calculate_cart_discounts(
        self,
        cart_items: List[CartItem],
        customer: CustomerProfile,
        payment_info: Optional[PaymentInfo] = None,
    ) -> DiscountedPrice:
        """
        Calculate final price after applying discount logic by processing
        the configured discount rules.

        Args:
            cart_items: List of items in the cart
            customer: Customer profile with tier and optional voucher code
            payment_info: Optional payment information for bank offers

        Returns:
            DiscountedPrice object with final price and applied discounts
        """
        context = DiscountContext(cart_items, customer, payment_info)

        for rule in self.rules:
            rule.apply(context)
        
        total_original_price = context.original_total_price
        total_final_price = context.calculate_final_price()
        
        # Aggregate discounts for the final summary
        applied_discounts_summary: Dict[str, Decimal] = {}
        for discount in context.applied_discounts:
            applied_discounts_summary[discount.name] = (
                applied_discounts_summary.get(discount.name, Decimal("0.0")) + discount.amount
            )

        # Build discount message
        messages = []
        if applied_discounts_summary:
            messages.append("Applied discounts:")
            for discount_name, amount in applied_discounts_summary.items():
                messages.append(f"  - {discount_name}: ₹{amount:.2f}")
        else:
            messages.append("No discounts applied")

        discount_message = "\n".join(messages)

        return DiscountedPrice(
            original_price=total_original_price,
            final_price=total_final_price,
            applied_discounts=applied_discounts_summary,
            message=discount_message,
        )

