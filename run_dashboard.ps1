# Run the dashboard
Write-Host "Starting Database Dashboard..." -ForegroundColor Green
streamlit run src/dashboard.py --server.port=8502 --server.address=0.0.0.0
