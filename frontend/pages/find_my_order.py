import requests
import streamlit as st

import os
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")  #for checking the API base URL from environment variable, defaulting to localhost if not set

# Styles for this form only
st.html("""
<style>
.st-key-find_order_form,
.st-key-find_order_form [data-testid="stForm"] {
    border-radius: 8px !important;
}

.st-key-find_order_form div[data-baseweb="input"] {
    border-radius: 5px !important;
    border: 1px solid #cbd5e1;
    background-color: #f8fafc;
}

.st-key-find_order_form input {
    font-size: 16px;
    padding: 12px 14px;
    box-sizing: border-box;
    max-width: 100%;
}

.st-key-find_order_form label {
    font-weight: 600;
}

/* Desktop spacing and instruction */
.lookup-top-space {
    height: 100px;
}

.order-instruction {
    font-size: 18px;
    font-weight: 600;
    line-height: 1.4;
}

.order-line {
    height: 1px;
    width: 100%;
    background-color: #64748b;
    margin: 4px 0 12px;
}

/* Changes applied on phone-sized screens */
@media (max-width: 640px) {
    .lookup-top-space {
        height: 24px;
    }

    .order-instruction {
        font-size: 16px;
    }

    .st-key-find_order_form input {
        padding: 10px 12px;
    }
}
</style>
""")

st.html('<div class="lookup-top-space"></div>')

left, middle, right = st.columns([1, 7, 1], wrap=True)

with middle:
    with st.form(key="find_order_form"):
        st.title("Find My Order", text_alignment="center")

        # Horizontal line and sentence above the form fields
        st.html("""
<div class="order-instruction">
    Enter your Email and Order ID.
</div>
<div class="order-line"></div>
""")

        email = st.text_input(
            "Email",
            placeholder="Enter your email address"
        )
        order_id = st.text_input(
            "Order ID",
            placeholder="Enter your order ID"
        )
        submit_button = st.form_submit_button("Find Order")

    if submit_button:
        st.session_state.pop("found_order", None)
        st.session_state.pop("verified_email", None)
        st.session_state.pop("refund_response", None)

        if not email.strip() or not order_id.strip():
            st.error("Please enter both email and order ID.")
        else:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/api/orders/lookup", 
                    json={
                        "email": email.strip(),
                        "order_id": order_id.strip(),
                    },
                    timeout=10,
                )

                if response.status_code == 200:
                    st.session_state["found_order"] = response.json()
                    st.session_state["verified_email"] = email.strip()
                elif response.status_code == 404:
                    st.error("No order matches that email and order ID.")
                else:
                    st.error(f"Order lookup failed: {response.status_code}")

            except requests.RequestException:
                st.error("Could not reach the backend. Check that FastAPI is running.")

    if "found_order" in st.session_state:
        order = st.session_state["found_order"]

        with st.container(border=True):
            st.subheader(order["item"])
            st.write(f"**Order ID:** {order['order_id']}")
            st.write(f"**Amount:** ${order['amount']:,.2f}")
            st.write(f"**Purchase date:** {order['purchase_date']}")

        if st.button("Report an issue", type="primary"):
            st.switch_page("pages/complaint.py")