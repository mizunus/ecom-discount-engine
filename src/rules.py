from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Dict, Optional

from src.models import CartItem, CustomerProfile, PaymentInfo, AppliedDiscount


class DiscountContext:
    """
    Holds the state of the cart during discount calculation.
    Rules will read from and write to this context.
    """
    def __init__(
        self,
        cart_items: List[CartItem],
        customer: CustomerProfile,
        payment: Optional[PaymentInfo] = None,
    ):
        self.cart_items = cart_items
        self.customer = customer
        self.payment_info = payment
        # This tracks the price of each item as discounts are applied
        self.item_prices = {
            item.product.id: item.product.base_price for item in cart_items
        }
        self.applied_discounts: List[AppliedDiscount] = []

    @property
    def original_total_price(self) -> Decimal:
        return sum(item.product.base_price * item.quantity for item in self.cart_items)

    def calculate_final_price(self) -> Decimal:
        total = Decimal("0.0")
        for item in self.cart_items:
            price = self.item_prices[item.product.id]
            total += max(price, Decimal("0.0")) * item.quantity
        return total


class IDiscountRule(ABC):
    """Interface for a discount rule."""

    @abstractmethod
    def apply(self, context: DiscountContext) -> None:
        """
        Applies a discount to the cart.
        The method should modify the context by updating item_prices
        and appending to applied_discounts.
        """
        pass


class BrandDiscountRule(IDiscountRule):
    """A discount rule that applies discounts to specific brands."""
    def __init__(self, brand_discounts: Dict[str, Decimal]):
        """
        Initializes the rule with brand-to-discount mappings.

        Args:
            brand_discounts: A dictionary mapping brand names to their discount percentages.
        """
        self._brand_discounts = brand_discounts

    def apply(self, context: DiscountContext) -> None:
        for item in context.cart_items:
            product = item.product
            if product.brand in self._brand_discounts:
                discount_pct = self._brand_discounts[product.brand]
                current_price = context.item_prices[product.id]
                
                discount_amount = current_price * (discount_pct / Decimal("100.0"))
                context.item_prices[product.id] -= discount_amount

                context.applied_discounts.append(
                    AppliedDiscount(
                        name=f"{product.brand} Brand Discount",
                        amount=discount_amount * item.quantity,
                    )
                )


class CategoryDiscountRule(IDiscountRule):
    """A discount rule that applies discounts to specific product categories."""
    def __init__(self, category_discounts: Dict[str, Decimal]):
        """
        Initializes the rule with category-to-discount mappings.

        Args:
            category_discounts: A dictionary mapping category names to their discount percentages.
        """
        self._category_discounts = category_discounts

    def apply(self, context: DiscountContext) -> None:
        for item in context.cart_items:
            product = item.product
            if product.category in self._category_discounts:
                discount_pct = self._category_discounts[product.category]
                current_price = context.item_prices[product.id]
                
                discount_amount = current_price * (discount_pct / Decimal("100.0"))
                context.item_prices[product.id] -= discount_amount

                context.applied_discounts.append(
                    AppliedDiscount(
                        name=f"{product.category} Category Discount",
                        amount=discount_amount * item.quantity,
                    )
                )


class VoucherDiscountRule(IDiscountRule):
    """
    A discount rule that applies a discount based on a customer's voucher code.
    Also handles validation logic like brand exclusions and tier requirements.
    """
    def __init__(self, voucher_discounts: Dict[str, Decimal], **kwargs):
        """
        Initializes the rule with voucher codes and validation data.

        Args:
            voucher_discounts: A dictionary mapping voucher codes to discount percentages.
            **kwargs: Additional validation data, e.g., 'brand_exclusions', 'tier_requirements'.
        """
        self._voucher_discounts = voucher_discounts
        # In a real app, validation logic would also be more robust
        self._brand_exclusions = kwargs.get("brand_exclusions", {})
        self._tier_requirements = kwargs.get("tier_requirements", {})

    def _is_valid(self, code: str, context: DiscountContext) -> bool:
        """
        Checks if a voucher code is valid for the given cart context.

        Args:
            code: The voucher code to validate.
            context: The current discount context.

        Returns:
            True if the code is valid and can be applied, False otherwise.
        """
        if code not in self._voucher_discounts:
            return False
        
        # Check brand exclusions
        if code in self._brand_exclusions:
            excluded_brands = self._brand_exclusions[code]
            if any(item.product.brand in excluded_brands for item in context.cart_items):
                return False

        return True

    def apply(self, context: DiscountContext) -> None:
        code = context.customer.voucher_code
        if not code or not self._is_valid(code, context):
            return

        discount_pct = self._voucher_discounts[code]
        for item in context.cart_items:
            product = item.product
            current_price = context.item_prices[product.id]
            
            discount_amount = current_price * (discount_pct / Decimal("100.0"))
            context.item_prices[product.id] -= discount_amount
            
            context.applied_discounts.append(
                AppliedDiscount(
                    name=f"Voucher {code}",
                    amount=discount_amount * item.quantity
                )
            )