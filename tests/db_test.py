import os

import pytest
from PyQt6.QtWidgets import QApplication

from pykanban.database import DatabaseStatus, SQLiteManager

# ==========================================================================================
# ==========================================================================================
# File:    test.py
# Date:    January 21, 2025
# Author:  Jonathan A. Webb
# Purpose: Describe the types of testing to occur in this file.
# Instruction: This code can be run in hte following ways
# ==========================================================================================
# ==========================================================================================
# TEST FIXTURES


# Create QApplication instance for the tests
@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance"""
    app = QApplication([])
    yield app
    app.quit()


# ------------------------------------------------------------------------------------------


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database path"""
    db_file = tmp_path / "test.db"
    return str(db_file)


# ------------------------------------------------------------------------------------------


@pytest.fixture
def db_manager(qapp, temp_db_path):
    """Create a database manager instance"""
    manager = SQLiteManager(temp_db_path)
    yield manager
    manager.remove_db()
    if os.path.exists(temp_db_path):
        os.remove(temp_db_path)


# ==========================================================================================
# ==========================================================================================
# TEST CODE


def test_open_close_db(db_manager):
    """Test opening and closing database connection"""
    # Test opening
    result = db_manager.open_db()
    assert result.success is True
    assert result.data == DatabaseStatus.OPEN

    # Test reopening (should fail)
    result = db_manager.open_db()
    assert result.success is False

    # Test closing
    result = db_manager.close_db()
    assert result.success is True
    assert result.data == DatabaseStatus.CLOSED


# ------------------------------------------------------------------------------------------


def test_create_table(db_manager):
    """Test table creation"""
    with db_manager.connection():
        result = db_manager.create_table(
            "test_table",
            ["id", "name", "age"],
            ["INTEGER PRIMARY KEY", "TEXT", "INTEGER"],
        )
        assert result.success is True

        # Verify table exists
        exists_result = db_manager.table_exists("test_table")
        assert exists_result.success is True
        assert exists_result.data is DatabaseStatus.OPEN


# ------------------------------------------------------------------------------------------


def test_execute_query(db_manager):
    """Test query execution"""
    with db_manager.connection():
        # Create table
        create_result = db_manager.create_table(
            "users", ["id", "name", "age"], ["INTEGER PRIMARY KEY", "TEXT", "INTEGER"]
        )
        assert create_result.success is True

        # Insert data
        insert_query = "INSERT INTO users (name, age) VALUES (?, ?)"
        result = db_manager.safe_execute_query(insert_query, ("John Doe", 30))
        assert result.success is True

        # Select data
        select_query = "SELECT name, age FROM users WHERE age = ?"
        result = db_manager.safe_execute_query(select_query, (30,))
        assert result.success is True

        # Verify result
        query = result.data
        assert query.next() is True
        assert query.value("name") == "John Doe"
        assert query.value("age") == 30


# ------------------------------------------------------------------------------------------


def test_transaction_handling(db_manager):
    """Test transaction management"""
    with db_manager.connection():
        # Create table
        db_manager.create_table(
            "transactions", ["id", "value"], ["INTEGER PRIMARY KEY", "INTEGER"]
        )

        # Start transaction
        begin_result = db_manager.begin_transaction()
        assert begin_result.success is True

        # Execute query within transaction
        insert_result = db_manager.execute_query(
            "INSERT INTO transactions (value) VALUES (?)", (42,)
        )
        assert insert_result.success is True

        # Commit transaction
        commit_result = db_manager.commit_transaction()
        assert commit_result.success is True

        # Verify data was saved
        select_result = db_manager.safe_execute_query(
            "SELECT value FROM transactions WHERE value = ?", (42,)
        )
        assert select_result.success is True
        query = select_result.data
        assert query.next() is True
        assert query.value("value") == 42


# ------------------------------------------------------------------------------------------


def test_schema_operations(db_manager):
    """Test schema-related operations"""
    with db_manager.connection():
        # Create test table
        db_manager.create_table(
            "schema_test",
            ["id", "name", "value"],
            ["INTEGER PRIMARY KEY", "TEXT", "REAL"],
        )

        # Test table schema
        schema_result = db_manager.table_schema("schema_test")
        assert schema_result.success is True
        assert "id" in schema_result.data
        assert "name" in schema_result.data
        assert "value" in schema_result.data

        # Test database schema
        db_schema_result = db_manager.db_schema()
        assert db_schema_result.success is True
        assert "schema_test" in db_schema_result.data


# ------------------------------------------------------------------------------------------


def test_error_handling(db_manager):
    """Test error handling scenarios"""
    # Test querying closed database
    result = db_manager.execute_query("SELECT 1")
    assert result.success is False
    assert result.data == DatabaseStatus.CLOSED

    # Test invalid SQL
    with db_manager.connection():
        result = db_manager.safe_execute_query("INVALID SQL")
        assert result.success is False
        assert result.data == DatabaseStatus.ERROR

    # Test accessing non-existent table
    with db_manager.connection():
        result = db_manager.table_schema("nonexistent_table")
        assert result.success is False


# ==========================================================================================
# ==========================================================================================
# eof
