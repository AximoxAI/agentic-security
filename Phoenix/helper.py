import os
from dotenv import load_dotenv, find_dotenv
import phoenix as px

def load_env():
    load_dotenv(find_dotenv(), override=True)

def get_openai_api_key():
    load_env()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    return openai_api_key

def get_phoenix_endpoint():
    """Returns the Phoenix UI endpoint - no need to set PHOENIX_COLLECTOR_ENDPOINT"""
    return "http://localhost:6006/"

def setup_phoenix():
    """Properly sets up Phoenix without collector endpoint issues"""
    load_env()
    
    # Make sure no collector endpoint is set (this was causing your issue)
    if 'PHOENIX_COLLECTOR_ENDPOINT' in os.environ:
        del os.environ['PHOENIX_COLLECTOR_ENDPOINT']
    
    # Launch Phoenix app
    session = px.launch_app(run_in_thread=True)
    print(f"Phoenix is running at: {get_phoenix_endpoint()}")
    return session