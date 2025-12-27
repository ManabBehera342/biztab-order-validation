import streamlit as st
import uuid
import time

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "selected_product" not in st.session_state:
    st.session_state.selected_product = None

# -------------------------------------------------
# BUSINESS RULE CONSTANTS
# -------------------------------------------------
MAX_ORDER_AMOUNT = 5000          # Risk mitigation threshold
MIN_ORDER_QUANTITY = 1           # MOQ
SERVICEABLE_ZONES = ["IN"]       # Mock delivery zone
PROCESSED_ORDERS = set()         # Prevent duplicate orders

# -------------------------------------------------
# MOCK PRODUCT CATALOG (Flipkart-style)
# -------------------------------------------------
PRODUCTS = {
    "P001": {
        "name": "Wireless Mouse",
        "price": 799,
        "stock": 15,
        "image": "https://cdn-icons-png.flaticon.com/512/2919/2919592.png",
        "description": "Ergonomic wireless mouse with adjustable DPI and long battery life."
    },
    "P002": {
        "name": "Mechanical Keyboard",
        "price": 2499,
        "stock": 5,
        "image": "https://cdn-icons-png.flaticon.com/512/2920/2920244.png",
        "description": "Compact mechanical keyboard with tactile switches and RGB backlight."
    },
    "P003": {
        "name": "USB-C Charger",
        "price": 999,
        "stock": 0,
        "image": "https://cdn-icons-png.flaticon.com/512/2910/2910768.png",
        "description": "Fast charging USB-C charger compatible with phones and laptops."
    },
    "P004": {
        "name": "Noise Cancelling Headphones",
        "price": 5999,
        "stock": 8,
        "image": "https://cdn-icons-png.flaticon.com/512/2921/2921822.png",
        "description": "Over-ear headphones with active noise cancellation and rich sound."
    },
    "P005": {
        "name": "Laptop Stand",
        "price": 1299,
        "stock": 20,
        "image": "https://cdn-icons-png.flaticon.com/512/2920/2920329.png",
        "description": "Adjustable aluminum laptop stand for better posture and airflow."
    }
}

# -------------------------------------------------
# BUSINESS LOGIC MODULES
# -------------------------------------------------
def validate_order(order):
    # 1. Order ID validation
    if not order["order_id"]:
        return False, "Invalid Order ID"

    # 2. Duplicate order check
    if order["order_id"] in PROCESSED_ORDERS:
        return False, "Duplicate order detected"

    # 3. Minimum Order Quantity (MOQ)
    if order["quantity"] < MIN_ORDER_QUANTITY:
        return False, "Order quantity below minimum threshold"

    # 4. High-value order risk check
    if order["total_amount"] > MAX_ORDER_AMOUNT:
        return False, "Order amount exceeds risk threshold"

    # 5. Delivery zone validation (mock)
    if order.get("delivery_zone", "IN") not in SERVICEABLE_ZONES:
        return False, "Delivery address not serviceable"

    return True, "Order validated successfully"


def check_inventory(order):
    product = PRODUCTS[order["product_id"]]
    if product["stock"] >= order["quantity"]:
        return True, f"Stock available ({product['stock']} units)"
    return False, "Out of stock"


def process_payment(total_amount):
    # MOCK PAYMENT GATEWAY
    if total_amount <= MAX_ORDER_AMOUNT:
        return True, "Payment successful"
    return False, "Payment failed due to risk threshold"


def fulfill_order(order):
    PRODUCTS[order["product_id"]]["stock"] -= order["quantity"]
    return "Order packed successfully"


def initiate_shipment():
    return f"TRK-{uuid.uuid4().hex[:8].upper()}"


def confirm_delivery():
    return "Order delivered successfully"


# -------------------------------------------------
# STREAMLIT UI
# -------------------------------------------------
st.set_page_config(page_title="Order-to-Delivery Demo", layout="centered")

st.title("🛒 Order-to-Delivery Business Flow Demo")
st.caption("Python + Streamlit | Flipkart-style Mock System")

st.divider()

# -------------------------------------------------
# PRODUCT CATALOG
# -------------------------------------------------
st.subheader("🛍️ Product Catalog")

cols = st.columns(3)
for idx, (pid, product) in enumerate(PRODUCTS.items()):
    with cols[idx % 3]:
        st.image(product["image"], width=120)
        st.markdown(f"**{product['name']}**")
        st.markdown(f"💰 ₹{product['price']}")
        st.markdown(
            f"📦 Stock: {product['stock']}"
            if product["stock"] > 0
            else "❌ Out of Stock"
        )

        if st.button("View Details", key=f"view_{pid}"):
            st.session_state.selected_product = pid

        st.markdown("---")

# -------------------------------------------------
# PRODUCT DETAILS (Flipkart-style)
# -------------------------------------------------
if st.session_state.selected_product:
    product = PRODUCTS[st.session_state.selected_product]

    st.divider()
    st.subheader("🧾 Product Details")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(product["image"], width=220)

    with col2:
        st.markdown(f"### {product['name']}")
        st.markdown(f"💰 **Price:** ₹{product['price']}")
        st.markdown(f"📦 **Stock Available:** {product['stock']}")
        st.markdown("📝 **Description:**")
        st.write(product["description"])

        if product["stock"] == 0:
            st.error("Currently out of stock")

# -------------------------------------------------
# ORDER PLACEMENT
# -------------------------------------------------
st.divider()
st.subheader("📝 Place Your Order")

order_id = f"ORD-{uuid.uuid4().hex[:6].upper()}"

product_id = st.selectbox(
    "Select Product",
    list(PRODUCTS.keys()),
    format_func=lambda x: f"{PRODUCTS[x]['name']} (₹{PRODUCTS[x]['price']})"
)

quantity = st.number_input("Quantity", min_value=1, step=1)

selected_product = PRODUCTS[product_id]
total_amount = selected_product["price"] * quantity

st.info(f"💳 Total Amount Payable: ₹{total_amount}")

# -------------------------------------------------
# ORDER PROCESSING FLOW
# -------------------------------------------------
if st.button("🚀 Submit Order"):
    order = {
        "order_id": order_id,
        "product_id": product_id,
        "quantity": quantity,
        "total_amount": total_amount,
        "delivery_zone": "IN"
    }

    st.divider()
    st.subheader("🔄 Order Processing Status")

    time.sleep(1)
    valid, msg = validate_order(order)
    if not valid:
        st.error(msg)
        st.stop()

    PROCESSED_ORDERS.add(order["order_id"])
    st.success(msg)

    time.sleep(1)
    stock_ok, msg = check_inventory(order)
    if not stock_ok:
        st.error(msg)
        st.stop()
    st.success(msg)

    time.sleep(1)
    payment_ok, msg = process_payment(total_amount)
    if not payment_ok:
        st.error(msg)
        st.stop()
    st.success(msg)

    time.sleep(1)
    st.success(fulfill_order(order))

    time.sleep(1)
    tracking_id = initiate_shipment()
    st.info(f"📦 Shipment Initiated | Tracking ID: {tracking_id}")

    time.sleep(1)
    st.success(confirm_delivery())

    st.balloons()
