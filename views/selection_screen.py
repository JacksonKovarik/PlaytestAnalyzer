"""
SelectionScreen — VIEW

Prompts the user to choose between "Controlled" and "Free-Range" analysis
modes, then delegates to ScreenController.go_to_parameters().
"""

import streamlit as st


class SelectionScreen:

    def __init__(self, controller):
        self.controller = controller

    def render(self):
        pset = st.session_state.playtest_set

        st.title("Playtest Analyzer")
        st.subheader("Step 2 — Select Analysis Mode")
        st.markdown(f"**Game:** {pset['game_name']} &nbsp;|&nbsp; **Date:** {pset['test_date']}")
        st.divider()

        col_c, col_f = st.columns(2, gap="large")

        with col_c:
            st.markdown("### Controlled")
            st.markdown(
                "You already have a specific hypothesis or bug to investigate.  "
                "Provide a target problem and success criteria, and the Comparison "
                "Engine will focus its entire analysis on that question.\n\n"
                "*Best for:* targeted QA, regression checks, exploit confirmation."
            )
            if st.button("Choose Controlled", type="primary", use_container_width=True):
                self.controller.go_to_parameters("controlled")

        with col_f:
            st.markdown("### Free-Range")
            st.markdown(
                "You have no specific hypothesis yet.  Provide general game "
                "parameters and the Comparison Engine will explore both datasets "
                "freely to surface exploits, divergences, and anomalies.\n\n"
                "*Best for:* early-access discovery, broad behavioural audits."
            )
            if st.button("Choose Free-Range", type="secondary", use_container_width=True):
                self.controller.go_to_parameters("freerange")

        st.divider()
        if st.button("← Back"):
            self.controller.go_back()
