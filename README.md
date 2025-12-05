# ecom-discount-engine

Module for handling and applying discounts on products based on specific parameters.

## Features

- **Brand-specific discounts**: Apply discounts based on product brands (e.g., "Min 40% off on PUMA")
- **Category-specific deals**: Apply additional discounts on specific categories (e.g., "Extra 10% off on T-shirts")
- **Bank card offers**: Apply instant discounts based on payment method (e.g., "10% instant discount on ICICI Bank cards")
- **Vouchers**: Apply voucher codes for additional discounts (e.g., 'SUPER69' for 69% off)

## Architecture: A Rule-Based Engine

This project uses a flexible rule-based engine. The order of discount application is not fixed; it is determined by the order in which discount rules are passed to the `DiscountService` during initialization. This allows for dynamic and configurable discount strategies.

For example, to apply brand discounts before voucher discounts:
service = DiscountService(rules=[
    BrandDiscountRule(...),
    VoucherDiscountRule(...)
])

## Getting Started

To get started with development, create a virtual environment and install the project in editable mode.

### Prerequisites

- Python 3.8+

### Installation

1.  **Clone the repository:**
    git clone https://github.com/mizunus/ecom-discount-engine.git
    cd ecom-discount-engine

2.  **Create and activate a virtual environment:**
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

3.  **Install the project in editable mode with development dependencies:**
    pip install -e .[dev]
        This installs the project along with the testing libraries defined in `pyproject.toml`.

## Usage

The following example demonstrates how to set up and use the `DiscountService`.

python```
import asyncio
from decimal import Decimal

# 1. Import necessary classes
from src.models import CartItem, CustomerProfile, PaymentInfo, Product, BrandTier
from src.services import DiscountService
from src.rules import BrandDiscountRule, CategoryDiscountRule, BankOfferRule

# 2. Define discount configurations
# In a real app, this would come from a database or config file
brand_discounts = {"PUMA": Decimal("40.0")}
category_discounts = {"T-shirts": Decimal("10.0")}
bank_offers = {"ICICI": Decimal("10.0")}

# 3. Create rule instances in the desired order of application
rules = [
    BrandDiscountRule(brand_discounts),
    CategoryDiscountRule(category_discounts),
    BankOfferRule(bank_offers),
]

# 4. Initialize the DiscountService
service = DiscountService(rules=rules)

# 5. Set up a scenario to test
product = Product(
    id="prod_001", brand="PUMA", brand_tier=BrandTier.PREMIUM,
    category="T-shirts", base_price=Decimal("1000.00"),
    current_price=Decimal("1000.00"),
)
cart_items = [CartItem(product=product, quantity=1, size="M")]
customer = CustomerProfile(id="cust_001", tier="regular")
payment_info = PaymentInfo(method="CARD", bank_name="ICICI", card_type="CREDIT")

# 6. Run the async calculation and get the result
# This line can be run directly in a Python 3.7+ shell
result = asyncio.run(service.calculate_cart_discounts(
    cart_items=cart_items,
    customer=customer,
    payment_info=payment_info,
))

# 7. Print the results
print(f"Original Price: ₹{result.original_price}")
print(f"Final Price: ₹{result.final_price}")
print(result.message)
```

## Running Tests
After installing the project with the `[dev]` dependencies, you can run the tests:
```bash
pytest
```

## Project Structure

```
ecom-discount-engine/
├── src/
│   ├── models.py       # Data models (Product, CartItem, etc.)
│   ├── services.py     # The core discount rule engine
│   ├── rules.py        # Individual discount rule implementations
│   └── fake_data.py    # Scenarios for testing
├── tests/
│   ├── test_services.py  # Integration tests for the service
│   └── test_rules.py     # Unit tests for individual rules
└── pyproject.toml      # Project configuration and dependencies
```
