from PyQt6.QtWidgets import QTabWidget, QWidget

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

        # Add the tabs to the QTabWidget
        self.addTab(self.task_queue_tab, "Task Queue")
        self.addTab(self.kanban_tab, "Kanban")
        self.addTab(self.statistics_tab, "Statistics")


# ==========================================================================================
# ==========================================================================================
# eof
