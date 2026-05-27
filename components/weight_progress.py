import streamlit as st
import pandas as pd
import plotly.express as px

def render_weight_progress(weight_logs, height):

    st.subheader("📈 Weight & BMI Progress")

    if weight_logs:

        df = pd.DataFrame(
            weight_logs,
            columns=["Date", "Weight"]
        )

        # CONVERT HEIGHT FROM CM TO METERS
        height_m = float(height) / 100

        # CALCULATE BMI
        df["BMI"] = df["Weight"] / (height_m ** 2)

        # WEIGHT GRAPH
        fig_weight = px.line(
            df,
            x="Date",
            y="Weight",
            markers=True,
            title="Weight Progress"
        )

        fig_weight.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            title_font_size=24,
            font=dict(size=14),
            height=400
        )

        fig_weight.update_traces(
            line=dict(width=4),
            marker=dict(size=10)
        )

        st.plotly_chart(
            fig_weight,
            use_container_width=True
        )

        # BMI GRAPH
        fig_bmi = px.line(
            df,
            x="Date",
            y="BMI",
            markers=True,
            title="BMI Progress"
        )

        fig_bmi.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            title_font_size=24,
            font=dict(size=14),
            height=400,
        )

        fig_bmi.update_traces(
            line=dict(width=4),
            marker=dict(size=10)
        )

        # BMI CATEGORY LINES
        fig_bmi.add_hline(
            y=18.5,
            line_dash="dash",
            line_color="blue"
        )

        fig_bmi.add_hline(
            y=25,
            line_dash="dash",
            line_color="green",
        )

        fig_bmi.add_hline(
            y=30,
            line_dash="dash",
            line_color="orange"
        )

        fig_bmi.add_hline(
            y=35,
            line_dash="dash",
            line_color="red"
        )

        st.plotly_chart(
            fig_bmi,
            use_container_width=True
        )
        st.caption("Blue = Underweight | Green = Normal | Orange = Overweight | Red = Obese")
    else:
        st.info("No weight progress yet.")