"""
Dummy data for testing the discount service.
"""

from decimal import Decimal
from src.models import (
    Product,
    CartItem,
    CustomerProfile,
    PaymentInfo,
    BrandTier,
)


def get_test_cart_scenario():
    """
    Multiple Discount Scenario:
    - PUMA T-shirt with "Min 40% off"
    - Additional 10% off on T-shirts category
    - ICICI bank offer of 10% instant discount
    """
    # Create PUMA T-shirt product
    puma_tshirt = Product(
        id="prod_001",
        brand="PUMA",
        brand_tier=BrandTier.PREMIUM,
        category="T-shirts",
        base_price=Decimal("1000.00"),
        current_price=Decimal("1000.00"),  # Will be calculated by service
    )

    # Create cart item
    cart_item = CartItem(
        product=puma_tshirt,
        quantity=1,
        size="M",
    )

    # Create customer profile
    customer = CustomerProfile(
        id="cust_001",
        tier="regular",
        voucher_code=None,  # No voucher for this scenario
    )

    # Create payment info with ICICI bank card
    payment_info = PaymentInfo(
        method="CARD",
        bank_name="ICICI",
        card_type="CREDIT",
    )

    return {
        "cart_items": [cart_item],
        "customer": customer,
        "payment_info": payment_info,
    }


def get_test_voucher_scenario():
    """
    Scenario with voucher code 'SUPER69' for 69% off.
    """
    puma_tshirt = Product(
        id="prod_001",
        brand="PUMA",
        brand_tier=BrandTier.PREMIUM,
        category="T-shirts",
        base_price=Decimal("1000.00"),
        current_price=Decimal("1000.00"),
    )

    cart_item = CartItem(
        product=puma_tshirt,
        quantity=1,
        size="M",
    )

    customer = CustomerProfile(
        id="cust_002",
        tier="regular",
        voucher_code="SUPER69",
    )

    payment_info = PaymentInfo(
        method="CARD",
        bank_name="HDFC",
        card_type="CREDIT",
    )

    return {
        "cart_items": [cart_item],
        "customer": customer,
        "payment_info": payment_info,
    }

