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


class DiscountService:
    """
    Service for calculating and validating discounts on cart items.
    
    Discount application order:
    1. Brand/Category discounts
    2. Voucher codes
    3. Bank offers
    """

    # Brand-specific discounts: brand_name -> discount_percentage
    BRAND_DISCOUNTS: Dict[str, Decimal] = {
        "PUMA": Decimal("40.0"),  # 40% off on PUMA
    }

    # Category-specific discounts: category_name -> discount_percentage
    CATEGORY_DISCOUNTS: Dict[str, Decimal] = {
        "T-shirts": Decimal("10.0"),  # 10% off on T-shirts
    }

    # Voucher codes: code -> discount_percentage
    VOUCHER_DISCOUNTS: Dict[str, Decimal] = {
        "SUPER69": Decimal("69.0"),  # 69% off with SUPER69
    }

    # Bank offers: bank_name -> discount_percentage
    BANK_OFFERS: Dict[str, Decimal] = {
        "ICICI": Decimal("10.0"),  # 10% off on ICICI cards
    }

    # Brand exclusions for vouchers: voucher_code -> list of excluded brands
    VOUCHER_BRAND_EXCLUSIONS: Dict[str, List[str]] = {
        # Example: "SUPER69": ["NIKE", "ADIDAS"]
    }

    # Category restrictions for vouchers: voucher_code -> allowed categories
    VOUCHER_CATEGORY_RESTRICTIONS: Dict[str, List[str]] = {
        # Example: "SUPER69": ["T-shirts", "Jeans"]
    }

    # Customer tier requirements: voucher_code -> required_tier
    VOUCHER_TIER_REQUIREMENTS: Dict[str, str] = {
        # Example: "SUPER69": "gold"
    }

    async def calculate_cart_discounts(
        self,
        cart_items: List[CartItem],
        customer: CustomerProfile,
        payment_info: Optional[PaymentInfo] = None,
    ) -> DiscountedPrice:
        """
        Calculate final price after applying discount logic:
        - First apply brand/category discounts
        - Then apply coupon codes
        - Then apply bank offers

        Args:
            cart_items: List of items in the cart
            customer: Customer profile with tier and optional voucher code
            payment_info: Optional payment information for bank offers

        Returns:
            DiscountedPrice object with final price and applied discounts
        """
        total_original_price = Decimal("0.00")
        total_final_price = Decimal("0.00")
        applied_discounts: Dict[str, Decimal] = {}

        for cart_item in cart_items:
            item_total_base = cart_item.product.base_price * cart_item.quantity
            total_original_price += item_total_base

            # Start with base price
            current_price = cart_item.product.base_price
            item_discounts: Dict[str, Decimal] = {}

            # Step 1: Apply brand/category discounts
            brand_discount_applied = False
            category_discount_applied = False

            # Apply brand discount
            if cart_item.product.brand in self.BRAND_DISCOUNTS:
                brand_discount_pct = self.BRAND_DISCOUNTS[cart_item.product.brand]
                brand_discount_amount = current_price * (brand_discount_pct / Decimal("100.0"))
                current_price -= brand_discount_amount
                item_discounts[f"{cart_item.product.brand} Brand Discount"] = brand_discount_amount
                brand_discount_applied = True

            # Apply category discount
            if cart_item.product.category in self.CATEGORY_DISCOUNTS:
                category_discount_pct = self.CATEGORY_DISCOUNTS[cart_item.product.category]
                category_discount_amount = current_price * (category_discount_pct / Decimal("100.0"))
                current_price -= category_discount_amount
                item_discounts[f"{cart_item.product.category} Category Discount"] = category_discount_amount
                category_discount_applied = True

            # Step 2: Apply voucher code if available
            if customer.voucher_code and await self.validate_discount_code(
                customer.voucher_code, [cart_item], customer
            ):
                voucher_code = customer.voucher_code
                if voucher_code in self.VOUCHER_DISCOUNTS:
                    voucher_discount_pct = self.VOUCHER_DISCOUNTS[voucher_code]
                    voucher_discount_amount = current_price * (voucher_discount_pct / Decimal("100.0"))
                    current_price -= voucher_discount_amount
                    item_discounts[f"Voucher {voucher_code}"] = voucher_discount_amount

            # Step 3: Apply bank offer if available
            if payment_info and payment_info.bank_name in self.BANK_OFFERS:
                bank_discount_pct = self.BANK_OFFERS[payment_info.bank_name]
                bank_discount_amount = current_price * (bank_discount_pct / Decimal("100.0"))
                current_price -= bank_discount_amount
                item_discounts[f"{payment_info.bank_name} Bank Offer"] = bank_discount_amount

            # Ensure price doesn't go negative
            current_price = max(current_price, Decimal("0.00"))

            # Multiply by quantity for total item price
            item_final_price = current_price * cart_item.quantity

            # Scale discounts by quantity
            for discount_name, discount_amount in item_discounts.items():
                total_discount_amount = discount_amount * cart_item.quantity
                if discount_name in applied_discounts:
                    applied_discounts[discount_name] += total_discount_amount
                else:
                    applied_discounts[discount_name] = total_discount_amount

            total_final_price += item_final_price

        # Build discount message
        messages = []
        if applied_discounts:
            messages.append("Applied discounts:")
            for discount_name, amount in applied_discounts.items():
                messages.append(f"  - {discount_name}: ₹{amount:.2f}")
        else:
            messages.append("No discounts applied")

        discount_message = "\n".join(messages)

        return DiscountedPrice(
            original_price=total_original_price,
            final_price=total_final_price,
            applied_discounts=applied_discounts,
            message=discount_message,
        )

    async def validate_discount_code(
        self,
        code: str,
        cart_items: List[CartItem],
        customer: CustomerProfile,
    ) -> bool:
        """
        Validate if a discount code can be applied.
        Handle cases like:
        - Brand exclusions
        - Category restrictions
        - Customer tier requirements

        Args:
            code: Voucher code to validate
            cart_items: List of items in the cart
            customer: Customer profile

        Returns:
            True if the voucher code can be applied, False otherwise
        """
        # Check if voucher code exists
        if code not in self.VOUCHER_DISCOUNTS:
            return False

        # Check customer tier requirements
        if code in self.VOUCHER_TIER_REQUIREMENTS:
            required_tier = self.VOUCHER_TIER_REQUIREMENTS[code]
            if customer.tier.lower() != required_tier.lower():
                return False

        # Check brand exclusions
        if code in self.VOUCHER_BRAND_EXCLUSIONS:
            excluded_brands = self.VOUCHER_BRAND_EXCLUSIONS[code]
            for cart_item in cart_items:
                if cart_item.product.brand in excluded_brands:
                    return False

        # Check category restrictions
        if code in self.VOUCHER_CATEGORY_RESTRICTIONS:
            allowed_categories = self.VOUCHER_CATEGORY_RESTRICTIONS[code]
            for cart_item in cart_items:
                if cart_item.product.category not in allowed_categories:
                    return False

        return True

