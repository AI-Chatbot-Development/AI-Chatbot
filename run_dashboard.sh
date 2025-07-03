#!/bin/bash

# Run the dashboard
echo "Starting Database Dashboard..."
streamlit run src/dashboard.py --server.port=8502 --server.address=0.0.0.0
