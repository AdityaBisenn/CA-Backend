#!/bin/bash

# Script to populate database with test data for frontend testing

echo "Populating database with test data..."

# Activate virtual environment and run population script
source .venv/bin/activate
python -m app.utils.populate_db

echo "Test data population completed!"
echo ""
echo "You can now test the frontend with the following credentials:"
echo "================================="
echo "Super Admin (Platform Admin):"
echo "  Email: admin@trenor.ai"
echo "  Password: admin123"
echo ""
echo "CA Firm Admin:"
echo "  Email: admin@testcafirm.com"
echo "  Password: cafirm123"
echo ""
echo "CA Staff:"
echo "  Email: staff@testcafirm.com"
echo "  Password: staff123"
echo "================================="