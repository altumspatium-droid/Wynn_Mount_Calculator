import streamlit as st
from calculator import calculate_feeding

st.set_page_config(
    page_title="Mount Feeding Calculator",
    page_icon="🐎",
    layout="wide",
)

st.title("🐎 Mount Feeding Calculator")
st.write("Find the optimal feeding strategy for your mount.")

st.divider()

# -----------------------
# Limits
# -----------------------

st.subheader("Limits")

limits = []

cols = st.columns(8)

for i, col in enumerate(cols):
    with col:
        limits.append(
            st.number_input(
                label=f"Limit {i+1}",
                value=1,
                min_value=0,
                max_value=30,
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
        maxes.append(
            st.number_input(
                label=f"Max {i+1}",
                value=30,
                min_value=0,
                max_value=30,
                step=1,
                label_visibility="collapsed",
            )
        )

st.write("")

# -----------------------
# Calculate
# -----------------------

if st.button("Calculate Feeding Advice", type="primary"):

    with st.spinner("Optimizing..."):

        try:
            result = calculate_feeding(limits, maxes)

            st.success("Optimization complete!")

            st.divider()

            st.subheader("Results")

            st.write(result)

        except Exception as e:
            st.error(f"Calculation failed:\n\n{e}")
