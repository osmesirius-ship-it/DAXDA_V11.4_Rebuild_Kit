"""Passenger WSGI entry point for Hostinger Python Application setup.

Hostinger's Phusion Passenger server looks for `application` in this file.
"""
import sys
import os

# Ensure current directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app as application, USE_FLASK

if not USE_FLASK:
    from app import application
