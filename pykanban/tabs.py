import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QMenu,
    QMessageBox,
    QScrollArea,
    QTabWidget,
    QWidget,
)

from pykanban.dialogs import NewColumnDialog
from pykanban.widgets import KanbanColumn

# ==========================================================================================
# ==========================================================================================

# File:    tabs.py
# Date:    January 25, 2025
# Author:  Jonathan A. Webb
# Purpose: Contains code for the tabs within the application
# ==========================================================================================
# ==========================================================================================
# Insert Code here


class KanbanTabManager(QTabWidget):
    """Manages multiple tabs including Kanban board display

    Creates and manages tabs for task queue, Kanban board, statistics,
    and blocked tasks. Sets up scrollable container for Kanban columns.

    Attributes:
        task_queue_tab: Tab for task queue view
        kanban_tab: Tab containing Kanban board
        statistics_tab: Tab for statistics view
        stuck_tab: Tab for blocked tasks
        column_layout: Layout managing Kanban columns
    """

    def __init__(self, db_manager=None, log: logging.Logger = None, parent=None):
        """Initialize tab manager with empty tabs

        Args:
            db_manager: Database manager instance
            log: Logger instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.db_manager = db_manager
        self.log = log

        self.task_queue_tab = QWidget()
        self.kanban_tab = QWidget()
        self.statistics_tab = QWidget()
        self.stuck_tab = QWidget()
        self._setup_kanban_board()

        self.addTab(self.task_queue_tab, "Task Queue")
        self.addTab(self.kanban_tab, "Kanban")
        self.addTab(self.statistics_tab, "Statistics")
        self.addTab(self.stuck_tab, "Blocked")

    # ------------------------------------------------------------------------------------------

    def update_column(self, name: str, number: int):
        """Update task count for specified column

        Args:
            name: Name of column to update
            number: New task count
        """
        for i in range(self.column_layout.count()):
            column = self.column_layout.itemAt(i).widget()
            if column.name == name:
                column.update_task_count(number)
                break

    # ------------------------------------------------------------------------------------------

    def add_column(
        self,
        name: str,
        number: int = 0,
        column_color: str = "#b8daff",
        text_color: str = "#000000",
    ):
        """Add new column to Kanban board

        Creates a new KanbanColumn widget with specified properties and adds it to
        the board layout. The column is initialized with the provided colors and
        connected to the database manager for persistent color updates.

        Args:
            name: Column header text
            number: Initial task count (defaults to 0)
            column_color: Background color for column header in hex format
            (defaults to light blue) text_color: Text color for column header in
            hex format (defaults to black)

        Note:
            The db_manager property must be set before calling this method for color
            persistence to work. The database manager is passed to each KanbanColumn
            to enable direct updates of color changes to the database.
        """
        column = KanbanColumn(
            name=name,
            number=number,
            column_color=column_color,
            text_color=text_color,
            parent=self,
            db_manager=self.db_manager,
        )
        self.column_layout.addWidget(column)
        if self.log:
            self.log.info(f"Added Kanban column: {name} with color {column_color}")

    # ------------------------------------------------------------------------------------------

    @property
    def db_manager(self):
        """Get the current database manager instance

        Returns:
            The database manager object used for column operations
        """
        return self._db_manager

    # ------------------------------------------------------------------------------------------

    @db_manager.setter
    def db_manager(self, manager):
        """Set the database manager instance

        Args:
            manager: KanbanDatabaseManager instance for column operations
        """
        self._db_manager = manager
        print(f"Database manager updated: {manager is not None}")

    # ------------------------------------------------------------------------------------------

    def clear_columns(self):
        """Remove all columns from the Kanban board"""
        # Clear all widgets from the column layout
        while self.column_layout.count():
            # Get the widget at index 0
            item = self.column_layout.takeAt(0)
            if item is not None and item.widget():
                # Hide and delete the widget
                widget = item.widget()
                widget.hide()
                widget.deleteLater()

        # Force a layout update
        self.column_layout.update()

        if self.log:
            self.log.debug("Cleared all columns from Kanban board")

    # ==========================================================================================

    def _setup_kanban_board(self):
        """Configure layout for Kanban board tab
        Creates horizontal scrollable area to contain Kanban columns
        """
        self.kanban_layout = QHBoxLayout(self.kanban_tab)
        self.kanban_layout.setSpacing(10)
        self.kanban_layout.setContentsMargins(10, 10, 10, 10)

        self.scroll = QScrollArea()
        self.scroll.setObjectName("kanbanScrollArea")
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.column_container = QWidget()
        self.column_container.setObjectName("columnContainer")
        self.column_layout = QHBoxLayout(self.column_container)
        self.column_layout.setSpacing(10)
        self.column_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Enable context menu
        self.column_container.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.column_container.customContextMenuRequested.connect(self._show_context_menu)

        self.scroll.setWidget(self.column_container)
        self.kanban_layout.addWidget(self.scroll)

    # ------------------------------------------------------------------------------------------

    def _show_context_menu(self, position):
        """Show context menu for column container

        Args:
            position: Mouse position where menu should appear
        """
        if not self.db_manager:
            # No database open, don't show menu
            return

        context_menu = QMenu(self)
        create_action = context_menu.addAction("Create New Column")

        # Show the menu and get selected action
        action = context_menu.exec(self.column_container.mapToGlobal(position))

        if action == create_action:
            # Create new column using the existing dialog
            dialog = NewColumnDialog(self.log, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                column_name = dialog.get_column_name()

                try:
                    # Get the order value (before Complete)
                    result = self.db_manager.get_order_for_new_column()
                    if not result.success:
                        raise Exception(f"Failed to get column order: {result.message}")

                    new_order = result.data

                    # Add the column
                    result = self.db_manager.add_column(name=column_name, order=new_order)

                    if result.success:
                        # Clear existing columns
                        self.clear_columns()

                        # Reload columns from database
                        load_result = self.db_manager.load_columns()
                        if load_result.success:
                            for (
                                name,
                                number,
                                column_color,
                                text_color,
                            ) in load_result.data:
                                self.add_column(name, number, column_color, text_color)

                            QMessageBox.information(
                                self,
                                "Success",
                                f"Column '{column_name}' created successfully.",
                            )
                        else:
                            raise Exception(
                                f"Failed to reload columns: {load_result.message}"
                            )
                    else:
                        QMessageBox.critical(
                            self, "Error", f"Failed to create column: {result.message}"
                        )

                except Exception as e:
                    self.log.error(f"Error creating column: {str(e)}")
                    QMessageBox.critical(
                        self, "Error", f"Failed to create column: {str(e)}"
                    )


# ==========================================================================================
# ==========================================================================================
# eof
