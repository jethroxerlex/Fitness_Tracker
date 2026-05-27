import streamlit as st
import pandas as pd
import plotly.express as px

def render_weight_progress(weight_logs):

    st.subheader("📈 Weight Progress")

    if weight_logs:

        df = pd.DataFrame(
            weight_logs,
            columns=["Date", "Weight"]
        )

        fig = px.line(
            df,
            x="Date",
            y="Weight",
            markers=True,
            title="Weight Progress"
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            title_font_size=24,
            font=dict(size=14),
            height=450
        )

        fig.update_traces(
            line=dict(width=4),
            marker=dict(size=10)
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.info("No weight progress yet.")