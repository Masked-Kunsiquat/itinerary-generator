#!/usr/bin/env python3
"""
Web application entry point for the Itinerary Generator.
"""
from itinerary_generator.app import app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)