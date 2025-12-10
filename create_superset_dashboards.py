#!/usr/bin/env python3
"""
Script to create Superset dashboards for Unified Data Dashboard System
This script creates basic dashboards and charts for analyzing data from Google Sheets
"""

import os
import sys
import time
import json
from typing import Dict, List, Any

# Add Superset to path
sys.path.insert(0, "/workspace/superset")

from superset import app
from superset.extensions import db
from superset.connectors.sqla.models import SqlaTable, TableColumn
from superset.models.core import Database
from superset.models.dashboard import Dashboard
from superset.models.slice import Slice
from superset.utils.core import get_or_create_db

def create_database_connection() -> Database:
    """Create or get database connection to UDDS PostgreSQL"""
    print("Setting up database connection...")
    
    with app.app_context():
        # Get or create database connection
        database = get_or_create_db(
            "UDDS PostgreSQL",
            "postgresql+psycopg2://postgres:postgres@postgres:5432/udds",
        )
        
        # Refresh database schemas
        database.get_sqla_engine().connect()
        
        return database

def create_table_metadata(database: Database, table_name: str, schema: str = "public") -> SqlaTable:
    """Create table metadata in Superset"""
    print(f"Creating table metadata for {table_name}...")
    
    with app.app_context():
        # Check if table already exists
        existing_table = (
            db.session.query(SqlaTable)
            .filter_by(table_name=table_name, schema=schema, database=database)
            .first()
        )
        
        if existing_table:
            print(f"Table {table_name} already exists, updating...")
            table = existing_table
        else:
            table = SqlaTable(
                table_name=table_name,
                schema=schema,
                database=database,
            )
            db.session.add(table)
        
        # Set table properties
        table.main_dttm_col = "created_at"
        table.description = f"Data from Google Sheets: {table_name}"
        table.filter_select_enabled = True
        table.fetch_values_predicate = None
        table.is_sqllab_view = False
        table.template_params = json.dumps({})
        
        # Save table
        db.session.commit()
        
        # Refresh columns
        print(f"Refreshing columns for {table_name}...")
        table.fetch_metadata()
        
        return table

def create_chart(
    table: SqlaTable,
    chart_type: str,
    title: str,
    viz_type: str,
    params: Dict[str, Any],
    description: str = ""
) -> Slice:
    """Create a chart in Superset"""
    print(f"Creating chart: {title}...")
    
    with app.app_context():
        # Check if chart already exists
        existing_slice = (
            db.session.query(Slice)
            .filter_by(slice_name=title, datasource_id=table.id, datasource_type="table")
            .first()
        )
        
        if existing_slice:
            print(f"Chart {title} already exists, updating...")
            slice_obj = existing_slice
        else:
            slice_obj = Slice(
                slice_name=title,
                datasource_id=table.id,
                datasource_type="table",
                viz_type=viz_type,
                params=json.dumps(params),
                description=description,
            )
            db.session.add(slice_obj)
        
        # Update chart properties
        slice_obj.params = json.dumps(params)
        slice_obj.description = description
        
        db.session.commit()
        
        return slice_obj

def create_dashboard(title: str, description: str = "") -> Dashboard:
    """Create a dashboard in Superset"""
    print(f"Creating dashboard: {title}...")
    
    with app.app_context():
        # Check if dashboard already exists
        existing_dashboard = (
            db.session.query(Dashboard)
            .filter_by(dashboard_title=title)
            .first()
        )
        
        if existing_dashboard:
            print(f"Dashboard {title} already exists, updating...")
            dashboard = existing_dashboard
        else:
            dashboard = Dashboard(
                dashboard_title=title,
                description=description,
                published=True,
            )
            db.session.add(dashboard)
        
        db.session.commit()
        
        return dashboard

def add_chart_to_dashboard(dashboard: Dashboard, chart: Slice, position: Dict[str, Any]):
    """Add a chart to a dashboard"""
    with app.app_context():
        # Get current position metadata
        position_json = json.dumps(position)
        
        # Check if chart is already in dashboard
        # (Simplified - in real implementation would update positions)
        
        # For now, just add to dashboard's slices relationship
        if chart not in dashboard.slices:
            dashboard.slices.append(chart)
            db.session.commit()
        
        print(f"Added chart '{chart.slice_name}' to dashboard '{dashboard.dashboard_title}'")

def create_udds_dashboards():
    """Create all UDDS dashboards and charts"""
    print("Starting Superset dashboard creation...")
    
    # Initialize Flask app context
    app.config.from_object("superset_config")
    
    with app.app_context():
        # Create database connection
        database = create_database_connection()
        
        # Create table metadata for our data
        table = create_table_metadata(database, "records")
        
        # Create charts for different analyses
        
        # 1. Records over time
        time_chart = create_chart(
            table=table,
            chart_type="line",
            title="Records Over Time",
            viz_type="line",
            params={
                "datasource": f"{table.id}__table",
                "viz_type": "line",
                "time_range": "No filter",
                "granularity_sqla": "created_at",
                "time_grain_sqla": "P1D",
                "metrics": [{"label": "COUNT(*)", "expressionType": "SQL", "sqlExpression": "COUNT(*)"}],
                "groupby": [],
                "adhoc_filters": [],
                "row_limit": 10000,
                "x_axis_label": "Date",
                "y_axis_label": "Number of Records",
                "color_scheme": "supersetColors",
            },
            description="Number of records created over time"
        )
        
        # 2. Records by source
        source_chart = create_chart(
            table=table,
            chart_type="bar",
            title="Records by Source",
            viz_type="dist_bar",
            params={
                "datasource": f"{table.id}__table",
                "viz_type": "dist_bar",
                "metrics": [{"label": "COUNT(*)", "expressionType": "SQL", "sqlExpression": "COUNT(*)"}],
                "groupby": ["source"],
                "adhoc_filters": [],
                "row_limit": 50,
                "color_scheme": "supersetColors",
                "show_legend": True,
                "bar_stacked": False,
            },
            description="Distribution of records by data source"
        )
        
        # 3. Spam vs Non-Spam
        spam_chart = create_chart(
            table=table,
            chart_type="pie",
            title="Spam vs Non-Spam Records",
            viz_type="pie",
            params={
                "datasource": f"{table.id}__table",
                "viz_type": "pie",
                "metrics": [{"label": "COUNT(*)", "expressionType": "SQL", "sqlExpression": "COUNT(*)"}],
                "groupby": ["is_spam"],
                "adhoc_filters": [],
                "color_scheme": "supersetColors",
                "donut": True,
                "show_legend": True,
                "labels_outside": True,
            },
            description="Percentage of spam vs non-spam records"
        )
        
        # 4. Top categories
        category_chart = create_chart(
            table=table,
            chart_type="table",
            title="Top Categories",
            viz_type="table",
            params={
                "datasource": f"{table.id}__table",
                "viz_type": "table",
                "metrics": [{"label": "COUNT(*)", "expressionType": "SQL", "sqlExpression": "COUNT(*)"}],
                "groupby": ["category"],
                "adhoc_filters": [],
                "row_limit": 20,
                "order_desc": True,
                "table_timestamp_format": "smart_date",
                "page_length": 20,
                "include_search": True,
            },
            description="Top categories by number of records"
        )
        
        # 5. Records by status
        status_chart = create_chart(
            table=table,
            chart_type="bar",
            title="Records by Status",
            viz_type="dist_bar",
            params={
                "datasource": f"{table.id}__table",
                "viz_type": "dist_bar",
                "metrics": [{"label": "COUNT(*)", "expressionType": "SQL", "sqlExpression": "COUNT(*)"}],
                "groupby": ["status"],
                "adhoc_filters": [],
                "row_limit": 20,
                "color_scheme": "supersetColors",
                "show_legend": True,
                "bar_stacked": False,
            },
            description="Distribution of records by status"
        )
        
        # Create main dashboard
        main_dashboard = create_dashboard(
            title="UDDS Analytics Dashboard",
            description="Main dashboard for analyzing data from Google Sheets"
        )
        
        # Add charts to dashboard with positions
        # Note: In production, you would use proper layout management
        charts = [
            (time_chart, {"x": 0, "y": 0, "width": 12, "height": 4}),
            (source_chart, {"x": 0, "y": 4, "width": 6, "height": 4}),
            (spam_chart, {"x": 6, "y": 4, "width": 6, "height": 4}),
            (category_chart, {"x": 0, "y": 8, "width": 8, "height": 6}),
            (status_chart, {"x": 8, "y": 8, "width": 4, "height": 6}),
        ]
        
        for chart, position in charts:
            add_chart_to_dashboard(main_dashboard, chart, position)
        
        print("\n" + "="*50)
        print("Superset dashboards created successfully!")
        print("="*50)
        print(f"Dashboard URL: http://localhost:8088/superset/dashboard/{main_dashboard.id}/")
        print(f"Admin credentials: admin / admin")
        print("="*50)

def main():
    """Main function"""
    try:
        # Wait for Superset to be ready
        print("Waiting for Superset to initialize...")
        time.sleep(30)
        
        # Create dashboards
        create_udds_dashboards()
        
    except Exception as e:
        print(f"Error creating Superset dashboards: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()