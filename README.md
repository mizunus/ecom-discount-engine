# ecom-discount-engine

Module for handling and applying discounts on products based on specific parameters.

## Features

- **Brand-specific discounts**: Apply discounts based on product brands (e.g., "Min 40% off on PUMA")
- **Category-specific deals**: Apply additional discounts on specific categories (e.g., "Extra 10% off on T-shirts")
- **Bank card offers**: Apply instant discounts based on payment method (e.g., "10% instant discount on ICICI Bank cards")
- **Vouchers**: Apply voucher codes for additional discounts (e.g., 'SUPER69' for 69% off)

## Discount Application Order

Discounts are applied in the following sequential order:
1. Brand/Category discounts
2. Voucher codes
3. Bank offers

## Getting Started

To get started with development, create a virtual environment and install the project in editable mode.

### Prerequisites

- Python 3.8+

### Installation

1.  **Clone the repository:**
    git clone https://github.com/mizunus/ecom-discount-engine.git # Replace with your repo URL
    cd ecom-discount-engine

2.  **Create and activate a virtual environment:**
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

3.  **Install the project in editable mode with development dependencies:**
    pip install -e .[dev]
        This installs the project along with the testing libraries defined in `pyproject.toml`.

## Usage

```python
from src.services import DiscountService
from src.fake_data import get_test_cart_scenario

# Get test data
test_data = get_test_cart_scenario()

# Create service instance
service = DiscountService()

# Calculate discounts
result = await service.calculate_cart_discounts(
    cart_items=test_data["cart_items"],
    customer=test_data["customer"],
    payment_info=test_data["payment_info"],
)

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
│   ├── services.py     # DiscountService implementation
│   └── fake_data.py    # Test data
├── tests/
│   └── test_services.py  # Unit tests
└── pyproject.toml      # Project configuration and dependencies
```
