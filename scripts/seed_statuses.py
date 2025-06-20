import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSessionLocal # Changed from async_session_maker
from models.status import Status

# List of required status names
STATUS_NAMES = [
    "В строю",
    "На дежурстве",
    "После дежурства",
    "В командировке",
    "Учёба / Соревнования / Конференция",
    "В отпуске",
    "На больничном",
    "Прикомандирован",
    "Откомандирован",
]


async def seed_statuses(db_session: AsyncSession):
    """
    Seeds the statuses table with predefined status names.

    Args:
        db_session: The SQLAlchemy async session.
    """
    for status_name in STATUS_NAMES:
        # Check if the status already exists
        result = await db_session.execute(
            select(Status).where(Status.nameRU == status_name)
        )
        existing_status = result.scalars().first()

        if not existing_status:
            # If it doesn't exist, add a new record
            new_status = Status(nameRU=status_name, nameEN="", nameKZ="")  # Or None for nameEN, nameKZ
            db_session.add(new_status)
            print(f"Added status: {status_name}")
        else:
            print(f"Status already exists: {status_name}")

    await db_session.commit()
    print("Status seeding finished.")


async def main():
    """Main function to run the seeder."""
    print("Starting status seeding...")
    async with AsyncSessionLocal() as session: # Changed from async_session_maker
        await seed_statuses(session)


if __name__ == "__main__":
    # To run this seeder:
    # Ensure your database connection is configured in core/database.py
    # Then execute this script from the root of your project:
    # python -m scripts.seed_statuses
    #
    # Note: If you have a specific way to run alembic or other scripts
    # that set up the environment, adapt the execution command accordingly.
    # For example, if you use a manage.py or similar script, you might integrate this seeder there.
    asyncio.run(main())
