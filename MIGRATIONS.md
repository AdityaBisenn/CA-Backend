# Database Management with Alembic

## 🗄️ Migration Commands

### Quick Migration Guide

```bash
# Apply all pending migrations
./migrate.sh upgrade

# Create a new migration
./migrate.sh create "Add new table or column"

# View migration history
./migrate.sh history

# Check current migration
./migrate.sh current

# Downgrade by one step
./migrate.sh downgrade

# Reset database (⚠️ DESTRUCTIVE)
./migrate.sh reset
```

### Manual Alembic Commands

```bash
# Activate virtual environment first
source ../.venv/bin/activate

# Create migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Downgrade
alembic downgrade -1

# View history
alembic history

# Check current
alembic current
```

### Environment Configuration

Make sure your `.env` file has the correct database URL:

```bash
# For SQLite (development)
DATABASE_URL=sqlite:///./agentic_ai_data.db

# For PostgreSQL (production)
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/agentic_ai_db
```

### Migration Best Practices

1. **Always create migrations for schema changes** - Don't modify models without creating migrations
2. **Review generated migrations** - Check the generated migration file before applying
3. **Test migrations** - Test both upgrade and downgrade paths
4. **Backup before major changes** - Especially in production
5. **Use descriptive messages** - Make migration messages clear and specific

### Common Scenarios

#### Adding a New Table
1. Create the SQLAlchemy model in appropriate file under `app/cdm/models/`
2. Create the Pydantic schema in `app/cdm/schemas/`
3. Generate migration: `./migrate.sh create "Add new table"`
4. Apply migration: `./migrate.sh upgrade`

#### Adding a New Column
1. Add the column to the existing model
2. Generate migration: `./migrate.sh create "Add column to table"`
3. Apply migration: `./migrate.sh upgrade`

#### Renaming a Column
⚠️ **Be careful** - Alembic might drop and recreate the column, losing data
1. Modify the model
2. Generate migration: `./migrate.sh create "Rename column"`
3. **Review the generated migration file**
4. Manually edit if needed to preserve data
5. Apply migration: `./migrate.sh upgrade`