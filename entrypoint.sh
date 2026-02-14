#!/bin/bash

# Create database file if it doesn't exist
if [ ! -f /app/musiccat.db ]; then
    touch /app/musiccat.db
fi

# Run the Flask app
exec python app.py
