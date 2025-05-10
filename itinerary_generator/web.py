#!/usr/bin/env python3
"""
Web application entry point for the Itinerary Generator.
"""
import os
from itinerary_generator.app import app

if __name__ == "__main__": # pragma: no cover
    # Use environment variable to control debug mode, default to False for security
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)