import pytest
from dotenv import dotenv_values
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


@pytest.mark.asyncio
async def test_database_connection():
    test_url = dotenv_values(".env.test").get("TEST_DATABASE_URL")
    assert test_url, "postgresql+psycopg_async://taskmanager:0001@127.0.0.1:5432/taskmanager_test"

    engine = create_async_engine(test_url)

    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            assert result.scalar_one() == 1
    finally:
        await engine.dispose()