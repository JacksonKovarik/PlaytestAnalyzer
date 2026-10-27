# Playtest Analyzer — Setup

## Quick start

```bash
# 1. Create a virtual environment (from the Phase2 root)
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your Anthropic API key
cp .env.example .env
# Edit .env and paste your key

# 4. Run the app
streamlit run app.py
```

The app opens at http://localhost:8501

## Project structure

```
Phase2/
├── app.py                          # Entry point
├── controllers/
│   ├── screen_controller.py        # All navigation / routing (ScreenController)
│   └── data_connector.py           # Orchestration layer (DataConnector)
├── models/
│   ├── playtest_set.py             # PlaytestSet — uploaded file pair + metadata
│   ├── playtest_goal.py            # PlaytestGoal — Controlled mode parameters
│   └── user_bounds.py              # UserBounds — Free-Range mode parameters
├── connectors/
│   └── llm_connector.py            # LLMConnector — Anthropic API calls
└── views/
    ├── upload_screen.py
    ├── selection_screen.py
    ├── controlled_screen.py
    ├── free_range_screen.py
    └── results_screen.py
```

## Accepted file formats

Both human and agentic dataset files can be: `.txt`, `.csv`, `.json`, `.log`

The files are read as UTF-8 text and sent directly to Claude as inline content.
No local parsing is performed.
