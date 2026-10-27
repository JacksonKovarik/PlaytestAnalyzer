"""
PlaytestSet — MODEL

Encapsulates a paired set of playtesting data: one uploaded file from human
testers and one from an agentic (AI) tester.  Both arrive as Streamlit
UploadedFile objects and are held in session state for the lifetime of a
single analysis run.

Deliberately does NO parsing — its only job is clean, validated storage and a
single extraction method used by DataConnector.
"""

from datetime import date
from streamlit.runtime.uploaded_file_manager import UploadedFile


class PlaytestSet:
    """
    Parameters
    ----------
    human_file : UploadedFile
        Streamlit file object for the human playtest dataset.
    agent_file : UploadedFile
        Streamlit file object for the agentic playtest dataset.
    game_name : str
        Name of the game being analysed.
    test_date : str, optional
        ISO-8601 date string (YYYY-MM-DD); defaults to today.
    """

    def __init__(
        self,
        human_file: UploadedFile,
        agent_file: UploadedFile,
        game_name: str,
        test_date: str = "",
    ):
        if not human_file:
            raise ValueError("PlaytestSet: human_file is required")
        if not agent_file:
            raise ValueError("PlaytestSet: agent_file is required")
        if not game_name:
            raise ValueError("PlaytestSet: game_name is required")

        self.human_file = human_file
        self.agent_file = agent_file
        self.game_name  = game_name
        self.test_date  = test_date or date.today().isoformat()

        # Convenience attributes for display without re-reading the buffer
        self.human_file_name = human_file.name
        self.agent_file_name = agent_file.name

    def extract_contents(self) -> dict[str, str]:
        """
        Return the raw UTF-8 text content of both files.

        DataConnector calls this once to pull the strings before building the
        LLM prompt.  Decoding errors fall back to latin-1 so binary-encoded
        CSVs don't crash the pipeline.

        Returns
        -------
        dict with keys 'human_content' and 'agent_content'
        """
        human_bytes = self.human_file.read()
        self.human_file.seek(0)  # rewind so the file can be re-read if needed

        agent_bytes = self.agent_file.read()
        self.agent_file.seek(0)

        return {
            "human_content": human_bytes.decode("utf-8", errors="replace"),
            "agent_content": agent_bytes.decode("utf-8", errors="replace"),
        }

    def to_metadata(self) -> dict:
        """Plain dict summary safe to display or log — no file bytes."""
        return {
            "game_name":       self.game_name,
            "test_date":       self.test_date,
            "human_file_name": self.human_file_name,
            "agent_file_name": self.agent_file_name,
        }
