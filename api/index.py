import os
import sys

# Add the backend directory to sys.path so it can find 'app'
backend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend")
sys.path.insert(0, backend_dir)

from app.main import app
