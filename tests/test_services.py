import pytest
from decimal import Decimal

from src.models import CartItem, CustomerProfile, Product, BrandTier
from src.services import DiscountService
from src.rules import BrandDiscountRule, CategoryDiscountRule, VoucherDiscountRule, BankOfferRule
from src.fake_data import get_test_cart_scenario

# --- Fixtures for reusable test setup ---

@pytest.fixture
def brand_rule() -> BrandDiscountRule:
    """Fixture for a brand discount rule (40% off PUMA)."""
    return BrandDiscountRule({"PUMA": Decimal("40.0")})

@pytest.fixture
def category_rule() -> CategoryDiscountRule:
    """Fixture for a category discount rule (10% off T-shirts)."""
    return CategoryDiscountRule({"T-shirts": Decimal("10.0")})

@pytest.fixture
def voucher_rule() -> VoucherDiscountRule:
    """Fixture for a voucher rule (69% off for SUPER69)."""
    return VoucherDiscountRule({"SUPER69": Decimal("69.0")})

@pytest.fixture
def bank_rule() -> BankOfferRule:
    """Fixture for a bank offer rule (10% off ICICI)."""
    return BankOfferRule({"ICICI": Decimal("10.0")})

@pytest.fixture
def generic_customer() -> CustomerProfile:
    """Fixture for a standard customer profile."""
    return CustomerProfile(id="cust_generic", tier="bronze")

# --- Tests for DiscountService ---

@pytest.mark.asyncio
async def test_apply_brand_discount_only(brand_rule, generic_customer):
    """Test that only a brand discount is applied correctly."""
    cart = [CartItem(Product("1", "PUMA", BrandTier.PREMIUM, "Shoes", Decimal("1000.0"), Decimal("1000.0")), 2, "10")]
    service = DiscountService(rules=[brand_rule])
    result = await service.calculate_cart_discounts(cart, generic_customer)

    # 40% off 1000 is 400. Final price per item is 600. Total for 2 is 1200.
    assert result.final_price == Decimal("1200.00")
    assert "PUMA Brand Discount" in result.applied_discounts

@pytest.mark.asyncio
async def test_apply_brand_and_category_sequentially(brand_rule, category_rule, generic_customer):
    """Test that brand and category discounts are applied sequentially."""
    cart = [CartItem(Product("1", "PUMA", BrandTier.PREMIUM, "T-shirts", Decimal("1000.0"), Decimal("1000.0")), 1, "M")]
    service = DiscountService(rules=[brand_rule, category_rule])
    result = await service.calculate_cart_discounts(cart, generic_customer)

    # Initial: 1000. After 40% brand discount -> 600. After 10% category discount -> 540.
    assert result.final_price == Decimal("540.00")

@pytest.mark.asyncio
async def test_apply_voucher_discount(voucher_rule):
    """Test that a valid voucher code is applied."""
    cart = [CartItem(Product("1", "Generic", BrandTier.REGULAR, "Jeans", Decimal("2000.0"), Decimal("2000.0")), 1, "32")]
    customer = CustomerProfile(id="cust123", tier="gold", voucher_code="SUPER69")
    service = DiscountService(rules=[voucher_rule])
    result = await service.calculate_cart_discounts(cart, customer)

    # 69% off 2000 is 1380. Final price is 620.
    assert result.final_price == Decimal("620.00")
    assert "Voucher SUPER69" in result.applied_discounts

@pytest.mark.asyncio
async def test_no_discounts_applied(brand_rule, category_rule, voucher_rule, generic_customer):
    """Test that no discounts are applied for non-matching items."""
    cart = [CartItem(Product("1", "Nike", BrandTier.PREMIUM, "Socks", Decimal("500.0"), Decimal("500.0")), 3, "L")]
    service = DiscountService(rules=[brand_rule, category_rule, voucher_rule])
    result = await service.calculate_cart_discounts(cart, generic_customer)
    
    assert result.final_price == result.original_price
    assert not result.applied_discounts

@pytest.mark.asyncio
async def test_full_scenario_with_all_discounts(brand_rule, category_rule, bank_rule):
    """
    Test the full scenario from fake_data with brand, category, and bank discounts.
    """
    scenario = get_test_cart_scenario()
    cart = scenario["cart_items"]
    customer = scenario["customer"]
    payment = scenario["payment_info"]

    # The order of rules is critical for the final calculation
    service = DiscountService(rules=[brand_rule, category_rule, bank_rule])
    result = await service.calculate_cart_discounts(cart, customer, payment)

    # Calculation on a 1000.00 item:
    # 1. After 40% Brand Discount: 1000 * 0.6 = 600.00
    # 2. After 10% Category Discount: 600 * 0.9 = 540.00
    # 3. After 10% Bank Offer: 540 * 0.9 = 486.00
    assert result.final_price == pytest.approx(Decimal("486.00"))
    assert "PUMA Brand Discount" in result.applied_discounts
    assert "T-shirts Category Discount" in result.applied_discounts
    assert "ICICI Bank Offer" in result.applied_discounts
    