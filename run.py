import sys
import os

# Ensure the root directory is in python path so 'backend' package works
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app import app

if __name__ == '__main__':
    print("Starting Influenze Relay Backend...")
    app.run(debug=True, port=5000)
