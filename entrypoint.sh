#!/bin/bash

# Create database file if it doesn't exist
if [ ! -f musiccat.db ]; then
    touch musiccat.db
fi

# Run the Flask app
exec python app.py
