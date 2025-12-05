from decimal import Decimal
import pytest

from src.models import CartItem, CustomerProfile, Product, BrandTier
from src.rules import (
    DiscountContext,
    BrandDiscountRule,
    CategoryDiscountRule,
    VoucherDiscountRule,
    BankOfferRule,
    PaymentInfo,
)

# --- Test BrandDiscountRule ---

def test_brand_rule_applies_correctly():
    """Test discount is applied for a matching brand."""
    rule = BrandDiscountRule({"PUMA": Decimal("25.0")})
    cart = [CartItem(Product("1", "PUMA", BrandTier.PREMIUM, "Shoes", Decimal("100.0"), Decimal("100.0")), 1, "10")]
    context = DiscountContext(cart, CustomerProfile("1", "gold"))

    rule.apply(context)

    assert context.item_prices["1"] == Decimal("75.0")
    assert len(context.applied_discounts) == 1

def test_brand_rule_does_not_apply_for_other_brands():
    """Test discount is not applied for a non-matching brand."""
    rule = BrandDiscountRule({"PUMA": Decimal("25.0")})
    cart = [CartItem(Product("1", "Nike", BrandTier.PREMIUM, "Shoes", Decimal("100.0"), Decimal("100.0")), 1, "10")]
    context = DiscountContext(cart, CustomerProfile("1", "gold"))

    rule.apply(context)

    assert context.item_prices["1"] == Decimal("100.0")
    assert not context.applied_discounts

# --- Test CategoryDiscountRule ---

def test_category_rule_applies_correctly():
    """Test discount is applied for a matching category."""
    rule = CategoryDiscountRule({"Shirts": Decimal("15.0")})
    cart = [CartItem(Product("1", "Generic", BrandTier.REGULAR, "Shirts", Decimal("200.0"), Decimal("200.0")), 1, "M")]
    context = DiscountContext(cart, CustomerProfile("1", "gold"))

    rule.apply(context)

    assert context.item_prices["1"] == Decimal("170.0") # 200 * (1 - 0.15)

# --- Test VoucherDiscountRule ---

def test_voucher_rule_with_tier_requirement_success():
    """Test voucher is applied when customer tier matches requirement."""
    rule = VoucherDiscountRule({"GOLD": Decimal("50.0")}, tier_requirements={"GOLD": "gold"})
    cart = [CartItem(Product("1", "A", BrandTier.REGULAR, "B", Decimal("100.0"), Decimal("100.0")), 1, "S")]
    customer = CustomerProfile("1", tier="gold", voucher_code="GOLD")
    context = DiscountContext(cart, customer)

    rule.apply(context)

    assert context.item_prices["1"] == Decimal("50.0")

def test_voucher_rule_with_tier_requirement_failure():
    """Test voucher is NOT applied when customer tier does not match."""
    rule = VoucherDiscountRule({"GOLD": Decimal("50.0")}, tier_requirements={"GOLD": "gold"})
    cart = [CartItem(Product("1", "A", BrandTier.REGULAR, "B", Decimal("100.0"), Decimal("100.0")), 1, "S")]
    customer = CustomerProfile("1", tier="silver", voucher_code="GOLD") # Wrong tier
    context = DiscountContext(cart, customer)

    rule.apply(context)

    assert context.item_prices["1"] == Decimal("100.0")
    assert not context.applied_discounts


# --- Test BankOfferRule ---

def test_bank_offer_rule_applies_correctly():
    """Test bank discount is applied for a matching bank."""
    rule = BankOfferRule({"ICICI": Decimal("10.0")})
    cart = [CartItem(Product("1", "A", BrandTier.REGULAR, "B", Decimal("1000.0"), Decimal("1000.0")), 1, "S")]
    payment = PaymentInfo(method="CARD", bank_name="ICICI", card_type="CREDIT")
    context = DiscountContext(cart, CustomerProfile("1", "gold"), payment=payment)

    rule.apply(context)

    assert context.item_prices["1"] == Decimal("900.0")
    assert context.applied_discounts[0].name == "ICICI Bank Offer"

def test_bank_offer_rule_does_not_apply_for_wrong_bank():
    """Test bank discount is not applied for a non-matching bank."""
    rule = BankOfferRule({"ICICI": Decimal("10.0")})
    cart = [CartItem(Product("1", "A", BrandTier.REGULAR, "B", Decimal("1000.0"), Decimal("1000.0")), 1, "S")]
    payment = PaymentInfo(method="CARD", bank_name="HDFC", card_type="CREDIT")
    context = DiscountContext(cart, CustomerProfile("1", "gold"), payment=payment)

    rule.apply(context)

    assert context.item_prices["1"] == Decimal("1000.0")
    assert not context.applied_discounts

def test_bank_offer_rule_does_not_apply_without_payment_info():
    """Test bank discount is not applied when there is no payment info."""
    rule = BankOfferRule({"ICICI": Decimal("10.0")})
    cart = [CartItem(Product("1", "A", BrandTier.REGULAR, "B", Decimal("1000.0"), Decimal("1000.0")), 1, "S")]
    context = DiscountContext(cart, CustomerProfile("1", "gold"), payment=None) # No payment

    rule.apply(context)

    assert context.item_prices["1"] == Decimal("1000.0")
    assert not context.applied_discounts
