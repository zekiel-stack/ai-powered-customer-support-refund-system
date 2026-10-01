import streamlit as st
import requests
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")  #for checking the API base URL from environment variable, defaulting to localhost if not set

order = st.session_state.get("found_order")
email = st.session_state.get("verified_email")

if not order or not email:
    st.warning("Please find your order first.")
    if st.button("Find My Order"):
        st.switch_page("pages/find_my_order.py")
    st.stop()

# Styles for this page and form
st.html("""
<style>
.complaint-top-space {
    height: 100px;
}

.st-key-complaint_form,
.st-key-complaint_form [data-testid="stForm"] {
    border-radius: 8px !important;
}

.st-key-complaint_form div[data-baseweb="textarea"] {
    border-radius: 5px !important;
    border: 1px solid #cbd5e1;
    background-color: #f8fafc;
}

.st-key-complaint_form textarea {
    font-size: 16px;
    padding: 12px 14px;
    box-sizing: border-box;
}

.st-key-complaint_form label {
    font-weight: 600;
}

.complaint-instruction {
    font-size: 18px;
    font-weight: 600;
}

.complaint-line {
    height: 1px;
    background-color: #64748b;
    margin: 4px 0 12px;
}

@media (max-width: 640px) {
    .complaint-top-space {
        height: 24px;
    }

    .complaint-instruction {
        font-size: 16px;
    }
}
</style>
""")

st.html('<div class="complaint-top-space"></div>')

left, middle, right = st.columns([1, 7, 1], wrap=True)

with middle:
    st.title("Report an Issue", text_alignment="center")

    with st.container(border=True):
        st.subheader(order["item"])
        st.write(f"**Order ID:** {order['order_id']}")
        st.write(f"**Amount:** ${order['amount']:,.2f}")
        st.write(f"**Purchase date:** {order['purchase_date']}")

    
        result = st.session_state.get("refund_response")

    if result and result.get("order_id") == order["order_id"]:
        with st.container(border=True):
            decision = result["decision"]

            if decision == "Approved":
                st.success("Your request qualifies for a refund.")
            elif decision == "Denied":
                st.error("This request does not qualify for a refund.")
            else:
                st.warning("Your request has been sent to support for review.")

            st.write(f"**Reason:** {result['reason']}")
            st.caption(f"Request ID: {result['request_id']}")

    else:
        with st.form(key="complaint_form"):
            st.html("""
<div class="complaint-instruction">
    Tell us what went wrong with this order.
</div>
<div class="complaint-line"></div>
""")

            description = st.text_area(
                "Describe the issue",
                placeholder="For example: My headphones arrived broken and won't turn on.",
                height=150,
                max_chars=1000,
            )

            submitted = st.form_submit_button(
                "Submit Complaint",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            message = description.strip()

            if len(message) < 10:
                st.error("Please describe the issue in at least 10 characters.")
            else:
                try:
                    with st.spinner("Reviewing your request..."):
                        response = requests.post(
                            f"{API_BASE_URL}/api/refunds",
                            json={
                                "email": email,
                                "order_id": order["order_id"],
                                "message": message,
                            },
                            timeout=60,
                        )

                    if response.ok:
                        st.session_state["refund_response"] = response.json()
                        st.rerun()
                    elif response.status_code == 404:
                        st.error("That order and email could not be verified.")
                    elif response.status_code == 422:
                        st.error("Please enter a description between 10 and 1000 characters.")
                    else:
                        st.error(
                            f"Submission failed (HTTP {response.status_code}). "
                            "Check the FastAPI terminal."
                        )

                except requests.RequestException:
                    st.error("Could not reach FastAPI. Check that the backend is running.")