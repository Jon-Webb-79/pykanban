from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QScrollArea, QTabWidget, QWidget

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
    """
    Manages all application tabs in the main window.

    The tabs include:
    - Task Queue
    - Kanban Board
    - Statistics

    This class initializes empty tabs for now.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize the three tabs
        self.task_queue_tab = QWidget()
        self.kanban_tab = QWidget()
        self.statistics_tab = QWidget()
        self.stuck_tab = QWidget()

        self._setup_kanban_board()

        # Add the tabs to the QTabWidget
        self.addTab(self.task_queue_tab, "Task Queue")
        self.addTab(self.kanban_tab, "Kanban")
        self.addTab(self.statistics_tab, "Statistics")
        self.addTab(self.stuck_tab, "Blocked")

    # ------------------------------------------------------------------------------------------

    def _setup_kanban_board(self):
        """Initialize the Kanban board layout"""
        # Create horizontal layout for columns
        self.kanban_layout = QHBoxLayout(self.kanban_tab)
        self.kanban_layout.setSpacing(10)
        self.kanban_layout.setContentsMargins(10, 10, 10, 10)

        # Create scroll area for horizontal scrolling if many columns
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Create container widget for columns
        self.column_container = QWidget()
        self.column_layout = QHBoxLayout(self.column_container)
        self.column_layout.setSpacing(10)
        self.column_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        scroll.setWidget(self.column_container)
        self.kanban_layout.addWidget(scroll)

    # ------------------------------------------------------------------------------------------

    def add_column(self, name: str, number: int = 0):
        """Add a new column to the Kanban board

        Args:
            name: Name of the column
            number: Initial number of tasks in the column
        """
        column = KanbanColumn(name, number)
        self.column_layout.addWidget(column)

    # ------------------------------------------------------------------------------------------

    def update_column(self, name: str, number: int):
        """Update the task count for a specific column

        Args:
            name: Name of the column to update
            number: New number of tasks
        """
        for i in range(self.column_layout.count()):
            column = self.column_layout.itemAt(i).widget()
            if column.name == name:
                column.update_task_count(number)
                break


# ==========================================================================================
# ==========================================================================================
# eof
