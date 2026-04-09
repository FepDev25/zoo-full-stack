"""Initial schema - full database creation

Revision ID: 001_initial
Revises:
Create Date: 2026-04-09

"""

from pathlib import Path

from alembic import op

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None

SCHEMA_SQL = Path(__file__).parent / "01_initial_schema.sql"


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.execute(SCHEMA_SQL.read_text())


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS
            inventory_movements, inventory_items, supply_categories, suppliers,
            sponsorships, sponsors,
            show_animals, shows,
            tickets, visitors, ticket_types,
            feeding_schedules, diets,
            medical_vaccinations, vaccines, medical_records,
            animal_transfers, animals, enclosures, zones, species,
            employee_roles, employees, roles, departments
        CASCADE;
        """
    )
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;")
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp";')
