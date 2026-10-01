import requests
import streamlit as st
import os


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000") #for checking the API base URL from environment variable, defaulting to localhost if not set

token = st.session_state.get("admin_token")

#display a warning and redirect to the admin access page if the admin token is not present in the session state
if not token:
    st.warning("Please enter your admin access token first.")
    if st.button("Go to Admin Access"):
        st.switch_page("pages/admin.py")
    st.stop()

heading, action = st.columns([5, 1], wrap=True)

with heading:
    st.title("Refund Requests")
    st.caption("Review complaints and their decision outcomes.")

with action:
    if st.button("Sign out"):
        st.session_state.pop("admin_token", None)
        st.switch_page("pages/admin.py")


@st.fragment(run_every="5s")
def show_live_requests():
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/admin/refunds",
            headers={"X-Admin-Token": token},
            timeout=10,
        )
    except requests.RequestException:
        st.error("Could not reach FastAPI.")
        st.stop()

    if response.status_code in (401, 403):
        st.session_state.pop("admin_token", None)
        st.error("Your access is no longer valid. Please sign in again.")
        st.stop()

    if response.status_code != 200:
        st.error(f"Could not load requests (HTTP {response.status_code}).")
        st.stop()

    requests_list = response.json().get("requests", [])

    statuses = ("Approved", "Denied", "Escalated")
    counts = {
        status: sum(
            request["decision"] == status
            for request in requests_list
        )
        for status in statuses
    }

    metric_columns = st.columns(4, wrap=True)
    metric_columns[0].metric("Total", len(requests_list), border=True)
    metric_columns[1].metric("Approved", counts["Approved"], border=True)
    metric_columns[2].metric("Denied", counts["Denied"], border=True)
    metric_columns[3].metric("Escalated", counts["Escalated"], border=True)

    selected_status = st.selectbox(
        "Filter requests",
        ["All", "Approved", "Denied", "Escalated"],
    )

    visible_requests = [
        request for request in requests_list
        if selected_status == "All"
        or request["decision"] == selected_status
    ]

    if not visible_requests:
        st.info("No requests to show.")

    for request in visible_requests:
        with st.container(border=True):
            details, status = st.columns([4, 1], wrap=True)

            with details:
                st.subheader(
                    f"{request['customer_name']} · {request['order_id']}"
                )
                st.caption(
                    f"{request['email']} · {request['item']} "
                    f"· ${request['amount']:,.2f}"
                )

            with status:
                badge_color = {
                    "Approved": "green",
                    "Denied": "red",
                    "Escalated": "orange",
                }.get(request["decision"], "gray")

                st.badge(request["decision"], color=badge_color)

            st.write(f"**Complaint:** {request['message']}")
            st.write(f"**AI category:** {request['issue']}")
            st.write(f"**Decision reason:** {request['reason']}")
            st.caption(f"Request ID: {request['request_id']}")


show_live_requests()