# Database Dashboard

This dashboard provides a simple interface to view and monitor your chatbot's database tables.

## Features

- **Database Overview**: View summary statistics of all tables
- **Table Explorer**: Browse individual tables with pagination
- **Schema Information**: View table structures and column details
- **Data Export**: Download table data as CSV files
- **Analytics**: Interactive charts for interaction data
- **Real-time Data**: Always shows the latest database state

## Running the Dashboard

### Option 1: Using Docker Compose (Recommended)

```bash
# Start both the main app and dashboard
docker-compose up

# Or start only the dashboard
docker-compose up dashboard
```

The dashboard will be available at: http://localhost:8502

### Option 2: Using Streamlit Directly

```bash
# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run src/dashboard.py --server.port=8502
```

### Option 3: Using the Scripts

**Windows PowerShell:**

```powershell
.\run_dashboard.ps1
```

**Linux/Mac:**

```bash
./run_dashboard.sh
```

## Dashboard Sections

### 1. Overview Page

- Total number of tables
- Total records across all tables
- Database file size
- Summary table with record counts
- Interactive analytics for the interactions table

### 2. Table Details

- Complete table schema
- Data preview with pagination
- CSV download functionality
- Record count and column information

## Database Tables

The dashboard automatically detects and displays:

- **interactions**: User queries, bot responses, match scores, feedback
- **escalations**: Queries that needed human intervention
- Any other tables in your SQLite database

## Troubleshooting

1. **Database not found**: Make sure your main chatbot application has been run at least once to create the database
2. **Connection errors**: Ensure the database file is accessible and not locked by another process
3. **Port conflicts**: Change the port in the command if 8502 is already in use

## Technologies Used

- **Streamlit**: Web interface framework
- **SQLite**: Database system
- **Pandas**: Data manipulation
- **Plotly**: Interactive charts
- **Docker**: Containerization
