# Alembic Migration Guide

This guide explains how to use Alembic for database migrations in this project.

## Setup

1. Install Alembic:

```bash
pip install alembic
```

2. Make sure it's added to your requirements.txt:

```
alembic==1.10.3
```

## Creating Migrations

### Automatic Migration Generation

Alembic can automatically detect changes between your SQLAlchemy models and the current database schema:

```bash
# From the backend directory
alembic revision --autogenerate -m "Description of changes"
```

For example:

```bash
alembic revision --autogenerate -m "Update contact model"
```

This will create a new migration file in `alembic/versions/` with the changes detected.

### Manual Migration Creation

You can also create a blank migration file and edit it manually:

```bash
alembic revision -m "Description of changes"
```

## Applying Migrations

To apply all pending migrations:

```bash
alembic upgrade head
```

To apply migrations up to a specific revision:

```bash
alembic upgrade <revision_id>
```

## Rolling Back Migrations

To rollback the most recent migration:

```bash
alembic downgrade -1
```

To rollback to a specific revision:

```bash
alembic downgrade <revision_id>
```

To rollback all migrations:

```bash
alembic downgrade base
```

## Migration History

To see the migration history:

```bash
alembic history
```

## Current Database Status

To see the current revision:

```bash
alembic current
```

## Initial Database Setup

If you're starting with a new database, run:

```bash
alembic stamp head
```

This marks all existing migrations as applied without actually running them.

## Working with Existing Tables

If you have existing tables that were created without Alembic:

1. Create a migration that represents your current schema
2. Run `alembic stamp head` to mark it as applied
3. Then make changes to your models and generate new migrations
