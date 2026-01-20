import streamlit as st
import pandas as pd

from preprocess_data import process_data
from rating_based_recommendation import get_top_rated_items
from content_based_filtering import content_based_recommendation
from collaborative_based_filtering import collaborative_filtering_recommendations


# ------------------------------------------------------
# Session state init
# ------------------------------------------------------
if "recent_searches" not in st.session_state:
    st.session_state.recent_searches = []

if "refresh_sidebar" not in st.session_state:
    st.session_state.refresh_sidebar = False

if "typed_product" not in st.session_state:
    st.session_state.typed_product = ""

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "last_resolved_product" not in st.session_state:
    st.session_state.last_resolved_product = None


# ------------------------------------------------------
# Page config (UNCHANGED UI)
# ------------------------------------------------------
st.set_page_config(
    page_title="E-Commerce Products Recommender",
    page_icon="6795674-200.png",
    layout="wide"
)

# 🔥 UI THEME — UNCHANGED
st.markdown(""" 
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [data-testid="stApp"] {
    font-family: 'Inter', sans-serif !important;
    background: radial-gradient(
        1200px 600px at 20% -10%,
        #1e293b 0%,
        #020617 45%
    );
    color: #e5e7eb;
}

.block-container {
    padding-top: 2.2rem;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
}

h1 {
    font-size: 2.8rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

input, textarea {
    background-color: #020617 !important;
    border-radius: 10px !important;
    border: 1px solid #1e293b !important;
}

button {
    border-radius: 12px !important;
    font-weight: 600 !important;
}

section[data-testid="stSidebar"] {
    background: #020617;
    border-right: 1px solid #1e293b;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="margin-bottom: 2.5rem;">
    <h1>Algorithmic Recommendation System</h1>
    <p style="color:#94a3b8;font-size:1.05rem;max-width:720px;">
        Discover personalized product recommendations using intelligent
        content-based and collaborative filtering techniques.
    </p>
</div>
""", unsafe_allow_html=True)


# ------------------------------------------------------
# Load data
# ------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("clean_data.csv")
    return process_data(df)

data = load_data()


# ------------------------------------------------------
# Helper functions
# ------------------------------------------------------
def recommendation_reason(selected_user, typed_product):
    if typed_product:
        return "Recommended because it is similar to the searched product"
    elif selected_user == 0:
        return "Recommended because these are top-rated products"
    else:
        return "Recommended based on your activity and similar users"


def resolve_product_name(name, products):
    if not name:
        return None
    name = name.lower().strip()
    for p in products:
        if name in p.lower():
            return p
    return None


def get_user_recent_product(data, user_id):
    user_data = data[data["ID"] == user_id]
    if user_data.empty:
        return None
    return user_data.iloc[0]["Name"]


# ------------------------------------------------------
# Sidebar – Recent Searches
# ------------------------------------------------------
with st.sidebar:
    st.markdown("### Recent Searches")

    if not st.session_state.recent_searches:
        st.caption("No recent searches")
    else:
        for item in st.session_state.recent_searches:
            label = item[:45] + "…" if len(item) > 45 else item
            if st.button(label, key=item, help=item):
                st.session_state.typed_product = item
                st.rerun()

        if st.button("Clear History"):
            st.session_state.recent_searches = []
            st.session_state.last_result = None
            st.rerun()


# ------------------------------------------------------
# Inputs
# ------------------------------------------------------
col1, col2 = st.columns([3, 1])

with col1:
    typed_product = st.text_input(
        "Product Search",
        value=st.session_state.typed_product
    )

    selected_user = st.selectbox(
        "User ID (0 = New User)",
        [0] + sorted(data["ID"].unique())
    )

    top_n = st.radio("Top N", [5, 10, 20, 30], horizontal=True)
    run = st.button("Get Recommendations", use_container_width=True)


# ------------------------------------------------------
# Recommendation logic
# ------------------------------------------------------
if run:
    resolved_product = None

    if typed_product:
        resolved_product = resolve_product_name(
            typed_product, data["Name"].unique()
        )

        if resolved_product:
            if resolved_product in st.session_state.recent_searches:
                st.session_state.recent_searches.remove(resolved_product)

            st.session_state.recent_searches.insert(0, resolved_product)
            st.session_state.recent_searches = st.session_state.recent_searches[:6]

            result = content_based_recommendation(
                data, resolved_product, top_n
            )
        else:
            result = get_top_rated_items(data, top_n)

    elif selected_user == 0:
        result = get_top_rated_items(data, top_n)

    else:
        recent = get_user_recent_product(data, selected_user)
        if recent:
            cb = content_based_recommendation(data, recent, 5)
            cf = collaborative_filtering_recommendations(
                data, selected_user, top_n - 5
            )
            result = pd.concat([cb, cf]).drop_duplicates()
        else:
            result = get_top_rated_items(data, top_n)

    st.session_state.last_result = result
    st.session_state.last_resolved_product = resolved_product


# ------------------------------------------------------
# Display (PERSISTENT)
# ------------------------------------------------------
if st.session_state.last_result is not None:

    if st.session_state.last_resolved_product:
        st.success(
            f"Showing recommendations for: **{st.session_state.last_resolved_product}**"
        )

    st.subheader("Recommended Products")

    cols = st.columns(4)
    for i, (_, row) in enumerate(st.session_state.last_result.iterrows()):
        with cols[i % 4]:
            st.image(row["ImageURL"], use_container_width=True)
            st.markdown(f"**{row['Name']}**")
            st.caption(f"Brand: {row.get('Brand', 'N/A')}")
            st.caption(f"Rating: {round(row.get('Rating', 0), 2)}")

