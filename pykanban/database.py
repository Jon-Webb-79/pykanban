import logging
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


class KanbanDatabaseManager:
    """
    Class that implements Kanban-specific database operations using SQLiteManager

    :param db_path: Path to the SQLite database file
    :param log: Logger instance for tracking operations
    """

    def __init__(self, db_path: str, log: logging.Logger):
        self.db_path = db_path
        self.log = log
        self.db_manager = SQLiteManager(db_path)

    # ------------------------------------------------------------------------------------------

    def initialize_database(self) -> QueryResult:
        """Create initial schema for a new Kanban database with default columns"""
        create_columns_table = """
            CREATE TABLE Columns (
            Name TEXT PRIMARY KEY,
            "Order" INTEGER NOT NULL UNIQUE,
            Number INTEGER NOT NULL DEFAULT 0,
            ColumnColor TEXT NOT NULL DEFAULT '#b8daff',
            TextColor TEXT NOT NULL DEFAULT '#000000'
        );
        """
        with self.db_manager.connection() as db:
            try:
                # Begin transaction for schema creation
                begin_result = db.begin_transaction()
                if not begin_result.success:
                    self.log.error(f"Failed to begin transaction: {begin_result.message}")
                    return begin_result

                # Create the Columns table
                query_result = db.execute_query(create_columns_table)
                if not query_result.success:
                    self.log.error(
                        f"Failed to create Columns table: {query_result.message}"
                    )
                    db.rollback_transaction()
                    return query_result

                # Add default columns
                default_columns = [
                    ("Ready to Start", 1, "#b8daff", "#000000"),
                    ("In Progress", 2, "#b8daff", "#000000"),
                    ("Complete", 3, "#b8daff", "#000000"),
                ]

                insert_query = """
                INSERT INTO Columns (Name, "Order", Number, ColumnColor, TextColor)
                VALUES (?, ?, 0, ?, ?);
                """
                for name, order, column_color, text_color in default_columns:
                    column_result = db.execute_query(
                        insert_query, (name, order, column_color, text_color)
                    )
                    if not column_result.success:
                        self.log.error(
                            f"""Failed to create default col
                            {name}: {column_result.message}"""
                        )
                        db.rollback_transaction()
                        return column_result

                # Commit the changes
                commit_result = db.commit_transaction()
                if not commit_result.success:
                    self.log.error(
                        f"Failed to commit transaction: {commit_result.message}"
                    )
                    db.rollback_transaction()
                    return commit_result

                self.log.info(
                    "Successfully initialized Kanban database schema with default columns"
                )
                return QueryResult(
                    True, None, "Kanban database schema created successfully"
                )

            except Exception as e:
                db.rollback_transaction()
                self.log.error(f"Unexpected error initializing database: {str(e)}")
                return QueryResult(
                    False, None, f"Failed to create database schema: {str(e)}"
                )

    # ------------------------------------------------------------------------------------------

    def add_column(
        self,
        name: str,
        order: int,
        column_color: str = "#b8daff",
        text_color: str = "#000000",
    ) -> QueryResult:
        """Add a new column to the Kanban board

        Args:
            name: Name of the column
            order: Order of the column (left to right)
            column_color: Color of the column header background (defaults to light blue)
            text_color: Color of the column header text (defaults to black)

        Returns:
            QueryResult indicating success/failure
        """
        insert_query = """
        INSERT INTO Columns (Name, "Order", Number, ColumnColor, TextColor)
        VALUES (?, ?, 0, ?, ?);
        """

        with self.db_manager.connection() as db:
            try:
                # Begin transaction
                begin_result = db.begin_transaction()
                if not begin_result.success:
                    self.log.error(f"Failed to begin transaction: {begin_result.message}")
                    return begin_result

                # Insert the new column
                query_result = db.execute_query(
                    insert_query, (name, order, column_color, text_color)
                )
                if not query_result.success:
                    self.log.error(
                        f"Failed to create column {name}: {query_result.message}"
                    )
                    db.rollback_transaction()
                    return query_result

                # Commit the changes
                commit_result = db.commit_transaction()
                if not commit_result.success:
                    self.log.error(
                        f"Failed to commit transaction: {commit_result.message}"
                    )
                    db.rollback_transaction()
                    return commit_result

                self.log.info(f"Successfully created column: {name} at position {order}")
                return QueryResult(True, None, f"Column {name} created successfully")

            except Exception as e:
                db.rollback_transaction()
                self.log.error(f"Unexpected error creating column: {str(e)}")
                return QueryResult(False, None, f"Failed to create column: {str(e)}")

    # ------------------------------------------------------------------------------------------

    def reorder_column(self, column_name: str, new_order: int) -> QueryResult:
        """Reorder a Kanban column

        Args:
            column_name: Name of the column to reorder
            new_order: New position for the column

        Returns:
            QueryResult indicating success/failure
        """
        # Don't allow reordering of fixed columns
        if column_name in ["Ready to Start", "Complete"]:
            return QueryResult(False, None, f"Cannot reorder fixed column: {column_name}")

        # Get current max order
        max_order_query = 'SELECT MAX("Order") as max_order FROM Columns;'

        with self.db_manager.connection() as db:
            try:
                # Begin transaction
                begin_result = db.begin_transaction()
                if not begin_result.success:
                    return begin_result

                # Get max order
                query_result = db.execute_query(max_order_query)
                if not query_result.success:
                    db.rollback_transaction()
                    return query_result

                result = query_result.data
                result.next()
                max_order = result.value("max_order")

                # Validate new order
                if new_order <= 1 or new_order >= max_order:
                    db.rollback_transaction()
                    return QueryResult(
                        False,
                        None,
                        "Cannot move column before 'Ready to Start' or after 'Complete'",
                    )

                # Update the order
                update_query = """
                UPDATE Columns
                SET "Order" = ?
                WHERE Name = ?;
                """

                update_result = db.execute_query(update_query, (new_order, column_name))
                if not update_result.success:
                    db.rollback_transaction()
                    return update_result

                # Commit the changes
                commit_result = db.commit_transaction()
                if not commit_result.success:
                    db.rollback_transaction()
                    return commit_result

                return QueryResult(
                    True, None, f"Column {column_name} reordered successfully"
                )

            except Exception as e:
                db.rollback_transaction()
                return QueryResult(False, None, f"Failed to reorder column: {str(e)}")

    # ------------------------------------------------------------------------------------------

    def load_columns(self) -> QueryResult:
        """Load all columns from the database

        Returns:
            QueryResult with list of (name, number, column_color, text_color) tuples
            ordered by column order
        """
        query = """
        SELECT Name, Number, ColumnColor, TextColor
        FROM Columns
        ORDER BY "Order";
        """

        with self.db_manager.connection() as db:
            try:
                result = db.execute_query(query)
                if not result.success:
                    return result

                columns = []
                query_result = result.data
                while query_result.next():
                    name = query_result.value("Name")
                    number = query_result.value("Number")
                    column_color = query_result.value("ColumnColor")
                    text_color = query_result.value("TextColor")
                    columns.append((name, number, column_color, text_color))

                return QueryResult(True, columns, "Columns loaded successfully")

            except Exception as e:
                return QueryResult(False, None, f"Failed to load columns: {str(e)}")

    # def load_columns(self) -> QueryResult:
    #     """Load all columns from the database
    #
    #     Returns:
    #         QueryResult with list of (name, number) tuples ordered by column order
    #     """
    #     query = """
    #     SELECT Name, Number
    #     FROM Columns
    #     ORDER BY "Order";
    #     """
    #
    #     with self.db_manager.connection() as db:
    #         try:
    #             result = db.execute_query(query)
    #             if not result.success:
    #                 return result
    #
    #             columns = []
    #             query_result = result.data
    #             while query_result.next():
    #                 name = query_result.value("Name")
    #                 number = query_result.value("Number")
    #                 columns.append((name, number))
    #
    #             return QueryResult(True, columns, "Columns loaded successfully")
    #
    #         except Exception as e:
    #             return QueryResult(False, None, f"Failed to load columns: {str(e)}")


# ==========================================================================================
# ==========================================================================================
# eof
