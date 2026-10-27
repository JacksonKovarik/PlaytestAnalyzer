"""
PlaytestGoal — MODEL  (Controlled analysis mode)

Holds the specific, scoped parameters a researcher provides when they already
know what they are looking for — e.g. "Does the agent exploit the economy
system in ways humans don't?"

Controlled mode gives the LLM a tight brief so it focuses its comparison on
the stated problem rather than doing broad discovery.
"""


class PlaytestGoal:
    """
    Parameters
    ----------
    target_problem : str
        The specific bug or behaviour to investigate.
    success_criteria : str
        What a "confirmed finding" looks like for this investigation.
    focus_areas : list[str], optional
        Sub-systems to prioritise (e.g. ["economy", "combat"]).
    context : str, optional
        Extra narrative context the LLM should hold while analysing.
    """

    def __init__(
        self,
        target_problem: str,
        success_criteria: str,
        focus_areas: list[str] | None = None,
        context: str = "",
    ):
        if not target_problem:
            raise ValueError("PlaytestGoal: target_problem is required")
        if not success_criteria:
            raise ValueError("PlaytestGoal: success_criteria is required")

        self.target_problem   = target_problem
        self.success_criteria = success_criteria
        self.focus_areas      = focus_areas or []
        self.context          = context

    def to_prompt_fragment(self) -> str:
        """
        Serialises the goal into a self-contained block of text that
        LLMConnector injects directly into the user message.
        """
        areas = f"Focus areas: {', '.join(self.focus_areas)}." if self.focus_areas else ""
        parts = [
            f"TARGET PROBLEM: {self.target_problem}",
            f"SUCCESS CRITERIA: {self.success_criteria}",
            areas,
            f"ADDITIONAL CONTEXT: {self.context}" if self.context else "",
        ]
        return "\n".join(p for p in parts if p)
