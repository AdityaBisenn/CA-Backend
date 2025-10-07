#!/bin/bash
# Migration management script for Agentic AI Layer

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Activate virtual environment
source ../.venv/bin/activate

case "$1" in
    "upgrade")
        echo -e "${GREEN}🔄 Running database migrations...${NC}"
        alembic upgrade head
        echo -e "${GREEN}✅ Database upgraded successfully!${NC}"
        ;;
    "create")
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Please provide a migration message.${NC}"
            echo "Usage: ./migrate.sh create \"Add new table\""
            exit 1
        fi
        echo -e "${YELLOW}📝 Creating new migration: $2${NC}"
        alembic revision --autogenerate -m "$2"
        echo -e "${GREEN}✅ Migration created successfully!${NC}"
        echo -e "${YELLOW}💡 Don't forget to run './migrate.sh upgrade' to apply it${NC}"
        ;;
    "downgrade")
        if [ -z "$2" ]; then
            echo -e "${YELLOW}⬇️  Downgrading by 1 revision...${NC}"
            alembic downgrade -1
        else
            echo -e "${YELLOW}⬇️  Downgrading to: $2${NC}"
            alembic downgrade "$2"
        fi
        echo -e "${GREEN}✅ Downgrade completed!${NC}"
        ;;
    "history")
        echo -e "${GREEN}📋 Migration history:${NC}"
        alembic history
        ;;
    "current")
        echo -e "${GREEN}📍 Current migration:${NC}"
        alembic current
        ;;
    "reset")
        echo -e "${RED}⚠️  This will delete the database and recreate it!${NC}"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -f agentic_ai_data.db
            alembic upgrade head
            echo -e "${GREEN}✅ Database reset successfully!${NC}"
        else
            echo -e "${YELLOW}❌ Reset cancelled${NC}"
        fi
        ;;
    *)
        echo -e "${GREEN}🗄️  Agentic AI Layer - Database Migration Manager${NC}"
        echo ""
        echo "Usage: ./migrate.sh [command] [options]"
        echo ""
        echo "Commands:"
        echo "  upgrade           Apply all pending migrations"
        echo "  create \"message\"   Create a new migration"
        echo "  downgrade [rev]   Downgrade database (1 step or to specific revision)"
        echo "  history          Show migration history"
        echo "  current          Show current migration"
        echo "  reset            Delete and recreate database"
        echo ""
        echo "Examples:"
        echo "  ./migrate.sh upgrade"
        echo "  ./migrate.sh create \"Add user preferences table\""
        echo "  ./migrate.sh downgrade"
        echo "  ./migrate.sh reset"
        ;;
esac