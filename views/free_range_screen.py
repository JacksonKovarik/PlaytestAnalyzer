"""
FreeRangeScreen — VIEW

Collects the UserBounds parameters for open-ended discovery: game context,
optional scope exclusions, a priority hint, and a findings cap.  On submit,
delegates to ScreenController.run_analysis() with bounds_data populated.
"""

import streamlit as st


class FreeRangeScreen:

    def __init__(self, controller):
        self.controller = controller

    def render(self):
        pset = st.session_state.playtest_set

        st.title("Playtest Analyzer")
        st.subheader("Step 3 — Set Discovery Bounds")
        st.markdown(
            f"**Game:** {pset['game_name']} &nbsp;|&nbsp; "
            f"**Date:** {pset['test_date']} &nbsp;|&nbsp; **Mode:** Free-Range"
        )
        st.divider()

        # ── Bounds fields ──────────────────────────────────────────────────
        game_parameters = st.text_area(
            "Game Parameters *",
            placeholder=(
                "Describe the game's core rules and systems so the analyser has "
                "enough domain context to interpret the data correctly.\n\n"
                "Example: Turn-based strategy game.  Players collect resources each "
                "turn, build units, and attack enemy bases.  Victory condition: "
                "destroy all enemy structures.  Economy, combat, and diplomacy systems."
            ),
            height=150,
        )

        col1, col2 = st.columns(2)
        with col1:
            priority_hint = st.text_input(
                "Priority Hint (optional)",
                placeholder="e.g. economy exploits",
                help="Which class of finding to surface first in the report.",
            )
        with col2:
            max_findings = st.number_input(
                "Max Findings to Report",
                min_value=1,
                max_value=50,
                value=10,
                help="Caps the number of findings to keep the report actionable.",
            )

        scope_limit = st.text_input(
            "Out of Scope (optional)",
            placeholder="e.g. ignore tutorial levels, skip UI events",
            help="Anything the analyser should explicitly exclude.",
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
            ready = bool(game_parameters.strip())
            label = "Analyzing…" if st.session_state.is_analyzing else "Run Analysis →"
            if st.button(label, disabled=not ready or st.session_state.is_analyzing,
                         type="primary", use_container_width=True):
                self.controller.run_analysis(
                    bounds_data={
                        "game_parameters": game_parameters.strip(),
                        "scope_limit":     scope_limit.strip(),
                        "max_findings":    int(max_findings),
                        "priority_hint":   priority_hint.strip(),
                    }
                )
