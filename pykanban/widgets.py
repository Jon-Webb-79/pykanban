from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QRadioButton,
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
    """A widget representing a single column in a Kanban board"""

    def __init__(
        self,
        name: str,
        number: int = 0,
        column_color: str = "#b8daff",
        text_color: str = "#000000",
        parent: QWidget = None,
    ):
        """Initialize the Kanban column

        Args:
            name: Text to display in column header
            number: Initial number of tasks (defaults to 0)
            column_color: Background color for header (defaults to light blue)
            text_color: Text color for header (defaults to black)
            parent: Parent widget (optional)
        """
        # Call parent constructor first
        super().__init__(parent)

        # Store instance variables
        self.name = name
        self.number = number
        self.column_color = column_color
        self.text_color = text_color

        # Setup the UI
        self._setup_ui()

    # ------------------------------------------------------------------------------------------

    def update_task_count(self, number: int):
        """Update the number of tasks shown in column header"""
        self.number = number
        self.header.setText(f"{self.name} / {self.number}")

    # ================================================================================

    def _setup_ui(self):
        """Configure the column's UI layout and styling"""
        self.setObjectName("kanbanColumn")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.setFixedWidth(300)
        self.header = QLabel(f"{self.name} / {self.number}")
        self.header.setObjectName("columnHeader")
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header.setFixedHeight(40)

        # Apply custom colors to header
        self.header.setStyleSheet(
            f"""
            background-color: {self.column_color};
            color: {self.text_color};
        """
        )

        self.task_container = QWidget()
        self.task_container.setObjectName("columnTaskContainer")
        self.task_layout = QVBoxLayout(self.task_container)
        self.task_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.task_layout.setSpacing(5)

        layout.addWidget(self.header)
        layout.addWidget(self.task_container)

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)


# ==========================================================================================
# ==========================================================================================
# eof
