"""
ControlledScreen — VIEW

Collects the PlaytestGoal parameters: the specific problem to investigate,
success criteria, optional focus areas, and optional context.  On submit,
delegates to ScreenController.run_analysis() with goal_data populated.
"""

import streamlit as st


class ControlledScreen:

    def __init__(self, controller):
        self.controller = controller

    def render(self):
        pset = st.session_state.playtest_set

        st.title("Playtest Analyzer")
        st.subheader("Step 3 — Define Your Investigation")
        st.markdown(
            f"**Game:** {pset['game_name']} &nbsp;|&nbsp; "
            f"**Date:** {pset['test_date']} &nbsp;|&nbsp; **Mode:** Controlled"
        )
        st.divider()

        # ── Goal fields ────────────────────────────────────────────────────
        target_problem = st.text_area(
            "Target Problem *",
            placeholder=(
                "Describe the specific bug, exploit, or behaviour you want to "
                "investigate.  Be as precise as possible.\n\n"
                "Example: Does the AI agent exploit the item duplication glitch in "
                "the inventory system more frequently than human players?"
            ),
            height=120,
        )

        success_criteria = st.text_area(
            "Success Criteria *",
            placeholder=(
                "What does a confirmed finding look like?\n\n"
                "Example: The agent's inventory logs show item counts exceeding the "
                "theoretical maximum more than 3 times per session, while human logs "
                "show zero such occurrences."
            ),
            height=100,
        )

        focus_areas_raw = st.text_input(
            "Focus Areas (optional, comma-separated)",
            placeholder="e.g. inventory, economy, combat",
            help="Sub-systems to prioritise in the analysis.",
        )

        context = st.text_area(
            "Additional Context (optional)",
            placeholder="Any background the analyser should know — patch notes, prior findings, etc.",
            height=80,
        )

        # ── Error feedback ─────────────────────────────────────────────────
        if st.session_state.analysis_error:
            st.error(f"Analysis failed: {st.session_state.analysis_error}")

        st.divider()

        col_back, col_run = st.columns([1, 3])
        with col_back:
            if st.button("← Back"):
                self.controller.go_back()

        with col_run:
            ready = bool(target_problem.strip() and success_criteria.strip())
            label = "Analyzing…" if st.session_state.is_analyzing else "Run Analysis →"
            if st.button(label, disabled=not ready or st.session_state.is_analyzing,
                         type="primary", use_container_width=True):
                focus_areas = [a.strip() for a in focus_areas_raw.split(",") if a.strip()]
                self.controller.run_analysis(
                    goal_data={
                        "target_problem":   target_problem.strip(),
                        "success_criteria": success_criteria.strip(),
                        "focus_areas":      focus_areas,
                        "context":          context.strip(),
                    }
                )
