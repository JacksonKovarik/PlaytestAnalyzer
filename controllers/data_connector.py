"""
DataConnector — CONTROLLER (server-side orchestration layer)

Acts as the seam between the ScreenController and the LLM infrastructure.
It receives the raw session-state values, hydrates them into the correct Model
instances, validates consistency with the requested mode, then delegates to
LLMConnector and returns the result dict.

Nothing in this class touches Streamlit directly — ScreenController is its
only caller and is responsible for all session-state reads/writes.
"""

from models.playtest_set  import PlaytestSet
from models.playtest_goal import PlaytestGoal
from models.user_bounds   import UserBounds
from connectors.llm_connector import LLMConnector


class DataConnector:

    def __init__(self):
        self.llm = LLMConnector()

    def run_analysis(
        self,
        *,
        human_file,
        agent_file,
        game_name: str,
        test_date: str,
        mode: str,
        goal_data: dict | None,
        bounds_data: dict | None,
    ) -> dict:
        """
        Primary orchestration method. Called once per analysis request.

        Parameters
        ----------
        human_file   : UploadedFile  Streamlit file object for human data.
        agent_file   : UploadedFile  Streamlit file object for agent data.
        game_name    : str
        test_date    : str           ISO-8601 date string.
        mode         : str           'controlled' or 'freerange'
        goal_data    : dict | None   Raw kwargs for PlaytestGoal; required if mode == 'controlled'.
        bounds_data  : dict | None   Raw kwargs for UserBounds;  required if mode == 'freerange'.

        Returns
        -------
        dict  { 'report': str, 'metadata': dict }
        """
        # ── Step 1: Hydrate the dataset model ─────────────────────────────────
        playtest_set = PlaytestSet(
            human_file=human_file,
            agent_file=agent_file,
            game_name=game_name,
            test_date=test_date,
        )
        contents = playtest_set.extract_contents()

        # ── Step 2: Hydrate the mode-specific parameter model ─────────────────
        goal, bounds = self._hydrate_parameters(mode, goal_data, bounds_data)

        # ── Step 3: Delegate to LLMConnector ──────────────────────────────────
        report = self.llm.analyze(
            human_content=contents["human_content"],
            agent_content=contents["agent_content"],
            metadata=playtest_set.to_metadata(),
            mode=mode,
            goal=goal,
            bounds=bounds,
        )

        return {
            "report":   report,
            "metadata": playtest_set.to_metadata(),
        }

    # ── Private helpers ───────────────────────────────────────────────────────

    def _hydrate_parameters(
        self,
        mode: str,
        goal_data: dict | None,
        bounds_data: dict | None,
    ) -> tuple:
        """
        Validates that the correct parameter model exists for the given mode
        and constructs the appropriate class instance.

        Centralising this logic here means the ScreenController stays thin and
        mode-validation is tested in one place.
        """
        if mode == "controlled":
            if not goal_data:
                raise ValueError("DataConnector: goal_data is required for controlled mode")
            return PlaytestGoal(**goal_data), None

        if mode == "freerange":
            if not bounds_data:
                raise ValueError("DataConnector: bounds_data is required for freerange mode")
            return None, UserBounds(**bounds_data)

        raise ValueError(
            f'DataConnector: unknown mode "{mode}". Expected "controlled" or "freerange".'
        )
