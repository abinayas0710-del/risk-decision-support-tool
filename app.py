import streamlit as st
import pandas as pd
import plotly.express as px


# ------------------ APP CONFIG ------------------
st.set_page_config(
    page_title="Risk Decision Support Tool",
    layout="wide"
)

st.markdown("## 🛠️ Risk Decision Support Tool")
st.caption("Interactive Risk Analysis for IT Projects")

# ------------------ LOAD DATA ------------------
df = pd.read_csv("data/project1.csv")

# ------------------ SIDEBAR ------------------
st.sidebar.header("⚙️ Control Panel")

view_mode = st.sidebar.radio(
    "Select View",
    ["Overview", "Risk Analysis", "Critical Risks"]
)

threshold = st.sidebar.slider(
    "High Risk Threshold (After)",
    min_value=0,
    max_value=100,
    value=40
)
# -------- WHAT-IF SIMULATION CONTROLS --------
st.sidebar.subheader("🧪 What-If Simulation")

prob_reduce = st.sidebar.slider(
    "Reduce Probability (%)",
    min_value=0,
    max_value=50,
    value=0
)

impact_reduce = st.sidebar.slider(
    "Reduce Impact (%)",
    min_value=0,
    max_value=50,
    value=0
)

# ------------------ LOGIC ------------------
df["Residual_Risk"] = df["RiskScore_After"].apply(
    lambda x: "High" if x >= threshold else "Acceptable"
)
# -------- SIMULATED RISK CALCULATION --------
df["Sim_Probability"] = df["Probability_After_%"] * (1 - prob_reduce / 100)
df["Sim_Impact"] = df["Impact_After_%"] * (1 - impact_reduce / 100)
df["Sim_RiskScore"] = (df["Sim_Probability"] * df["Sim_Impact"]) / 100

def recommend(score):
    if score >= threshold:
        return "❌ Mitigation Required"
    elif score >= threshold * 0.7:
        return "⚠️ Monitor Closely"
    else:
        return "✅ Accept Risk"

df["Recommendation"] = df["Sim_RiskScore"].apply(recommend)

# ------------------ OVERVIEW ------------------
if view_mode == "Overview":
    st.subheader("📊 Project Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Risks", len(df))
    col2.metric(
        "High Residual Risks",
        len(df[df["Residual_Risk"] == "High"])
    )
    col3.metric(
        "Average Risk Reduction",
        round(df["Reduction_Abs"].mean(), 2)
    )

    fig = px.bar(
        df,
        x="Risk_ID",
        y=["RiskScore_Before", "RiskScore_After"],
        barmode="group",
        title="Before vs After Risk Scores"
    )
    st.plotly_chart(fig, use_container_width=True)


# ------------------ RISK ANALYSIS ------------------
elif view_mode == "Risk Analysis":
    st.subheader("📈 Detailed Risk Analysis")

    st.dataframe(
        df[
            [
                "Risk_ID",
                "Risk_Name",
                "RiskScore_Before",
                "Sim_RiskScore",
                "Residual_Risk",
                "Recommendation"
            ]
        ],
        use_container_width=True
    )

    fig2 = px.scatter(
        df,
        x="Probability_After_%",
        y="Impact_After_%",
        size="RiskScore_After",
        color="Residual_Risk",
        title="Risk Heat Map (After Mitigation)"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ------------------ CRITICAL RISKS ------------------
else:
    st.subheader("⚠️ Critical Risks Requiring Attention")

    critical = df[df["Residual_Risk"] == "High"]

    if critical.empty:
        st.success("No critical risks detected 🎉")
    else:
        st.warning("Immediate attention required")
        st.dataframe(
            critical[
                [
                    "Risk_ID",
                    "Risk_Name",
                    "RiskScore_After",
                    "Impact_Category_After"
                ]
            ],
            use_container_width=True
        )