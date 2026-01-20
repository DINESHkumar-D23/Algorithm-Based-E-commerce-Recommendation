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

if "typed_product" not in st.session_state:
    st.session_state.typed_product = ""


# ------------------------------------------------------
# Page config
# ------------------------------------------------------
st.set_page_config(
    page_title="AI E-Commerce Recommender",
    page_icon="6795674-200.png",
    layout="wide"
)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ------------------ Global ------------------ */
html, body, [data-testid="stApp"] {
    font-family: 'Inter', sans-serif !important;
    background: radial-gradient(
        1200px 600px at 20% -10%,
        #1e293b 0%,
        #020617 45%
    );
    color: #e5e7eb;
}

/* Remove Streamlit default padding */
.block-container {
    padding-top: 2.2rem;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
}

/* ------------------ Headings ------------------ */
h1 {
    font-size: 2.8rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}

h2 {
    font-size: 1.8rem !important;
    font-weight: 700 !important;
}

h3 {
    font-size: 1.2rem !important;
    font-weight: 600 !important;
    color: #cbd5f5;
}

/* ------------------ Inputs ------------------ */
input, textarea {
    background-color: #020617 !important;
    border-radius: 10px !important;
    border: 1px solid #1e293b !important;
}

/* ------------------ Buttons ------------------ */
button {
    border-radius: 12px !important;
    font-weight: 600 !important;
}

button:hover {
    transform: translateY(-1px);
}

/* ------------------ Sidebar ------------------ */
section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #020617,
        #020617
    );
    border-right: 1px solid #1e293b;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
    margin-bottom: 2.5rem;
">
    <h1>AI-Powered Recommendation System</h1>
    <p style="
        color:#94a3b8;
        font-size:1.05rem;
        max-width:720px;
        line-height:1.6;
    ">
        Discover personalized product recommendations using intelligent
        content-based, collaborative, and hybrid filtering techniques.
    </p>
</div>
""", unsafe_allow_html=True)


# ------------------------------------------------------
# Load & preprocess data
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


def resolve_product_name(typed_name, product_list):
    if not typed_name:
        return None
    typed_name = typed_name.lower().strip()
    matches = [p for p in product_list if typed_name in p.lower()]
    return matches[0] if matches else None


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
            display_text = (
                item[:45] + "…" if len(item) > 45 else item
            )

            if st.button(
                display_text,
                key=f"recent_{item}",
                help=item   # tooltip shows full text
            ):
                st.session_state.typed_product = item
                st.rerun()

        if st.button("Clear History"):
            st.session_state.recent_searches = []
            st.rerun()


# ------------------------------------------------------
# Inputs
# ------------------------------------------------------
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Product Search (optional)")
    typed_product = st.text_input(
        "Type product name",
        value=st.session_state.typed_product,
        placeholder="e.g. iPhone, shoes, laptop..."
    )

    st.subheader("User Input")
    user_ids = [0] + sorted(data["ID"].unique())
    selected_user = st.selectbox(
        "Select user ID (0 = New User)",
        user_ids
    )

    top_n = st.radio(
        "Number of recommendations",
        [5, 10, 20, 30],
        horizontal=True
    )

    run = st.button("Get Recommendations", use_container_width=True)

with col2:
    st.markdown("""
<style>
.How {
    background: #020617;
    padding: 1.5rem;
    border-radius: 12px;
    border: 1px solid #1e293b;
    margin-top: 2.2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    transition: box-shadow 0.35s ease, transform 0.35s ease;
}
.How:hover {
    box-shadow: 0 18px 55px rgba(15,23,42,0.9),
                0 0 30px rgba(56,189,248,0.9);
    transform: translateY(-4px);
}
</style>

<div class="How">
    <h4 style="color:white;">How it works</h4>
    <p style="color:#94a3b8;font-size:0.9rem;">
        This system handles new users using top-rated products,
        personalizes for existing users using content-based and
        collaborative filtering, and prioritizes product search
        when provided.
    </p>
</div>
""", unsafe_allow_html=True)


# ------------------------------------------------------
# Recommendation logic
# ------------------------------------------------------
if run:
    resolved_product = None

    with st.spinner("Generating recommendations..."):

        # CASE 3: Product search (highest priority)
        if typed_product:
            resolved_product = resolve_product_name(
                typed_product, data["Name"].unique()
            )

            if not resolved_product:
                st.warning("Invalid product name. Showing top-rated items.")
                result = get_top_rated_items(data, top_n)
            else:
                # Save to recent searches
                # Save to recent searches
                if resolved_product in st.session_state.recent_searches:
                    st.session_state.recent_searches.remove(resolved_product)

                st.session_state.recent_searches.insert(0, resolved_product)
                st.session_state.recent_searches = st.session_state.recent_searches[:6]

                st.session_state.typed_product = resolved_product

                st.rerun()   



                result = content_based_recommendation(
                    data, resolved_product, top_n
                )
                st.write("DEBUG recent:", st.session_state.recent_searches)


        # CASE 1: New user
        elif selected_user == 0:
            result = get_top_rated_items(data, top_n)

        # CASE 2: Existing user
        else:
            recent_product = get_user_recent_product(data, selected_user)

            if recent_product:
                content_results = content_based_recommendation(
                    data, recent_product, 5
                )

                collaborative_results = collaborative_filtering_recommendations(
                    data, selected_user, top_n - 5
                )

                result = pd.concat(
                    [content_results, collaborative_results]
                ).drop_duplicates().head(top_n)
            else:
                result = get_top_rated_items(data, top_n)

    # --------------------------------------------------
    # Display results
    # --------------------------------------------------
    if resolved_product:
        st.success(f"Showing recommendations for: **{resolved_product}**")

    st.subheader("Recommended Products")

    cols = st.columns(4)
    for idx, (_, row) in enumerate(result.iterrows()):
        with cols[idx % 4]:
            if isinstance(row.get("ImageURL"), str):
                st.image(row["ImageURL"], use_container_width=True)

            st.markdown(f"**{row['Name']}**")
            st.caption(f"Brand: {row.get('Brand', 'N/A')}")
            st.caption(f"Rating: {round(row.get('Rating', 0), 2)}")
            st.caption(recommendation_reason(selected_user, typed_product))
