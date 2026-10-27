"""
UserBounds — MODEL  (Free-Range analysis mode)

Defines the soft guardrails for an open-ended comparative analysis where the
researcher does NOT have a specific bug in mind.  The LLM is told to explore
freely but stay within these boundaries to keep results actionable.

Free-Range mode is for discovery — use Controlled mode once you have a lead.
"""


class UserBounds:
    """
    Parameters
    ----------
    game_parameters : str
        Plain-text description of game rules and systems the LLM needs as
        domain context to interpret the data correctly.
    scope_limit : str, optional
        Explicit exclusions (e.g. "ignore tutorial levels").
    output_format : str, optional
        Preferred report structure hint.
    max_findings : int, optional
        Cap on the number of reported findings; prevents information overload.
    priority_hint : str, optional
        Which class of finding matters most (e.g. "economy exploits").
    """

    _DEFAULT_FORMAT = (
        "structured Markdown report with sections: "
        "Summary, Exploits Found, Behavioural Differences, Potential Bugs, Recommendations"
    )

    def __init__(
        self,
        game_parameters: str,
        scope_limit: str = "",
        output_format: str = "",
        max_findings: int = 10,
        priority_hint: str = "",
    ):
        if not game_parameters:
            raise ValueError("UserBounds: game_parameters is required")

        self.game_parameters = game_parameters
        self.scope_limit     = scope_limit
        self.output_format   = output_format or self._DEFAULT_FORMAT
        self.max_findings    = max_findings
        self.priority_hint   = priority_hint

    def to_prompt_fragment(self) -> str:
        """
        Serialises the bounds into a self-contained block of text that
        LLMConnector injects directly into the user message.
        """
        parts = [
            f"GAME PARAMETERS: {self.game_parameters}",
            f"OUT OF SCOPE: {self.scope_limit}" if self.scope_limit else "",
            f"MAXIMUM FINDINGS TO REPORT: {self.max_findings}",
            f"PRIORITISE: {self.priority_hint}" if self.priority_hint else "",
            f"OUTPUT FORMAT: {self.output_format}",
        ]
        return "\n".join(p for p in parts if p)
