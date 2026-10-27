"""
app.py — Entry Point

Boots the Streamlit application and hands control to ScreenController, which
owns all routing logic for the duration of the session.

Run:  streamlit run app.py
"""

from dotenv import load_dotenv

load_dotenv()  # loads ANTHROPIC_API_KEY from .env before any Anthropic SDK import

from controllers.screen_controller import ScreenController  # noqa: E402 (must be after load_dotenv)

import streamlit as st  # noqa: E402

st.set_page_config(
    page_title="Playtest Analyzer",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed",
)

controller = ScreenController()
controller.render()
