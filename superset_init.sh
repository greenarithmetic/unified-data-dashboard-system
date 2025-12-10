#!/bin/bash

# Superset initialization script for Unified Data Dashboard System

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! nc -z postgres 5432; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Initialize Superset database
echo "Initializing Superset database..."
superset db upgrade

# Create admin user if it doesn't exist
echo "Creating admin user..."
if ! superset fab list-users | grep -q "admin@example.com"; then
    superset fab create-admin \
        --username admin \
        --firstname Admin \
        --lastname User \
        --email admin@example.com \
        --password admin
fi

# Load examples (optional)
# echo "Loading examples..."
# superset load_examples

# Initialize Superset
echo "Initializing Superset..."
superset init

# Create database connection to our UDDS PostgreSQL
echo "Creating database connection to UDDS PostgreSQL..."
python3 << EOF
import superset.utils.database as database_utils
from superset import app

with app.app_context():
    # Check if connection already exists
    from superset.connectors.sqla.models import Database
    from superset.extensions import db
    
    existing_db = db.session.query(Database).filter_by(database_name="UDDS PostgreSQL").first()
    
    if not existing_db:
        print("Creating new database connection...")
        database_utils.get_or_create_db(
            "UDDS PostgreSQL",
            "postgresql+psycopg2://postgres:postgres@postgres:5432/udds",
        )
        print("Database connection created!")
    else:
        print("Database connection already exists")
EOF

# Start Superset
echo "Starting Superset..."
exec superset run -p 8088 --with-threads --reload --debugger --host=0.0.0.0