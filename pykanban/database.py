import uuid
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Any, TypeVar

from PyQt6.QtSql import QSqlDatabase, QSqlError, QSqlQuery

T = TypeVar("T", bound="DatabaseManager")

# ==========================================================================================
# ==========================================================================================

# File:    database.py
# Date:    June 04, 2023
# Author:  Jonathan A. Webb
# Purpose: This file contains classes that implement local and shared databases for the
#          PyQt6 library
# ==========================================================================================
# ==========================================================================================
# Insert Code here


@dataclass
class QueryResult:
    """Container for database query results

    Attributes:
        success (bool): Indicates if operation completed successfully
        data (Any): Contains query results - could be None, single value, list,
                    or other data structure depending on query type
       message (str): Description of operation result or error message if
                      unsuccessful
    """

    success: bool
    data: Any
    message: str


# ==========================================================================================
# ==========================================================================================


class DatabaseManager(ABC):
    """Abstract base class defining interface for database operations"""

    @abstractmethod
    def __init__(self, db_name: str, **kwargs):
        """Initialize database connection

        Args:
            db_name (str): Database name/path
            **kwargs: Additional database-specific connection parameters like:
                hostname (str): Database server hostname
                username (str): Database user
                password (str): User password
                port (int): Server port
        """
        pass

    # ------------------------------------------------------------------------------------------

    @contextmanager
    def connection(self):
        """Context manager for database connections

        Returns:
            SQLiteManager: Database manager with active connection
        """
        success = self.open_db()
        if not success.success:
            raise QSqlError(success.message)
        try:
            yield self
        finally:
            self.close_db()

    # ------------------------------------------------------------------------------------------

    @abstractmethod
    def open_db(self) -> QueryResult:
        """Open database connection

        Returns:
            QueryResult:
                success (bool): True if connection opened
                data (None): No data returned
                message (str): Description of result
        """
        pass

    # ------------------------------------------------------------------------------------------

    @abstractmethod
    def close_db(self) -> QueryResult:
        """Close database connection

        Returns:
            QueryResult:
                success (bool): True if connection closed
                data (None): No data returned
                message (str): Description of result
        """
        pass

    # ------------------------------------------------------------------------------------------

    @abstractmethod
    def execute_query(self, query: str, params: tuple = None) -> QueryResult:
        """Execute query within transaction. Must call begin_transaction() first.

        Args:
            query (str): SQL query string
            params (tuple, optional): Query parameters. Defaults to None.

        Returns:
            QueryResult:
                success (bool): True if query executed
                data (Any): Query results if applicable
                message (str): Description of result
        """
        pass

    # ------------------------------------------------------------------------------------------

    @abstractmethod
    def safe_execute_query(self, query: str, params: tuple = None) -> QueryResult:
        """Execute single query with automatic transaction handling

        Args:
            query (str): SQL query string
            params (tuple, optional): Query parameters. Defaults to None.

        Returns:
            QueryResult:
                success (bool): True if query executed and committed
                data (Any): Query results if applicable
                message (str): Description of result
        """
        pass

    # ------------------------------------------------------------------------------------------

    @abstractmethod
    def table_schema(self, table_name: str) -> QueryResult:
        """Get schema for specified table

        Args:
            table_name (str): Name of table to query

        Returns:
            QueryResult:
                success (bool): True if schema retrieved
                data (dict): Column names and types
                message (str): Description of result
        """
        pass

    # ------------------------------------------------------------------------------------------

    @abstractmethod
    def db_schema(self) -> QueryResult:
        """Get schema for entire database

        Returns:
            QueryResult:
                success (bool): True if schema retrieved
                data (dict): Tables, column names and types
                message (str): Description of result
        """
        pass

    # ------------------------------------------------------------------------------------------

    @abstractmethod
    def create_table(
        self, table_name: str, column_names: list[str], data_types: list[str]
    ) -> QueryResult:
        """Create new database table

        Args:
            table_name (str): Name of table to create
            column_names (list[str]): List of column names
            data_types (list[str]): List of SQL data types for columns

        Returns:
            QueryResult:
                success (bool): True if table created
                data (None): No data returned
                message (str): Description of result
        """
        pass

    # ------------------------------------------------------------------------------------------

    @abstractmethod
    def table_exists(self, table_name: str) -> QueryResult:
        """Check if table exists in database

        Args:
            table_name (str): Name of table to check

        Returns:
            QueryResult:
                success (bool): True if check completed
                data (bool): True if table exists
                message (str): Description of result
        """
        pass

    # ------------------------------------------------------------------------------------------

    @abstractmethod
    def remove_db(self) -> None:
        """Remove database and clean up resources"""
        pass

    # ------------------------------------------------------------------------------------------

    @abstractmethod
    def begin_transaction(self) -> QueryResult:
        """Begin database transaction

        Returns:
            QueryResult:
                success (bool): True if transaction started
                data (None): No data returned
                message (str): Description of result
        """
        pass

    # ------------------------------------------------------------------------------------------

    @abstractmethod
    def commit_transaction(self) -> QueryResult:
        """Commit current transaction

        Returns:
            QueryResult:
                success (bool): True if transaction committed
                data (None): No data returned
                message (str): Description of result
        """
        pass

    # ------------------------------------------------------------------------------------------

    @abstractmethod
    def rollback_transaction(self) -> QueryResult:
        """Rollback current transaction

        Returns:
            QueryResult:
                success (bool): True if transaction rolled back
                data (None): No data returned
                message (str): Description of result
        """
        pass


# ==========================================================================================
# ==========================================================================================


class DatabaseStatus(Enum):
    OPEN = "Database is open"
    CLOSED = "Database is closed"
    ERROR = "Database error"


# ==========================================================================================
# ==========================================================================================


class SQLiteManager(DatabaseManager):
    def __init__(self, db_name: str, connection_name: str = None, **kwargs):
        """Initialize database connection

        Args:
            db_name (str): Database name/path
            connection_name: Name for connection, defaults to uuid
            **kwargs: Additional database-specific connection parameters like:
                hostname (str): Database server hostname
                username (str): Database user
                password (str): User password
                port (int): Server port
        """
        super().__init__(db_name, **kwargs)

        if connection_name is None:
            connection_name = str(uuid.uuid4())
        self.connection_name = connection_name
        self.db_name = db_name
        self.con = QSqlDatabase.addDatabase("QSQLITE", connection_name)
        self.con.setDatabaseName(db_name)

    # ------------------------------------------------------------------------------------------

    def open_db(self) -> QueryResult:
        """Open database connection

        Returns:
            QueryResult:
                success (bool): True if connection opened
                data (None): No data returned
                message (str): Description of result
        """
        if self.con.isOpen():
            return QueryResult(
                False, DatabaseStatus.OPEN, f"{self.db_name} database is already open"
            )

        if not self.con.open():
            return QueryResult(
                False, DatabaseStatus.ERROR, f"{self.db_name} database does not exist"
            )

        return QueryResult(
            True, DatabaseStatus.OPEN, f"{self.db_name} database successfully opened"
        )

    # ------------------------------------------------------------------------------------------

    def close_db(self) -> QueryResult:
        """Close database connection

        Returns:
            QueryResult:
                success (bool): True if connection closed
                data (None): No data returned
                message (str): Description of result
        """
        if not self.con.isOpen():
            return QueryResult(
                False, DatabaseStatus.CLOSED, f"{self.db_name} database is not open"
            )
        try:
            self.con.close()
        except Exception as e:
            return QueryResult(False, DatabaseStatus.ERROR, str(e))

        return QueryResult(
            True, DatabaseStatus.CLOSED, f"{self.db_name} database successfully closed"
        )

    # ------------------------------------------------------------------------------------------

    def execute_query(self, query: str, params: tuple = None) -> QueryResult:
        """Execute query within transaction. Must call begin_transaction() first.

        Args:
            query (str): SQL query string
            params (tuple, optional): Query parameters. Defaults to None.

        Returns:
            QueryResult:
                success (bool): True if query executed
                data (Any): Query results if applicable
                message (str): Description of result
        """
        if not self.con.isOpen():
            return QueryResult(
                False, DatabaseStatus.CLOSED, f"{self.db_name} database not open"
            )

        q = QSqlQuery(self.con)
        q.prepare(query)

        if params:
            try:
                for param in params:
                    q.addBindValue(param)
            except Exception as e:
                return QueryResult(
                    False, DatabaseStatus.ERROR, f"Parameter binding failed: {str(e)}"
                )

        if not q.exec():
            return QueryResult(False, DatabaseStatus.ERROR, q.lastError().text())

        return QueryResult(True, q, "Query executed successfully")

    # ------------------------------------------------------------------------------------------

    def safe_execute_query(self, query: str, params: tuple = None) -> QueryResult:
        """Execute single query with automatic transaction handling

        Args:
            query (str): SQL query string
            params (tuple, optional): Query parameters. Defaults to None.

        Returns:
            QueryResult:
                success (bool): True if query executed and committed
                data (Any): Query results if applicable
                message (str): Description of result
        """
        begin_result = self.begin_transaction()
        if not begin_result.success:
            return begin_result

        query_result = self.execute_query(query, params)
        if not query_result.success:
            self.rollback_transaction()
            return query_result

        commit_result = self.commit_transaction()
        if not commit_result.success:
            self.rollback_transaction()
            return commit_result

        return query_result

    # ------------------------------------------------------------------------------------------

    def table_schema(self, table_name: str) -> QueryResult:
        """Get schema for specified table

        Args:
            table_name (str): Name of table to query

        Returns:
            QueryResult:
                success (bool): True if schema retrieved
                data (dict): Column names and types
                message (str): Description of result
        """
        if not self.con.isOpen():
            return QueryResult(
                False, DatabaseStatus.CLOSED, f"{self.db_name} database is not open"
            )

        query = QSqlQuery(self.con)
        query_str = f"PRAGMA table_info({table_name})"

        if not query.exec(query_str):
            return QueryResult(False, DatabaseStatus.ERROR, query.lastError().text())

        result = {}
        while query.next():
            column_name = query.value("name")
            column_type = query.value("type")
            result[column_name] = column_type

        if not result:
            return QueryResult(
                False, DatabaseStatus.ERROR, f"Table {table_name} not found"
            )

        return QueryResult(
            True, result, f"{self.db_name} queried for {table_name} schema"
        )

    # ------------------------------------------------------------------------------------------

    def db_schema(self) -> QueryResult:
        """Get schema for entire database

        Returns:
            QueryResult:
                success (bool): True if schema retrieved
                data (dict): Tables, column names and types
                message (str): Description of result
        """
        if not self.con.isOpen():
            return QueryResult(
                False, DatabaseStatus.CLOSED, f"{self.db_name} database is not open"
            )

        table_query = QSqlQuery(self.con)
        if not table_query.exec("SELECT name FROM sqlite_master WHERE type='table';"):
            return QueryResult(
                False, DatabaseStatus.ERROR, table_query.lastError().text()
            )

        result = {}
        while table_query.next():
            table_name = table_query.value("name")
            column_query = QSqlQuery(self.con)

            if not column_query.exec(f"PRAGMA table_info({table_name})"):
                return QueryResult(
                    False, DatabaseStatus.ERROR, column_query.lastError().text()
                )

            table_schema = {}
            while column_query.next():
                column_name = column_query.value("name")
                column_type = column_query.value("type")
                table_schema[column_name] = column_type
            result[table_name] = table_schema

        return QueryResult(True, result, f"{self.db_name} database schema queried")

    # ------------------------------------------------------------------------------------------

    def create_table(
        self, table_name: str, column_names: list[str], data_types: list[str]
    ) -> QueryResult:
        """Create new database table

        Args:
            table_name (str): Name of table to create
            column_names (list[str]): List of column names
            data_types (list[str]): List of SQL data types for columns

        Returns:
            QueryResult:
                success (bool): True if table created
                data (None): No data returned
                message (str): Description of result
        """
        if not self.con.isOpen():
            return QueryResult(
                False, DatabaseStatus.CLOSED, f"{self.db_name} database is not open"
            )

        if len(column_names) != len(data_types):
            return QueryResult(
                False,
                DatabaseStatus.ERROR,
                "Column names and data types lists must be of same length",
            )

        column_query_parts = [
            f"{name} {type}" for name, type in zip(column_names, data_types)
        ]
        column_query = ", ".join(column_query_parts)
        query_str = f"CREATE TABLE {table_name} ({column_query});"

        query = QSqlQuery(self.con)
        if not query.exec(query_str):
            return QueryResult(
                False,
                DatabaseStatus.ERROR,
                f"Failed to create table {table_name}: {query.lastError().text()}",
            )

        return QueryResult(
            True, DatabaseStatus.OPEN, f"Table {table_name} successfully created"
        )

    # ------------------------------------------------------------------------------------------

    def table_exists(self, table_name: str) -> QueryResult:
        """Check if table exists in database

        Args:
            table_name (str): Name of table to check

        Returns:
            QueryResult:
                success (bool): True if check completed
                data (DatabaseStatus): True if table exists
                message (str): Description of result
        """
        if not self.con.isOpen():
            return QueryResult(
                False, DatabaseStatus.CLOSED, f"{self.db_name} database is not open"
            )

        query = QSqlQuery(self.con)
        query_str = (
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
        )

        if not query.exec(query_str):
            return QueryResult(False, DatabaseStatus.ERROR, query.lastError().text())

        if query.next():
            return QueryResult(
                True, DatabaseStatus.OPEN, f"Table {table_name} exists in {self.db_name}"
            )

        return QueryResult(
            False,
            DatabaseStatus.ERROR,
            f"Table {table_name} does not exist in {self.db_name}",
        )

    # ------------------------------------------------------------------------------------------

    def remove_db(self) -> None:
        """Remove database and clean up resources"""
        if self.con.isOpen():
            self.close_db()
        QSqlDatabase.removeDatabase(self.con.connectionName())

    # ------------------------------------------------------------------------------------------

    def begin_transaction(self) -> QueryResult:
        """Begin database transaction

        Returns:
            QueryResult:
                success (bool): True if transaction started
                data (None): No data returned
                message (str): Description of result
        """
        if not self.con.isOpen():
            return QueryResult(
                False, DatabaseStatus.CLOSED, f"{self.db_name} database not open"
            )

        if not self.con.transaction():
            return QueryResult(False, DatabaseStatus.ERROR, "Failed to start transaction")

        return QueryResult(True, DatabaseStatus.OPEN, "Transaction started")

    # ------------------------------------------------------------------------------------------

    def commit_transaction(self) -> QueryResult:
        """Commit current transaction

        Returns:
            QueryResult:
                success (bool): True if transaction committed
                data (None): No data returned
                message (str): Description of result
        """
        if not self.con.isOpen():
            return QueryResult(
                False, DatabaseStatus.CLOSED, f"{self.db_name} database not open"
            )

        if not self.con.commit():
            return QueryResult(
                False, DatabaseStatus.ERROR, "Failed to commit transaction"
            )

        return QueryResult(True, DatabaseStatus.OPEN, "Transaction committed")

    # ------------------------------------------------------------------------------------------

    def rollback_transaction(self) -> QueryResult:
        """Rollback current transaction

        Returns:
            QueryResult:
                success (bool): True if transaction rolled back
                data (None): No data returned
                message (str): Description of result
        """
        if not self.con.isOpen():
            return QueryResult(
                False, DatabaseStatus.CLOSED, f"{self.db_name} database not open"
            )

        if not self.con.rollback():
            return QueryResult(
                False, DatabaseStatus.ERROR, "Failed to rollback transaction"
            )

        return QueryResult(True, DatabaseStatus.OPEN, "Transaction rolled back")


# ==========================================================================================
# ==========================================================================================
# eof
