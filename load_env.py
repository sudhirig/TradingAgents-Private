"""
Load environment variables from .env file for TradingAgents.
Import this module before running any TradingAgents code.
"""
import os
from pathlib import Path

def load_env():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent / '.env'
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print(f"Loaded environment variables from {env_path}")
    else:
        print(f"No .env file found at {env_path}")

# Auto-load when module is imported
load_env()
