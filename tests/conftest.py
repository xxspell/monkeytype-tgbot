import os
import sys
import tempfile
from unittest.mock import patch

import pytest
import aiosqlite

from src.database.db import init_db, DATABASE

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))



@pytest.fixture(scope='function')
async def setup_db():
    await init_db()
    yield
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute("SELECT name FROM sqlite_master WHERE type='table';") as cursor:
            tables = await cursor.fetchall()

        for table in tables:
            table_name = table[0]
            await db.execute(f"DELETE FROM {table_name};")
            await db.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}';")  # Reset autoincrement
            print(f"Table {table_name} cleared.")

        await db.commit()


