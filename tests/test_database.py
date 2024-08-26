# tests/test_database.py
import pytest
from app.database import Database
from unittest.mock import patch

@pytest.fixture
def db():
    with patch('app.database.psycopg2.pool.SimpleConnectionPool'):
        db = Database()
    return db

# Тесты для работы с базой данных
# ...
