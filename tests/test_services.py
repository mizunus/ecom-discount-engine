"""
Unit tests for the discount service.
"""

import pytest
from decimal import Decimal
from src.services import DiscountService
from src.fake_data import get_test_cart_scenario, get_test_voucher_scenario
from src.models import CartItem, CustomerProfile, PaymentInfo, Product, BrandTier


class TestDiscountService:
    """Test cases for DiscountService."""

    @pytest.fixture
    def service(self):
        """Create a DiscountService instance for testing."""
        return DiscountService()

    @pytest.mark.asyncio
    async def test_multiple_discount_scenario(self, service):
        """
        Test the multiple discount scenario:
        - PUMA T-shirt with "Min 40% off"
        - Additional 10% off on T-shirts category
        - ICICI bank offer of 10% instant discount
        
        Expected calculation:
        - Base price: ₹1000
        - After 40% brand discount: ₹1000 - ₹400 = ₹600
        - After 10% category discount: ₹600 - ₹60 = ₹540
        - After 10% bank discount: ₹540 - ₹54 = ₹486
        - Final price: ₹486
        """
        test_data = get_test_cart_scenario()
        result = await service.calculate_cart_discounts(
            cart_items=test_data["cart_items"],
            customer=test_data["customer"],
            payment_info=test_data["payment_info"],
        )

        # Verify original price
        assert result.original_price == Decimal("1000.00")

        # Verify final price calculation
        expected_final_price = Decimal("486.00")  # 1000 * 0.6 * 0.9 * 0.9 = 486
        assert result.final_price == expected_final_price

        # Verify discount amounts
        assert "PUMA Brand Discount" in result.applied_discounts
        assert result.applied_discounts["PUMA Brand Discount"] == Decimal("400.00")

        assert "T-shirts Category Discount" in result.applied_discounts
        assert result.applied_discounts["T-shirts Category Discount"] == Decimal("60.00")

        assert "ICICI Bank Offer" in result.applied_discounts
        assert result.applied_discounts["ICICI Bank Offer"] == Decimal("54.00")

        # Verify total discount
        total_discount = sum(result.applied_discounts.values())
        expected_total_discount = Decimal("514.00")  # 400 + 60 + 54
        assert total_discount == expected_total_discount

        # Verify message contains discount information
        assert "Applied discounts:" in result.message
        assert "PUMA Brand Discount" in result.message

    @pytest.mark.asyncio
    async def test_discount_order(self, service):
        """
        Test that discounts are applied in the correct order:
        1. Brand/Category discounts first
        2. Then voucher codes
        3. Then bank offers
        """
        # Create a product with all discount types
        product = Product(
            id="prod_test",
            brand="PUMA",
            brand_tier=BrandTier.PREMIUM,
            category="T-shirts",
            base_price=Decimal("1000.00"),
            current_price=Decimal("1000.00"),
        )

        cart_item = CartItem(product=product, quantity=1, size="M")

        customer = CustomerProfile(
            id="cust_test",
            tier="regular",
            voucher_code="SUPER69",
        )

        payment_info = PaymentInfo(
            method="CARD",
            bank_name="ICICI",
            card_type="CREDIT",
        )

        result = await service.calculate_cart_discounts(
            cart_items=[cart_item],
            customer=customer,
            payment_info=payment_info,
        )

        # Calculate expected price with correct order:
        # Base: 1000
        # After 40% brand: 600
        # After 10% category: 540
        # After 69% voucher: 540 * 0.31 = 167.40
        # After 10% bank: 167.40 * 0.9 = 150.66
        expected_final_price = Decimal("150.66")
        assert abs(result.final_price - expected_final_price) < Decimal("0.01")

        # Verify all discounts are applied
        assert "PUMA Brand Discount" in result.applied_discounts
        assert "T-shirts Category Discount" in result.applied_discounts
        assert "Voucher SUPER69" in result.applied_discounts
        assert "ICICI Bank Offer" in result.applied_discounts

    @pytest.mark.asyncio
    async def test_voucher_validation(self, service):
        """Test voucher code validation."""
        product = Product(
            id="prod_test",
            brand="PUMA",
            brand_tier=BrandTier.PREMIUM,
            category="T-shirts",
            base_price=Decimal("1000.00"),
            current_price=Decimal("1000.00"),
        )

        cart_item = CartItem(product=product, quantity=1, size="M")

        customer = CustomerProfile(
            id="cust_test",
            tier="regular",
            voucher_code="SUPER69",
        )

        # Valid voucher should return True
        is_valid = await service.validate_discount_code(
            code="SUPER69",
            cart_items=[cart_item],
            customer=customer,
        )
        assert is_valid is True

        # Invalid voucher should return False
        is_valid = await service.validate_discount_code(
            code="INVALID_CODE",
            cart_items=[cart_item],
            customer=customer,
        )
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_brand_exclusion_validation(self, service):
        """Test voucher validation with brand exclusions."""
        # Add a brand exclusion for testing
        service.VOUCHER_BRAND_EXCLUSIONS["SUPER69"] = ["NIKE"]

        product = Product(
            id="prod_test",
            brand="NIKE",  # Excluded brand
            brand_tier=BrandTier.PREMIUM,
            category="T-shirts",
            base_price=Decimal("1000.00"),
            current_price=Decimal("1000.00"),
        )

        cart_item = CartItem(product=product, quantity=1, size="M")

        customer = CustomerProfile(
            id="cust_test",
            tier="regular",
            voucher_code="SUPER69",
        )

        # Should return False due to brand exclusion
        is_valid = await service.validate_discount_code(
            code="SUPER69",
            cart_items=[cart_item],
            customer=customer,
        )
        assert is_valid is False

        # Reset exclusions
        if "SUPER69" in service.VOUCHER_BRAND_EXCLUSIONS:
            del service.VOUCHER_BRAND_EXCLUSIONS["SUPER69"]

    @pytest.mark.asyncio
    async def test_tier_requirement_validation(self, service):
        """Test voucher validation with tier requirements."""
        # Add a tier requirement for testing
        service.VOUCHER_TIER_REQUIREMENTS["SUPER69"] = "gold"

        product = Product(
            id="prod_test",
            brand="PUMA",
            brand_tier=BrandTier.PREMIUM,
            category="T-shirts",
            base_price=Decimal("1000.00"),
            current_price=Decimal("1000.00"),
        )

        cart_item = CartItem(product=product, quantity=1, size="M")

        # Regular tier customer should not be able to use gold tier voucher
        customer_regular = CustomerProfile(
            id="cust_test",
            tier="regular",
            voucher_code="SUPER69",
        )

        is_valid = await service.validate_discount_code(
            code="SUPER69",
            cart_items=[cart_item],
            customer=customer_regular,
        )
        assert is_valid is False

        # Gold tier customer should be able to use it
        customer_gold = CustomerProfile(
            id="cust_test",
            tier="gold",
            voucher_code="SUPER69",
        )

        is_valid = await service.validate_discount_code(
            code="SUPER69",
            cart_items=[cart_item],
            customer=customer_gold,
        )
        assert is_valid is True

        # Reset requirements
        if "SUPER69" in service.VOUCHER_TIER_REQUIREMENTS:
            del service.VOUCHER_TIER_REQUIREMENTS["SUPER69"]

    @pytest.mark.asyncio
    async def test_multiple_quantity(self, service):
        """Test discount calculation with multiple quantities."""
        test_data = get_test_cart_scenario()
        cart_item = test_data["cart_items"][0]
        cart_item.quantity = 2  # 2 items

        result = await service.calculate_cart_discounts(
            cart_items=[cart_item],
            customer=test_data["customer"],
            payment_info=test_data["payment_info"],
        )

        # Original price should be doubled
        assert result.original_price == Decimal("2000.00")

        # Final price should be doubled
        assert result.final_price == Decimal("972.00")  # 486 * 2

        # Discounts should be doubled
        assert result.applied_discounts["PUMA Brand Discount"] == Decimal("800.00")
        assert result.applied_discounts["T-shirts Category Discount"] == Decimal("120.00")
        assert result.applied_discounts["ICICI Bank Offer"] == Decimal("108.00")

    @pytest.mark.asyncio
    async def test_no_discounts(self, service):
        """Test calculation with no applicable discounts."""
        product = Product(
            id="prod_test",
            brand="UNKNOWN_BRAND",
            brand_tier=BrandTier.REGULAR,
            category="Unknown Category",
            base_price=Decimal("1000.00"),
            current_price=Decimal("1000.00"),
        )

        cart_item = CartItem(product=product, quantity=1, size="M")

        customer = CustomerProfile(
            id="cust_test",
            tier="regular",
            voucher_code=None,
        )

        payment_info = PaymentInfo(
            method="UPI",
            bank_name=None,
            card_type=None,
        )

        result = await service.calculate_cart_discounts(
            cart_items=[cart_item],
            customer=customer,
            payment_info=payment_info,
        )

        assert result.original_price == Decimal("1000.00")
        assert result.final_price == Decimal("1000.00")
        assert len(result.applied_discounts) == 0
        assert "No discounts applied" in result.message

    @pytest.mark.asyncio
    async def test_voucher_scenario(self, service):
        """Test scenario with voucher code only."""
        test_data = get_test_voucher_scenario()
        result = await service.calculate_cart_discounts(
            cart_items=test_data["cart_items"],
            customer=test_data["customer"],
            payment_info=test_data["payment_info"],
        )

        # With voucher code SUPER69 (69% off), starting from 1000
        # After brand discount 40%: 600
        # After category discount 10%: 540
        # After voucher 69%: 540 * 0.31 = 167.40
        # No bank discount (HDFC not in offers)
        expected_final_price = Decimal("167.40")
        assert abs(result.final_price - expected_final_price) < Decimal("0.01")

        # Verify voucher discount is applied
        assert "Voucher SUPER69" in result.applied_discounts

