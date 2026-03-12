#!/bin/bash

echo "🚀 Starting Project Management Dashboard..."
echo ""
echo "This will launch the Streamlit dashboard at:"
echo "http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server."
echo ""
echo "Starting in 3 seconds..."
sleep 3

cd "$(dirname "$0")"
streamlit run app.py
