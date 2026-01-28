import os
from dotenv import load_dotenv

def load_env_vars():
    """
    Load environment variables from .env file
    """
    load_dotenv()
    
    # Ensure required environment variables are set
    required_vars = ['OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return True

def get_api_key():
    """
    Get the OpenAI API key from environment
    """
    return os.getenv('OPENAI_API_KEY')