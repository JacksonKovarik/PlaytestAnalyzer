# PlaytestAnalyzer

A game playtesting analysis tool that compares **human playtester data** against **agentic (AI) playtester data** to identify strategic differences, exploits, and bugs — powered by Claude.

## What it does

Game studios increasingly use AI agents to run playtesting sessions at scale. PlaytestAnalyzer bridges the gap between human intuition and agentic throughput by sending both datasets directly to an LLM, which acts as a neutral **Comparison Engine** to surface:

- Exploits and unintended strategies the agent discovered that humans missed
- Significant behavioural divergences between human and agent play patterns
- Data anomalies that suggest underlying bugs (impossible values, missing state transitions, etc.)

Two analysis modes let you tailor the depth of investigation:

| Mode | When to use |
|---|---|
| **Controlled** | You have a specific hypothesis — provide a target problem and success criteria, and the engine focuses entirely on confirming or ruling it out |
| **Free-Range** | You have no hypothesis yet — provide general game parameters and let the engine explore both datasets for anything interesting |

## Architecture

Strict MVC pattern implemented in Python/Streamlit:

```
Phase2/
├── app.py                      # Entry point
├── controllers/
│   ├── screen_controller.py    # Central router — owns all st.session_state writes
│   └── data_connector.py       # Orchestration layer between UI and LLM
├── models/
│   ├── playtest_set.py         # Encapsulates the uploaded file pair + metadata
│   ├── playtest_goal.py        # Controlled mode parameters
│   └── user_bounds.py          # Free-Range mode parameters
├── connectors/
│   └── llm_connector.py        # Anthropic API calls + prompt construction
└── views/                      # One file per screen (5 screens total)
```

## Getting started

**Prerequisites:** Python 3.11+, an [Anthropic API key](https://console.anthropic.com/)

```bash
# 1. Clone the repo
git clone https://github.com/jacksonkovarik/PlaytestAnalyzer.git
cd PlaytestAnalyzer

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
cp .env.example .env
# Open .env and set: ANTHROPIC_API_KEY=your_key_here

# 5. Run the app
streamlit run app.py
```

The app opens at **http://localhost:8501**

## Accepted dataset formats

Both the human and agentic dataset files can be `.txt`, `.csv`, `.json`, or `.log`.  
The files are read as UTF-8 text and sent directly to Claude — no local parsing is performed.

## Future plans

- **Local dataset parsing** — structured ingest of common game-engine telemetry formats (Unity Analytics, Unreal Insights CSV exports) with pre-analysis normalization before the LLM call
- **Session history** — persist past analysis runs to a local SQLite database so results can be reviewed and compared across builds
- **Diff mode** — compare two analysis reports from different game versions to track whether a patch actually fixed a flagged exploit
- **Multi-dataset support** — accept more than one file per side (e.g. 10 human sessions aggregated), with a preprocessing step that merges them before analysis
- **Configurable model** — surface model selection in the UI so teams can trade off speed vs. depth (Haiku for quick scans, Opus for deep investigations)
- **Export formats** — download reports as PDF or structured JSON in addition to Markdown
