import streamlit as st
from calculator import calculate_feeding, calculate_num_needed

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

    with st.spinner("Optimizing..."):

        try:
            result = calculate_feeding(limits, maxes)

            st.success("Optimization complete!")

            st.divider()

            st.subheader("Results")
            number_needed = calculate_num_needed(limits, maxes)
            st.write(
                "Number of items needed to fully level your mount:", number_needed
            )

            st.table(result)

        except Exception as e:
            st.error(f"Calculation failed:\n\n{e}")
