"""
ResultsScreen — VIEW

Displays the Markdown report returned by the LLM, along with session metadata
(game name, date, files used).  Offers download of the raw report and a
"Start Over" button that resets the entire flow.
"""

import streamlit as st


class ResultsScreen:

    def __init__(self, controller):
        self.controller = controller

    def render(self):
        results  = st.session_state.results
        metadata = results["metadata"]
        report   = results["report"]
        mode     = st.session_state.analysis_mode

        st.title("Analysis Report")

        # ── Session metadata strip ─────────────────────────────────────────
        st.markdown(
            f"**Game:** {metadata['game_name']} &nbsp;|&nbsp; "
            f"**Date:** {metadata['test_date']} &nbsp;|&nbsp; "
            f"**Mode:** {'Controlled' if mode == 'controlled' else 'Free-Range'}"
        )
        st.caption(
            f"Human dataset: `{metadata['human_file_name']}`  &nbsp;·&nbsp;  "
            f"Agent dataset: `{metadata['agent_file_name']}`"
        )
        st.divider()

        # ── Report body ────────────────────────────────────────────────────
        st.markdown(report)

        st.divider()

        # ── Actions ────────────────────────────────────────────────────────
        col_dl, col_back, col_reset = st.columns(3)

        with col_dl:
            st.download_button(
                label="Download Report (.md)",
                data=report,
                file_name=f"playtest_report_{metadata['game_name'].replace(' ', '_')}_{metadata['test_date']}.md",
                mime="text/markdown",
                use_container_width=True,
            )

        with col_back:
            if st.button("← Adjust Parameters", use_container_width=True):
                self.controller.go_back()

        with col_reset:
            if st.button("Start Over", type="secondary", use_container_width=True):
                self.controller.reset()
