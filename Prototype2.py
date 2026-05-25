# -*- coding: utf-8 -*-
"""
Created on Mon May 25 19:23:17 2026

@author: Syauqi Hanif
"""

# ============================================================
# Prototype2
# Interactive Sustainability Assessment Framework with AHP
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
    page_title="Prototype2 - AHP Sustainability Framework",
    layout="wide"
)

st.title("Prototype2: Interactive Sustainability Assessment Framework")
st.subheader("AHP-Based Weighting + Design/Material Alternative Evaluation")

st.write("""
This prototype demonstrates a possible interactive decision-support tool for
sustainability-oriented material/design selection of aircraft cabin composite panels.
The workflow consists of:

1. AHP-based weighting questionnaire  
2. Input of design/material alternative data  
3. Ranking and visualization  
4. Manual weighting adjustment for dynamic sensitivity exploration  
""")

# ============================================================
# CRITERIA
# ============================================================

criteria = [
    "Environmental",
    "Life Cycle Cost",
    "Engineering Performance",
    "Manufacturing Feasibility",
    "Circularity",
    "Regulatory Constraint"
]

# ============================================================
# DEFAULT DATA
# Scores are assumed normalized from 0 to 1
# Higher score = better
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

# ============================================================
# AHP FUNCTIONS
# ============================================================

def ahp_calculate_weights(pairwise_matrix):
    eigenvalues, eigenvectors = np.linalg.eig(pairwise_matrix)

    max_index = np.argmax(eigenvalues.real)
    max_eigenvalue = eigenvalues.real[max_index]
    principal_eigenvector = eigenvectors[:, max_index].real

    weights = principal_eigenvector / principal_eigenvector.sum()
    weights = np.abs(weights)
    weights = weights / weights.sum()

    n = pairwise_matrix.shape[0]
    consistency_index = (max_eigenvalue - n) / (n - 1)

    random_index_dict = {
        1: 0.00,
        2: 0.00,
        3: 0.58,
        4: 0.90,
        5: 1.12,
        6: 1.24,
        7: 1.32,
        8: 1.41,
        9: 1.45,
        10: 1.49
    }

    random_index = random_index_dict[n]

    if random_index == 0:
        consistency_ratio = 0
    else:
        consistency_ratio = consistency_index / random_index

    return weights, consistency_index, consistency_ratio


def build_ahp_matrix(criteria_list, pairwise_inputs):
    n = len(criteria_list)
    matrix = np.ones((n, n))

    for i in range(n):
        for j in range(i + 1, n):
            value = pairwise_inputs[(criteria_list[i], criteria_list[j])]
            matrix[i, j] = value
            matrix[j, i] = 1 / value

    return matrix


def calculate_index(data, criteria_list, weights_dict):
    result = data.copy()
    result["Final Sustainability Index"] = 0.0

    for c in criteria_list:
        result["Final Sustainability Index"] += result[c] * weights_dict[c]

    result = result.sort_values(
        by="Final Sustainability Index",
        ascending=False
    )

    return result


# ============================================================
# SESSION STATE
# ============================================================

if "ahp_done" not in st.session_state:
    st.session_state.ahp_done = False

if "ahp_weights" not in st.session_state:
    st.session_state.ahp_weights = None

if "input_data" not in st.session_state:
    st.session_state.input_data = default_data.copy()

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.header("Prototype2 Navigation")

page = st.sidebar.radio(
    "Select workflow step",
    [
        "Step 1 - AHP Questionnaire",
        "Step 2 - Input Alternative Data",
        "Step 3 - Results and Manual Adjustment"
    ]
)

# ============================================================
# STEP 1 - AHP QUESTIONNAIRE
# ============================================================

if page == "Step 1 - AHP Questionnaire":

    st.header("Step 1 - AHP Weighting Questionnaire")

    st.write("""
    In this step, the user determines the weighting factor of the six sustainability
    dimensions using the Analytic Hierarchy Process (AHP).

    For each pair of criteria, select which criterion is more important and how strong
    the preference is.
    """)

    st.info("""
    Scale explanation:
    
    - 1 = Equal importance  
    - 3 = Moderate importance  
    - 5 = Strong importance  
    - 7 = Very strong importance  
    - 9 = Extreme importance  
    - 2, 4, 6, 8 = Intermediate values  
    """)

    pairwise_inputs = {}

    st.subheader("Pairwise Comparison Questionnaire")

    for i in range(len(criteria)):
        for j in range(i + 1, len(criteria)):
            c1 = criteria[i]
            c2 = criteria[j]

            st.write(f"### {c1} vs {c2}")

            preference = st.radio(
                f"Which criterion is more important?",
                [c1, c2, "Equal"],
                key=f"pref_{c1}_{c2}",
                horizontal=True
            )

            intensity = st.slider(
                "How strong is the preference?",
                min_value=1,
                max_value=9,
                value=1,
                step=1,
                key=f"intensity_{c1}_{c2}"
            )

            if preference == "Equal":
                value = 1
            elif preference == c1:
                value = intensity
            else:
                value = 1 / intensity

            pairwise_inputs[(c1, c2)] = value

            st.divider()

    if st.button("Calculate AHP Weights"):

        ahp_matrix = build_ahp_matrix(criteria, pairwise_inputs)
        ahp_weights_array, ci, cr = ahp_calculate_weights(ahp_matrix)

        ahp_weights = {
            criteria[i]: ahp_weights_array[i]
            for i in range(len(criteria))
        }

        st.session_state.ahp_weights = ahp_weights
        st.session_state.ahp_matrix = ahp_matrix
        st.session_state.consistency_index = ci
        st.session_state.consistency_ratio = cr
        st.session_state.ahp_done = True

    if st.session_state.ahp_done:

        st.success("AHP weighting has been calculated.")

        weights_df = pd.DataFrame({
            "Criterion": list(st.session_state.ahp_weights.keys()),
            "AHP Weight": list(st.session_state.ahp_weights.values())
        }).sort_values("AHP Weight", ascending=False)

        st.subheader("AHP Weighting Result")
        st.dataframe(weights_df.round(4), use_container_width=True)

        st.subheader("AHP Pairwise Comparison Matrix")
        matrix_df = pd.DataFrame(
            st.session_state.ahp_matrix,
            index=criteria,
            columns=criteria
        )
        st.dataframe(matrix_df.round(3), use_container_width=True)

        st.subheader("Consistency Check")

        st.write(f"Consistency Index: **{st.session_state.consistency_index:.4f}**")
        st.write(f"Consistency Ratio: **{st.session_state.consistency_ratio:.4f}**")

        if st.session_state.consistency_ratio <= 0.10:
            st.success("The AHP judgement is considered consistent.")
        else:
            st.warning("""
            The consistency ratio is higher than 0.10. 
            The judgement may be inconsistent. You may revise the pairwise comparison.
            """)

        st.write("""
        After checking the AHP result, continue to **Step 2 - Input Alternative Data**.
        """)

# ============================================================
# STEP 2 - INPUT ALTERNATIVE DATA
# ============================================================

elif page == "Step 2 - Input Alternative Data":

    st.header("Step 2 - Input Alternative Data")

    if not st.session_state.ahp_done:
        st.warning("""
        AHP weights have not been calculated yet. 
        You can still edit the data, but please complete Step 1 before final evaluation.
        """)

    st.write("""
    In this step, the user inputs or edits the sustainability performance data
    for each design/material alternative.

    The current prototype assumes that all scores are already normalized between 0 and 1.
    Higher value means better performance.
    """)

    edited_data = st.data_editor(
        st.session_state.input_data,
        num_rows="dynamic",
        use_container_width=True
    )

    if st.button("Save Alternative Data"):
        st.session_state.input_data = edited_data.copy()
        st.success("Alternative data has been saved.")

    st.subheader("Current Saved Data")
    st.dataframe(st.session_state.input_data, use_container_width=True)

    st.info("""
    After saving the data, continue to **Step 3 - Results and Manual Adjustment**.
    """)

# ============================================================
# STEP 3 - RESULTS AND MANUAL ADJUSTMENT
# ============================================================

elif page == "Step 3 - Results and Manual Adjustment":

    st.header("Step 3 - Results and Manual Weighting Adjustment")

    if not st.session_state.ahp_done:
        st.error("Please complete Step 1 first to generate AHP weights.")
        st.stop()

    raw_data = st.session_state.input_data.copy()

    if "Alternative" not in raw_data.columns:
        st.error("Input data must contain an 'Alternative' column.")
        st.stop()

    df = raw_data.set_index("Alternative")

    for c in criteria:
        if c not in df.columns:
            st.error(f"Missing criterion column: {c}")
            st.stop()

    df[criteria] = df[criteria].apply(pd.to_numeric, errors="coerce")

    if df[criteria].isnull().values.any():
        st.error("Please ensure all criteria values are numeric.")
        st.stop()

    df[criteria] = df[criteria].clip(0, 1)

    st.subheader("AHP-Based Weighting Result")

    ahp_weights = st.session_state.ahp_weights

    ahp_weights_df = pd.DataFrame({
        "Criterion": list(ahp_weights.keys()),
        "AHP Weight": list(ahp_weights.values())
    }).sort_values("AHP Weight", ascending=False)

    st.dataframe(ahp_weights_df.round(4), use_container_width=True)

    st.subheader("Manual Adjustment of Weighting Factors")

    st.write("""
    The sliders below are initialized using the AHP-derived weights.
    The user can adjust them manually to observe how ranking and visualization change.
    The prototype automatically normalizes the adjusted weights so that the total equals 1.
    """)

    adjusted_raw_weights = {}

    cols = st.columns(2)

    for idx, c in enumerate(criteria):
        with cols[idx % 2]:
            adjusted_raw_weights[c] = st.slider(
                c,
                min_value=0.0,
                max_value=1.0,
                value=float(ahp_weights[c]),
                step=0.01
            )

    total_adjusted_weight = sum(adjusted_raw_weights.values())

    if total_adjusted_weight == 0:
        st.error("Total adjusted weight cannot be zero.")
        st.stop()

    adjusted_weights = {
        c: adjusted_raw_weights[c] / total_adjusted_weight
        for c in criteria
    }

    adjusted_weights_df = pd.DataFrame({
        "Criterion": list(adjusted_weights.keys()),
        "Adjusted Weight": list(adjusted_weights.values())
    }).sort_values("Adjusted Weight", ascending=False)

    st.subheader("Adjusted and Normalized Weighting Factors")
    st.dataframe(adjusted_weights_df.round(4), use_container_width=True)

    # ========================================================
    # CALCULATE RESULTS
    # ========================================================

    ranking = calculate_index(df, criteria, adjusted_weights)

    # ========================================================
    # OUTPUT 1 - RANKING
    # ========================================================

    st.header("Output 1 - Ranking of Design/Material Alternatives")

    ranking_display = ranking[["Final Sustainability Index"]].copy()
    ranking_display.insert(0, "Rank", range(1, len(ranking_display) + 1))

    st.dataframe(ranking_display.round(4), use_container_width=True)

    best_alternative = ranking.index[0]
    best_score = ranking["Final Sustainability Index"].iloc[0]

    st.success(
        f"Best alternative: {best_alternative} "
        f"with final score {best_score:.4f}"
    )

    # ========================================================
    # OUTPUT 2 - BAR CHART
    # ========================================================

    st.header("Output 2 - Bar Chart of Final Score")

    fig1, ax1 = plt.subplots(figsize=(10, 5))

    ax1.bar(
        ranking.index,
        ranking["Final Sustainability Index"]
    )

    ax1.set_title("Final Sustainability Score")
    ax1.set_ylabel("Composite Sustainability Index")
    ax1.set_xlabel("Design / Material Alternative")
    ax1.set_ylim(0, 1)
    ax1.tick_params(axis="x", rotation=25)

    plt.tight_layout()
    st.pyplot(fig1)

    # ========================================================
    # OUTPUT 3 - SPIDER CHART
    # ========================================================

    st.header("Output 3 - Spider Chart of Trade-off Between Dimensions")

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
    ax2.set_title("Trade-off Between Sustainability Dimensions")
    ax2.legend(loc="upper right", bbox_to_anchor=(1.45, 1.10))

    plt.tight_layout()
    st.pyplot(fig2)

    # ========================================================
    # OUTPUT 4 - HEATMAP
    # ========================================================

    st.header("Output 4 - Heatmap of Strengths and Weaknesses")

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

    ax3.set_title("Strength and Weakness Comparison")

    plt.tight_layout()
    st.pyplot(fig3)

    # ========================================================
    # AUTOMATIC INSIGHT
    # ========================================================

    st.header("Automatic Insight")

    for alternative in ranking.index:
        strongest_dimension = df.loc[alternative, criteria].idxmax()
        weakest_dimension = df.loc[alternative, criteria].idxmin()
        final_score = ranking.loc[alternative, "Final Sustainability Index"]

        st.write(
            f"**{alternative}** obtains a final score of **{final_score:.4f}**. "
            f"Its strongest dimension is **{strongest_dimension}**, "
            f"while its weakest dimension is **{weakest_dimension}**."
        )

    st.write("""
    This final page allows the user to compare the original AHP-derived weighting
    with manually adjusted weighting factors. Therefore, the user can observe the
    dynamic effect of shifting decision priorities on the final ranking and visualization.
    """)