"""
LLMConnector — CONNECTOR

Single responsibility: package the  dataset strings plus the analysis
parameters into a well-formed Anthropic API call and return the structured
text report.

This class knows nothing about Streamlit, session state, or file I/O.
DataConnector is its only caller.

Design note: both datasets are inlined as clearly labelled text blocks inside
the user message.  This lets Claude see both datasets in the same context
window for direct side-by-side comparison without needing the Files API.
"""

import anthropic

from models.playtest_goal import PlaytestGoal
from models.user_bounds   import UserBounds


class LLMConnector:

    MODEL      = "claude-opus-4-8"  # highest reasoning quality for analysis tasks
    MAX_TOKENS = 4096

    def __init__(self):
        # The SDK automatically reads ANTHROPIC_API_KEY from the environment.
        self.client = anthropic.Anthropic()

    # ── Public API ────────────────────────────────────────────────────────────

    def analyze(
        self,
        *,
        human_content: str,
        agent_content: str,
        metadata: dict,
        mode: str,
        goal: PlaytestGoal | None,
        bounds: UserBounds | None,
    ) -> str:
        """
        Core entry point.  Dispatches to the correct prompt-builder based on
        mode, calls the API, and returns the report as a plain string.

        Parameters
        ----------
        human_content : str   Raw text of the human playtest file.
        agent_content : str   Raw text of the agent playtest file.
        metadata      : dict  PlaytestSet.to_metadata() output.
        mode          : str   'controlled' or 'freerange'
        goal          : PlaytestGoal | None  — populated in controlled mode.
        bounds        : UserBounds | None    — populated in freerange mode.

        Returns
        -------
        str  The LLM's analysis report in Markdown format.
        """
        system_prompt = self._build_system_prompt(metadata)
        user_message  = self._build_user_message(
            human_content=human_content,
            agent_content=agent_content,
            metadata=metadata,
            mode=mode,
            goal=goal,
            bounds=bounds,
        )

        response = self.client.messages.create(
            model=self.MODEL,
            max_tokens=self.MAX_TOKENS,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )

        return response.content[0].text

    # ── Private helpers ───────────────────────────────────────────────────────

    def _build_system_prompt(self, metadata: dict) -> str:
        """
        Establishes the LLM's persona and non-negotiable output constraints.
        This is identical regardless of analysis mode.
        """
        return (
            f'You are the Comparison Engine for a game playtesting analysis system.\n\n'
            f'Your purpose is to compare two playtesting datasets for '
            f'"{metadata["game_name"]}" (session date: {metadata["test_date"]}) '
            f'and produce an actionable report for a game designer or QA engineer.\n\n'
            f'Dataset A is from HUMAN playtesters.\n'
            f'Dataset B is from an AGENTIC (AI) playtester.\n\n'
            f'You will receive both datasets in full. Your analysis must:\n'
            f'1. Identify behavioural patterns that differ significantly between humans and the agent.\n'
            f'2. Flag any gameplay exploits, loopholes, or unintended strategies the agent discovered.\n'
            f'3. Surface any data anomalies that suggest bugs (impossible values, missing states, etc.).\n'
            f'4. Be specific — cite evidence from the data, not general observations.\n'
            f'5. Remain objective; do not assume agent behaviour is "wrong" just because it differs.\n\n'
            f'Format your response as a structured Markdown report.'
        )

    def _build_user_message(
        self,
        *,
        human_content: str,
        agent_content: str,
        metadata: dict,
        mode: str,
        goal: PlaytestGoal | None,
        bounds: UserBounds | None,
    ) -> str:
        """
        Assembles the full user turn.  Task brief comes first so the model
        reads the objectives before encountering the raw data.
        """
        task_section = (
            self._build_controlled_task(goal)
            if mode == "controlled"
            else self._build_freerange_task(bounds)
        )
        data_section = self._build_data_section(human_content, agent_content)
        return f"{task_section}\n\n{data_section}"

    def _build_data_section(self, human_content: str, agent_content: str) -> str:
        """
        Inlines both datasets inside XML-style fences so the model can
        unambiguously distinguish the two sources while cross-referencing.
        """
        return (
            "--- DATASET A: HUMAN PLAYTEST DATA ---\n"
            "<human_dataset>\n"
            f"{human_content}\n"
            "</human_dataset>\n\n"
            "--- DATASET B: AGENTIC PLAYTEST DATA ---\n"
            "<agent_dataset>\n"
            f"{agent_content}\n"
            "</agent_dataset>"
        )

    def _build_controlled_task(self, goal: PlaytestGoal) -> str:
        """
        Controlled mode: directs the LLM to answer a specific research question.
        PlaytestGoal.to_prompt_fragment() supplies the structured brief.
        """
        return (
            "## Analysis Mode: CONTROLLED\n\n"
            "You have been given a specific investigation brief. Focus your entire "
            "analysis on this brief. Do not report findings outside its scope unless "
            "they represent a critical safety or progression-breaking bug.\n\n"
            f"{goal.to_prompt_fragment()}\n\n"
            "Produce your report with the following sections:\n"
            "1. **Investigation Summary** — restate the problem in your own words\n"
            "2. **Evidence From Human Data** — relevant excerpts and patterns\n"
            "3. **Evidence From Agent Data** — relevant excerpts and patterns\n"
            "4. **Comparison** — direct contrast of the two datasets\n"
            "5. **Verdict** — does the data confirm the target problem? Cite your reasoning.\n"
            "6. **Recommendations** — concrete next steps for the design team"
        )

    def _build_freerange_task(self, bounds: UserBounds) -> str:
        """
        Free-range mode: grants broad discovery latitude while keeping results
        within UserBounds to prevent an unfocused wall of text.
        """
        return (
            "## Analysis Mode: FREE-RANGE\n\n"
            "Perform open-ended discovery across both datasets. You are looking for "
            "anything interesting: exploits, strategic divergences, bugs, or unexpected "
            "agent behaviour.\n\n"
            f"{bounds.to_prompt_fragment()}\n\n"
            "Produce your report with the following sections:\n"
            "1. **Executive Summary** — 3–5 bullet points of the most important findings\n"
            "2. **Exploits & Unintended Strategies** — list each with supporting data\n"
            "3. **Behavioural Divergences** — where human and agent strategies differ most\n"
            "4. **Potential Bugs** — data anomalies that suggest implementation errors\n"
            "5. **Recommendations** — ranked by severity"
        )
