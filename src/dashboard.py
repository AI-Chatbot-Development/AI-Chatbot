import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '../data/chatbot.db')

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

def get_table_names():
    """Get all table names from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]
    conn.close()
    return tables

def get_table_data(table_name):
    """Get all data from a specific table"""
    conn = get_db_connection()
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

def get_table_info(table_name):
    """Get table schema information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    conn.close()
    return columns

def get_table_count(table_name):
    """Get row count for a table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def main():
    st.set_page_config(
        page_title="Database Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #7EC143 0%, #5a9b32 50%, #4a7c28 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .table-header {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #7EC143;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 Database Dashboard</h1>
        <p>Monitor and explore your chatbot database tables</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if database exists
    if not os.path.exists(DB_PATH):
        st.error("❌ Database not found! Please make sure the chatbot application has been initialized.")
        return
    
    # Get tables
    try:
        tables = get_table_names()
    except Exception as e:
        st.error(f"❌ Error connecting to database: {e}")
        return
    
    if not tables:
        st.warning("⚠️ No tables found in the database.")
        return
    
    # Sidebar
    st.sidebar.title("🔍 Database Explorer")
    selected_table = st.sidebar.selectbox("Select a table:", ["Overview"] + tables)
    
    if selected_table == "Overview":
        show_overview(tables)
    else:
        show_table_details(selected_table)

def show_overview(tables):
    """Show overview of all tables"""
    st.header("📋 Database Overview")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Total Tables", len(tables))
    
    total_records = 0
    for table in tables:
        try:
            count = get_table_count(table)
            total_records += count
        except:
            continue
    
    with col2:
        st.metric("📝 Total Records", total_records)
    
    with col3:
        st.metric("💾 Database Size", f"{os.path.getsize(DB_PATH) / 1024:.1f} KB")
    
    # Table summary
    st.subheader("📊 Tables Summary")
    
    table_data = []
    for table in tables:
        try:
            count = get_table_count(table)
            columns = get_table_info(table)
            table_data.append({
                "Table Name": table,
                "Records": count,
                "Columns": len(columns)
            })
        except Exception as e:
            table_data.append({
                "Table Name": table,
                "Records": "Error",
                "Columns": "Error"
            })
    
    df_summary = pd.DataFrame(table_data)
    st.dataframe(df_summary, use_container_width=True)
    
    # Charts for interactions table if it exists
    if "interactions" in tables:
        show_interactions_analytics()

def show_interactions_analytics():
    """Show analytics for interactions table"""
    st.subheader("📈 Interactions Analytics")
    
    try:
        df = get_table_data("interactions")
        
        if not df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Interactions over time
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df['date'] = df['timestamp'].dt.date
                    daily_counts = df.groupby('date').size().reset_index(name='count')
                    
                    fig = px.line(daily_counts, x='date', y='count', 
                                title="Interactions Over Time")
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Match scores distribution
                if 'match_score' in df.columns and df['match_score'].notna().any():
                    fig = px.histogram(df, x='match_score', nbins=20,
                                     title="Match Score Distribution")
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading analytics: {e}")

def show_table_details(table_name):
    """Show detailed view of a specific table"""
    st.header(f"📊 Table: {table_name}")
    
    try:
        # Table info
        columns = get_table_info(table_name)
        count = get_table_count(table_name)
        
        # Metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📝 Total Records", count)
        with col2:
            st.metric("🔧 Columns", len(columns))
        
        # Schema
        st.subheader("🏗️ Table Schema")
        schema_data = []
        for col in columns:
            schema_data.append({
                "Column": col[1],
                "Type": col[2],
                "Not Null": "Yes" if col[3] else "No",
                "Default": col[4] if col[4] else "None",
                "Primary Key": "Yes" if col[5] else "No"
            })
        
        df_schema = pd.DataFrame(schema_data)
        st.dataframe(df_schema, use_container_width=True)
        
        # Data preview
        st.subheader("👀 Data Preview")
        
        if count > 0:
            # Pagination
            page_size = st.selectbox("Rows per page:", [10, 25, 50, 100], index=0)
            
            # Get data
            df = get_table_data(table_name)
            
            if not df.empty:
                total_pages = (len(df) - 1) // page_size + 1
                page = st.number_input("Page:", min_value=1, max_value=total_pages, value=1)
                
                start_idx = (page - 1) * page_size
                end_idx = start_idx + page_size
                
                st.dataframe(df.iloc[start_idx:end_idx], use_container_width=True)
                
                # Download option
                csv = df.to_csv(index=False)
                st.download_button(
                    label=f"📥 Download {table_name} as CSV",
                    data=csv,
                    file_name=f"{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No data available in this table.")
        else:
            st.info("This table is empty.")
            
    except Exception as e:
        st.error(f"❌ Error loading table data: {e}")

if __name__ == "__main__":
    main()