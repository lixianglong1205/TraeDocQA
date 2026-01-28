import streamlit as st
from utils.config import load_env_vars
from ui.main import main


def initialize_app():
    """
    Initialize the application
    """
    try:
        # Load environment variables
        load_env_vars()
    except ValueError as e:
        st.error(f"Environment configuration error: {e}")
        st.stop()


if __name__ == "__main__":
    initialize_app()
    main()