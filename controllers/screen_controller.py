"""
ScreenController — CONTROLLER (client-side navigation layer)

Implements the Centralized Controller ADR: all screen transitions flow through
this single class.  No view ever imports another view or writes to session
state directly — every transition goes through a named method here.

Streamlit re-runs the entire script on each interaction, so routing state is
persisted in st.session_state.  ScreenController owns that state schema and
is the only class that reads or writes it.

Screen identifiers
------------------
  'upload'     → UploadScreen
  'selection'  → SelectionScreen
  'controlled' → ControlledScreen
  'freerange'  → FreeRangeScreen
  'results'    → ResultsScreen
"""

import streamlit as st

from controllers.data_connector import DataConnector

# ── Session-state schema ──────────────────────────────────────────────────────

_DEFAULTS: dict = {
    "current_screen": "upload",
    "playtest_set":   None,   # dict: { human_file, agent_file, game_name, test_date }
    "analysis_mode":  None,   # 'controlled' | 'freerange'
    "goal_data":      None,   # dict matching PlaytestGoal constructor kwargs
    "bounds_data":    None,   # dict matching UserBounds constructor kwargs
    "results":        None,   # dict: { report, metadata }
    "is_analyzing":   False,
    "analysis_error": None,
}

# Back-stack is the natural linear flow of the app
_BACK_MAP: dict[str, str] = {
    "selection":  "upload",
    "controlled": "selection",
    "freerange":  "selection",
    "results":    None,        # resolved dynamically to the active mode screen
}


class ScreenController:

    def __init__(self):
        self._init_session_state()
        self._connector = DataConnector()

    # ── Public rendering entry point ──────────────────────────────────────────

    def render(self):
        """
        Main dispatch loop.  Called once per Streamlit script run.
        Reads the current screen from session state and renders the
        appropriate view, passing `self` so views can call navigation methods.
        """
        # Import views here (not at module level) to avoid circular imports
        # between the controller and its views.
        from views.upload_screen      import UploadScreen
        from views.selection_screen   import SelectionScreen
        from views.controlled_screen  import ControlledScreen
        from views.free_range_screen  import FreeRangeScreen
        from views.results_screen     import ResultsScreen

        screen_map = {
            "upload":     UploadScreen,
            "selection":  SelectionScreen,
            "controlled": ControlledScreen,
            "freerange":  FreeRangeScreen,
            "results":    ResultsScreen,
        }

        current = st.session_state.current_screen
        view_cls = screen_map.get(current)

        if view_cls is None:
            st.error(f"ScreenController: unknown screen '{current}'")
            return

        view_cls(controller=self).render()

    # ── Navigation actions ────────────────────────────────────────────────────

    def go_to_selection(self, playtest_set_data: dict):
        """
        Called by UploadScreen once both files and game metadata are committed.

        Parameters
        ----------
        playtest_set_data : dict
            Keys: human_file, agent_file, game_name, test_date
        """
        st.session_state.playtest_set  = playtest_set_data
        st.session_state.current_screen = "selection"
        st.rerun()

    def go_to_parameters(self, mode: str):
        """
        Called by SelectionScreen when the user picks an analysis mode.

        Parameters
        ----------
        mode : 'controlled' | 'freerange'
        """
        if mode not in ("controlled", "freerange"):
            st.error(f"ScreenController: unknown mode '{mode}'")
            return
        st.session_state.analysis_mode  = mode
        st.session_state.current_screen = mode
        st.rerun()

    def run_analysis(self, *, goal_data: dict | None = None, bounds_data: dict | None = None):
        """
        Called by ControlledScreen or FreeRangeScreen when the user submits
        their parameters.  Stores the parameters, triggers the LLM call via
        DataConnector, then navigates to ResultsScreen on success.

        Parameters
        ----------
        goal_data   : dict | None  — required when mode == 'controlled'
        bounds_data : dict | None  — required when mode == 'freerange'
        """
        st.session_state.goal_data      = goal_data
        st.session_state.bounds_data    = bounds_data
        st.session_state.is_analyzing   = True
        st.session_state.analysis_error = None

        pset = st.session_state.playtest_set
        mode = st.session_state.analysis_mode

        try:
            result = self._connector.run_analysis(
                human_file  = pset["human_file"],
                agent_file  = pset["agent_file"],
                game_name   = pset["game_name"],
                test_date   = pset.get("test_date", ""),
                mode        = mode,
                goal_data   = goal_data,
                bounds_data = bounds_data,
            )
            st.session_state.results        = result
            st.session_state.is_analyzing   = False
            st.session_state.current_screen = "results"
        except Exception as exc:
            st.session_state.is_analyzing   = False
            st.session_state.analysis_error = str(exc)

        st.rerun()

    def go_back(self):
        """Navigate one logical step back without losing already-entered data."""
        current = st.session_state.current_screen
        target  = _BACK_MAP.get(current)

        # Results screen goes back to whichever parameter screen was active
        if current == "results":
            target = st.session_state.analysis_mode or "selection"

        if target:
            st.session_state.current_screen = target
            st.rerun()

    def reset(self):
        """Full reset — returns the app to the initial upload screen."""
        for key, default in _DEFAULTS.items():
            st.session_state[key] = default
        st.rerun()

    # ── Internal helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _init_session_state():
        """Populate session state with defaults on first run only."""
        for key, default in _DEFAULTS.items():
            if key not in st.session_state:
                st.session_state[key] = default
