import requests
import streamlit as st
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")  #for checking the API base URL from environment variable, defaulting to localhost if not set

st.title("Admin Access", text_alignment="center")

left, middle, right = st.columns([1, 4, 1], wrap=True)

with middle:
    with st.form("admin_access_form"):
        st.write("Enter your access token to review refund requests.")

        token = st.text_input(
            "Access token",
            type="password",
            placeholder="Enter admin token",
        )

        submitted = st.form_submit_button(
            "Open Dashboard",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        st.session_state.pop("admin_token", None)

        if not token.strip():
            st.error("Enter your access token.")
        else:
            try:
                response = requests.get(
                    f"{API_BASE_URL}/api/admin/refunds",
                    headers={"X-Admin-Token": token.strip()},
                    timeout=10,
                )

                if response.status_code == 200:
                    st.session_state["admin_token"] = token.strip()
                    st.switch_page("pages/admin_dashboard.py")
                elif response.status_code in (401, 403):
                    st.error("Incorrect access token.")
                else:
                    st.error(f"Access check failed (HTTP {response.status_code}).")

            except requests.RequestException:
                st.error("Could not reach FastAPI. Check that the backend is running.")