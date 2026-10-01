import streamlit as st


def home():
    st.html("""
    <style>
    .home-top-space { height: 80px; }

    .st-key-customer_card,
    .st-key-admin_card {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
 }

@media (hover: hover) {
    .st-key-customer_card:hover,
    .st-key-admin_card:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.14);
    }
    }

    @media (max-width: 640px) {
        .home-top-space { height: 24px; }
    }
    </style>
    """) 

    st.html('<div class="home-top-space"></div>')

    left, middle, right = st.columns([1, 10, 1], wrap=True)

    with middle:
        st.title("Worknoon Refund Support", text_alignment="center")
        st.caption(
            "Find your order to request a refund, or review customer requests.",
            text_alignment="center",
        )

        customer_col, admin_col = st.columns(2, gap="large", wrap=True)

        with customer_col:
           with st.container(border=True, key="customer_card"):
    # Customer card content
                st.subheader("Customer")
                st.write("Look up your order and tell us what went wrong.")

                if st.button("Find My Order", use_container_width=True):
                    st.switch_page("pages/find_my_order.py")

        with admin_col:
            with st.container(border=True, key="admin_card"):
    # Admin card content
                st.subheader("Admin")
                st.write("Review submitted refund requests.")

                if st.button("Open Admin", use_container_width=True):
                    st.switch_page("pages/admin.py")

#page definitions
home_page = st.Page(home, title="Home", default=True)
find_order_page = st.Page("pages/find_my_order.py", title="Find My Order")
complaint_page = st.Page(
    "pages/complaint.py",
    title="Report an Issue",
    visibility="hidden",
)
admin_page = st.Page("pages/admin.py", title="Admin")


admin_dashboard_page = st.Page(
    "pages/admin_dashboard.py",
    title="Admin Dashboard",
    visibility="hidden",
)


st.navigation(
    [home_page, find_order_page, complaint_page, admin_page, admin_dashboard_page],
    position="top",
).run()