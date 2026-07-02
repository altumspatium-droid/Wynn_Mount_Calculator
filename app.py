import streamlit as st
from calculator import calculate_feeding, calculate_num_needed

st.set_page_config(
    page_title="Mount Feeding Calculator",
    page_icon="🐎",
    layout="wide",
)

# -----------------------
# Header Elements Side-by-Side
# -----------------------
# Allocate a wide column for the title text and a narrower one for the action button
header_col, button_col = st.columns([4, 1])

with header_col:
    # Using markdown to remove native h1 padding/margins so it aligns perfectly with the button
    st.markdown("<h1 style='margin:0; padding:0;'>🐎 Mount Feeding Calculator</h1>", unsafe_html=True)
    st.write("Find the optimal feeding strategy for your mount.")

with button_col:
    # Injecting empty space pushes the button down slightly to align with the text line baseline
    st.write("##") 
    max_allowed_level = st.selectbox(
    "What is the maximum item level you can use?",
    options=[115, 110, 105, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 1],
    help="The solver will not use any materials higher than this level, even if the mount's stats would normally allow it."
)

st.divider()

# -----------------------
# Limits
# -----------------------

st.subheader("Limits")

stat_names = [
    "Speed",
    "Acceleration",
    "Altitude",
    "Energy",
    "Handling",
    "Toughness",
    "Boost",
    "Training",
]


limits = []

cols = st.columns(8)

for i, col in enumerate(cols):
    with col:
        st.caption(stat_names[i])  # shows the stat name above the input
        limits.append(
            st.number_input(
                label=f"Limit {i+1}",
                value=1,
                min_value=1,
                max_value=9999,
                step=1,
                label_visibility="collapsed",
            )
        )

# -----------------------
# Maxes
# -----------------------

st.subheader("Maximum Values")

maxes = []

cols = st.columns(8)

for i, col in enumerate(cols):
    with col:
        st.caption(stat_names[i])  # shows the stat name above the input
        maxes.append(
            st.number_input(
                label=stat_names[i],
                value=30,
                min_value=1,
                max_value=9999,
                step=1,
                label_visibility="collapsed",
            )
        )

st.write("")

# -----------------------
# Calculate
# -----------------------

if st.button("Calculate Feeding Advice", type="primary"):

    with st.spinner("Generating ideal solution..."):

        try:
            limits2, maxes2 = limits.copy(), maxes.copy()
            result = calculate_feeding(limits, maxes)

            st.subheader("Results")

            number_needed = calculate_num_needed(limits2, maxes2)
            st.write(
                "Number of items needed to fully level your mount:", number_needed
            )

            st.table(result)

        except Exception as e:
            st.error(f"Calculation failed:\n\n{e}")
