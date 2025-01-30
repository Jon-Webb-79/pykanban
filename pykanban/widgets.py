from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# ==========================================================================================
# ==========================================================================================

# File:    widgets.py
# Date:    January 21, 2025
# Author:  Jonathan A. Webb
# Purpose: This file contains classes that implement widgets to be used in the todo_six
#          code base.  In most cases the classes act as warappers around widgets
#          implemented in the PyQt6 library.
# ==========================================================================================
# ==========================================================================================
# Insert Code here


class DayNightRadioButton(QWidget):
    """
    Custom QWidget that contains two QRadioButtons for selecting Day or Night themes.

    :param active_widget: Widget is active when created if set to True, inactive
                          if set to false
    """

    def __init__(self, active_widget: bool = True):
        super().__init__()

        self.form = QHBoxLayout(self)
        self.button_group = QButtonGroup(self)

        self.day_button = QRadioButton("Day")
        self.night_button = QRadioButton("Night")

        self.form.addWidget(self.day_button)
        self.form.addWidget(self.night_button)

        self.button_group.addButton(self.day_button)
        self.button_group.addButton(self.night_button)

        # Set the day theme as default
        self.day_button.setChecked(True)
        self.setEnabled(active_widget)


# ==========================================================================================
# ==========================================================================================


class KanbanColumn(QWidget):
    """A widget representing a single column in the Kanban board

    Attributes:
        name (str): Name of the column
        number (int): Number of tasks in the column
    """

    def __init__(self, name: str, number: int = 0, parent=None):
        super().__init__(parent)
        self.name = name
        self.number = number
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the column's user interface"""
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        # Set background and text colors programmatically
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(45, 45, 45))  # Dark background
        palette.setColor(self.foregroundRole(), QColor(220, 220, 220))  # Light text
        self.setPalette(palette)

        # Create header with column name and task count
        self.header = QLabel(f"{self.name} / {self.number}")
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
        """
        )

        # Create scrollable area for tasks
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Create container widget for tasks
        self.task_container = QWidget()
        self.task_layout = QVBoxLayout(self.task_container)
        self.task_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.task_layout.setSpacing(5)

        # Set up scroll area
        self.scroll_area.setWidget(self.task_container)

        # Add widgets to main layout
        layout.addWidget(self.header)
        layout.addWidget(self.scroll_area)

        # Set size policies
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.scroll_area.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # Style the column
        self.setStyleSheet(
            """
            QWidget {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QScrollArea {
                border: none;
            }
        """
        )

    def update_task_count(self, number: int):
        """Update the number of tasks displayed in the header

        Args:
            number: New number of tasks
        """
        self.number = number
        self.header.setText(f"{self.name} / {self.number}")


# ==========================================================================================
# ==========================================================================================
# eof
