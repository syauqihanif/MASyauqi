# -*- coding: utf-8 -*-
"""
Created on Mon May 25 18:56:17 2026

@author: Syauqi Hanif
"""

# ============================================================
# Prototype1
# Interactive Sustainability Assessment Prototype
# Case Study: Aircraft Cabin Composite Panel
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Prototype1 - Sustainability Assessment",
    layout="wide"
)

st.title("Prototype1: Interactive Sustainability Assessment Framework")
st.subheader("Case Study: Aircraft Cabin Composite Panel")

st.write("""
This prototype helps a user compare design/material alternatives using a
Composite Sustainability Index. The user can edit input data, choose a
weighting method, and directly observe ranking, bar chart, spider chart,
heatmap, and automatic insights.
""")

# ============================================================
# DEFAULT INPUT DATA
# Scores are assumed normalized between 0 and 1.
# Higher score = better performance.
# ============================================================

default_data = pd.DataFrame({
    "Alternative": [
        "A1 Thermoset CFRP + Autoclave",
        "A2 Thermoplastic CFRP + Compression",
        "A3 Thermoplastic GFRP + Thermoforming",
        "A4 Recycled Carbon TP + Compression"
    ],
    "Environmental": [0.42, 0.72, 0.78, 0.90],
    "Life Cycle Cost": [0.48, 0.58, 0.82, 0.66],
    "Engineering Performance": [0.92, 0.88, 0.62, 0.76],
    "Manufacturing Feasibility": [0.40, 0.80, 0.86, 0.72],
    "Circularity": [0.20, 0.74, 0.68, 0.94],
    "Regulatory Constraint": [0.92, 0.76, 0.62, 0.58]
})

criteria = [
    "Environmental",
    "Life Cycle Cost",
    "Engineering Performance",
    "Manufacturing Feasibility",
    "Circularity",
    "Regulatory Constraint"
]

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("User Control Panel")

weighting_method = st.sidebar.selectbox(
    "Choose weighting method",
    [
        "Equal Weighting",
        "Manual Weighting",
        "CRITIC Objective Weighting"
    ]
)

st.sidebar.write("""
**Note:** All input scores are assumed normalized from 0 to 1.
Higher value means better performance.
""")

# ============================================================
# DATA INPUT
# ============================================================

st.header("1. Input Data")

st.write("""
Budi can edit the table below. Each value represents the performance score
of an alternative in each sustainability dimension.
""")

edited_data = st.data_editor(
    default_data,
    num_rows="dynamic",
    use_container_width=True
)

df = edited_data.copy()

if "Alternative" not in df.columns:
    st.error("The table must contain an 'Alternative' column.")
    st.stop()

df = df.set_index("Alternative")

for c in criteria:
    if c not in df.columns:
        st.error(f"Missing required criterion column: {c}")
        st.stop()

df[criteria] = df[criteria].apply(pd.to_numeric, errors="coerce")

if df[criteria].isnull().values.any():
    st.error("Please make sure all criteria values are numeric.")
    st.stop()

# Clip values to 0-1 for safety
df[criteria] = df[criteria].clip(0, 1)

# ============================================================
# WEIGHTING FUNCTIONS
# ============================================================

def equal_weights(criteria_list):
    return {c: 1 / len(criteria_list) for c in criteria_list}


def manual_weights(criteria_list):
    st.sidebar.subheader("Manual Weighting")

    raw_weights = {}

    for c in criteria_list:
        raw_weights[c] = st.sidebar.slider(
            c,
            min_value=0.0,
            max_value=1.0,
            value=1 / len(criteria_list),
            step=0.01
        )

    total = sum(raw_weights.values())

    if total == 0:
        st.sidebar.error("Total weight cannot be zero.")
        st.stop()

    return {c: raw_weights[c] / total for c in criteria_list}


def critic_weights(data, criteria_list):
    matrix = data[criteria_list].copy()

    # Standard deviation of each criterion
    std_dev = matrix.std(axis=0)

    # Correlation matrix
    corr_matrix = matrix.corr()

    # Replace NaN correlation with 0
    corr_matrix = corr_matrix.fillna(0)

    information_content = {}

    for j in criteria_list:
        conflict_sum = 0

        for k in criteria_list:
            conflict_sum += 1 - corr_matrix.loc[j, k]

        information_content[j] = std_dev[j] * conflict_sum

    total_information = sum(information_content.values())

    if total_information == 0:
        return equal_weights(criteria_list)

    weights = {
        c: information_content[c] / total_information
        for c in criteria_list
    }

    return weights


# ============================================================
# SELECT WEIGHTS
# ============================================================

if weighting_method == "Equal Weighting":
    weights = equal_weights(criteria)

elif weighting_method == "Manual Weighting":
    weights = manual_weights(criteria)

elif weighting_method == "CRITIC Objective Weighting":
    weights = critic_weights(df, criteria)

# Display weights
st.header("2. Weighting Result")

weights_df = pd.DataFrame({
    "Criterion": list(weights.keys()),
    "Weight": list(weights.values())
}).sort_values("Weight", ascending=False)

st.dataframe(weights_df.round(3), use_container_width=True)

# ============================================================
# COMPOSITE INDEX CALCULATION
# ============================================================

df["Final Sustainability Index"] = 0.0

for c in criteria:
    df["Final Sustainability Index"] += df[c] * weights[c]

ranking = df.sort_values(
    by="Final Sustainability Index",
    ascending=False
)

# ============================================================
# RANKING
# ============================================================

st.header("3. Final Ranking")

ranking_display = ranking[["Final Sustainability Index"]].copy()
ranking_display.insert(0, "Rank", range(1, len(ranking_display) + 1))

st.dataframe(ranking_display.round(3), use_container_width=True)

best_alternative = ranking.index[0]
best_score = ranking["Final Sustainability Index"].iloc[0]

st.success(
    f"Best alternative: {best_alternative} "
    f"with final score {best_score:.3f}"
)

# ============================================================
# BAR CHART
# ============================================================

st.header("4. Bar Chart: Final Sustainability Score")

fig1, ax1 = plt.subplots(figsize=(10, 5))

ax1.bar(
    ranking.index,
    ranking["Final Sustainability Index"]
)

ax1.set_title("Final Sustainability Ranking")
ax1.set_ylabel("Composite Sustainability Index")
ax1.set_xlabel("Design / Material Alternative")
ax1.set_ylim(0, 1)
ax1.tick_params(axis="x", rotation=25)

plt.tight_layout()
st.pyplot(fig1)

# ============================================================
# SPIDER CHART
# ============================================================

st.header("5. Spider Chart: Trade-off Between Dimensions")

num_criteria = len(criteria)
angles = np.linspace(0, 2 * np.pi, num_criteria, endpoint=False).tolist()
angles += angles[:1]

fig2 = plt.figure(figsize=(8, 8))
ax2 = plt.subplot(111, polar=True)

for alternative in df.index:
    values = df.loc[alternative, criteria].tolist()
    values += values[:1]

    ax2.plot(
        angles,
        values,
        marker="o",
        label=alternative
    )

    ax2.fill(
        angles,
        values,
        alpha=0.08
    )

ax2.set_xticks(angles[:-1])
ax2.set_xticklabels(criteria)
ax2.set_ylim(0, 1)
ax2.set_title("Sustainability Dimension Trade-off")
ax2.legend(loc="upper right", bbox_to_anchor=(1.45, 1.10))

plt.tight_layout()
st.pyplot(fig2)

# ============================================================
# HEATMAP
# ============================================================

st.header("6. Heatmap: Strength and Weakness Comparison")

heatmap_data = df[criteria]

fig3, ax3 = plt.subplots(figsize=(10, 5))

im = ax3.imshow(
    heatmap_data,
    aspect="auto",
    vmin=0,
    vmax=1
)

fig3.colorbar(im, ax=ax3, label="Normalized Score")

ax3.set_xticks(np.arange(len(criteria)))
ax3.set_xticklabels(criteria, rotation=30, ha="right")

ax3.set_yticks(np.arange(len(heatmap_data.index)))
ax3.set_yticklabels(heatmap_data.index)

ax3.set_title("Heatmap of Sustainability Dimension Scores")

plt.tight_layout()
st.pyplot(fig3)

# ============================================================
# AUTOMATIC INSIGHT
# ============================================================

st.header("7. Automatic Insight")

st.write("""
The following insights are generated automatically from the input data.
They help the user identify the strongest and weakest sustainability dimensions
for each alternative.
""")

for alternative in ranking.index:
    strongest_dimension = df.loc[alternative, criteria].idxmax()
    weakest_dimension = df.loc[alternative, criteria].idxmin()
    final_score = df.loc[alternative, "Final Sustainability Index"]

    st.write(
        f"**{alternative}** has a final score of **{final_score:.3f}**. "
        f"Its strongest dimension is **{strongest_dimension}**, "
        f"while its weakest dimension is **{weakest_dimension}**."
    )

# ============================================================
# CRITIC EXPLANATION
# ============================================================

if weighting_method == "CRITIC Objective Weighting":
    st.header("8. CRITIC Method Explanation")

    st.write("""
    The CRITIC method determines objective weights based on:
    
    1. **Contrast intensity**: criteria with higher variation between alternatives
       receive higher importance.
    2. **Conflict between criteria**: criteria that are less correlated with other
       criteria provide more unique information.
       
    Therefore, a criterion receives a high CRITIC weight if it both differentiates
    alternatives strongly and provides non-redundant information.
    """)

# ============================================================
# EXPORT OPTION
# ============================================================

st.header("9. Export Result")

export_df = ranking.copy()
export_df["Rank"] = range(1, len(export_df) + 1)

csv = export_df.to_csv().encode("utf-8")

st.download_button(
    label="Download Result as CSV",
    data=csv,
    file_name="Prototype1_sustainability_result.csv",
    mime="text/csv"
)