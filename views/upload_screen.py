"""
UploadScreen — VIEW

Accepts two dataset files (human and agentic) plus game metadata, then
delegates to ScreenController.go_to_selection().

This view owns no state beyond what is live in the Streamlit widgets during a
single render pass.  The controller is the only entity that writes to
session_state.
"""

import streamlit as st


class UploadScreen:

    def __init__(self, controller):
        self.controller = controller

    def render(self):
        st.title("Playtest Analyzer")
        st.subheader("Step 1 — Upload Datasets")
        st.markdown(
            "Upload one dataset from **human** playtesters and one from an "
            "**agentic (AI)** playtester.  Both files should be plain text or "
            "CSV exports from your data collection tool."
        )

        st.divider()

        # ── Game metadata ──────────────────────────────────────────────────
        col1, col2 = st.columns(2)
        with col1:
            game_name = st.text_input("Game Name *", placeholder="e.g. Project Nova")
        with col2:
            test_date = st.date_input("Test Date", value="today")

        st.divider()

        # ── File uploaders ─────────────────────────────────────────────────
        col_h, col_a = st.columns(2)
        with col_h:
            st.markdown("#### Human Dataset")
            human_file = st.file_uploader(
                "Upload human playtest data",
                type=["txt", "csv", "json", "log"],
                key="human_upload",
                help="Data collected from human playtesters",
            )
            if human_file:
                st.success(f"Loaded: {human_file.name}")

        with col_a:
            st.markdown("#### Agentic Dataset")
            agent_file = st.file_uploader(
                "Upload agentic playtest data",
                type=["txt", "csv", "json", "log"],
                key="agent_upload",
                help="Data collected from the AI playtester",
            )
            if agent_file:
                st.success(f"Loaded: {agent_file.name}")

        st.divider()

        # ── Commit ─────────────────────────────────────────────────────────
        ready = human_file and agent_file and game_name.strip()
        if st.button("Continue →", disabled=not ready, type="primary", use_container_width=True):
            self.controller.go_to_selection({
                "human_file": human_file,
                "agent_file": agent_file,
                "game_name":  game_name.strip(),
                "test_date":  str(test_date),
            })

        if not ready:
            st.caption("Both files and a game name are required to continue.")
