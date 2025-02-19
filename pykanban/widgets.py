from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QButtonGroup,
    QColorDialog,
    QHBoxLayout,
    QLabel,
    QMenu,
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


class KanbanColors:
    """Class to manage Kanban board colors

    This class centralizes color management for the Kanban board, providing
    default colors and methods to modify them.
    """

    DEFAULT_HEADER_BG = "#b8daff"  # Light blue background
    DEFAULT_HEADER_TEXT = "#000000"  # Black text

    # ------------------------------------------------------------------------------------------

    @staticmethod
    def get_default_colors():
        """Get the default colors for a new Kanban column

        Returns:
            tuple: (header_background_color, header_text_color)
        """
        return (KanbanColors.DEFAULT_HEADER_BG, KanbanColors.DEFAULT_HEADER_TEXT)

    # ------------------------------------------------------------------------------------------

    @staticmethod
    def validate_color(color: str) -> bool:
        """Validate that a color string is a valid hex color code

        Args:
            color: Color string to validate

        Returns:
            bool: True if valid hex color, False otherwise
        """
        if not isinstance(color, str):
            return False

        # Check if it's a valid hex color code
        if not color.startswith("#"):
            return False

        # Remove the # and check if remaining chars are valid hex
        color = color.lstrip("#")
        return len(color) in (6, 8) and all(c in "0123456789ABCDEFabcdef" for c in color)


# ==========================================================================================
# ==========================================================================================


class KanbanColumn(QWidget):
    """A widget representing a single column in a Kanban board"""

    def __init__(
        self,
        name: str,
        number: int = 0,
        column_color: str = KanbanColors.DEFAULT_HEADER_BG,
        text_color: str = KanbanColors.DEFAULT_HEADER_TEXT,
        parent: QWidget = None,
        db_manager=None,
    ):
        """Initialize the Kanban column

        Args:
            name: Text to display in column header
            number: Initial number of tasks (defaults to 0)
            column_color: Background color for header
            text_color: Text color for header
            parent: Parent widget (optional)
            db_manager: Database manager instance
        """
        super().__init__(parent)

        self.name = name
        self.number = number
        self._column_color = column_color
        self._text_color = text_color
        self.db_manager = db_manager

        # Enable right-click menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        self._setup_ui()

    # ------------------------------------------------------------------------------------------

    @property
    def column_color(self) -> str:
        """Get the current column header background color"""
        return self._column_color

    # ------------------------------------------------------------------------------------------

    @column_color.setter
    def column_color(self, color: str):
        """Set a new column header background color

        Args:
            color: New color in hex format (#RRGGBB)
        """
        if KanbanColors.validate_color(color):
            self._column_color = color
            self._update_header_style()

    # ------------------------------------------------------------------------------------------

    @property
    def text_color(self) -> str:
        """Get the current column header text color"""
        return self._text_color

    # ------------------------------------------------------------------------------------------

    @text_color.setter
    def text_color(self, color: str):
        """Set a new column header text color

        Args:
            color: New color in hex format (#RRGGBB)
        """
        if KanbanColors.validate_color(color):
            self._text_color = color
            self._update_header_style()

    # ------------------------------------------------------------------------------------------

    def update_task_count(self, number: int):
        """Update the number of tasks shown in column header"""
        self.number = number
        self.header.setText(f"{self.name} / {self.number}")

    # ==========================================================================================

    def _show_context_menu(self, position):
        """Show the context menu for the column when right-clicked

        Args:
            position: Mouse position where menu should appear
        """
        # Create the main context menu
        context_menu = QMenu(self)

        # Create "Column Colors" submenu
        color_menu = QMenu("Column Colors", self)

        # Add color options to the submenu
        header_action = color_menu.addAction("Header Color")
        text_action = color_menu.addAction("Text Color")

        # Add the color submenu to main context menu
        context_menu.addMenu(color_menu)

        # Show the menu at the mouse position and get selected action
        action = context_menu.exec(self.mapToGlobal(position))

        # Handle the selected action
        if action == header_action:
            self._change_header_color()
        elif action == text_action:
            self._change_text_color()

    # ------------------------------------------------------------------------------------------

    def _change_header_color(self):
        """Open color dialog for header background color"""
        color = QColorDialog.getColor(
            QColor(self._column_color), self, "Select Header Color"
        )
        if color.isValid():
            new_color = color.name()
            self.column_color = new_color
            # Update database
            if self.db_manager:
                result = self.db_manager.update_column_color(
                    self.name, "ColumnColor", new_color
                )
                if result.success:
                    self.db_manager.log.info(
                        f"Column '{self.name}' header color changed to {new_color}"
                    )
                else:
                    self.db_manager.log.error(
                        f"""Failed to update header color for column
                    '{self.name}': {result.message}"""
                    )

    # ------------------------------------------------------------------------------------------

    def _change_text_color(self):
        """Open color dialog for header text color"""
        color = QColorDialog.getColor(QColor(self._text_color), self, "Select Text Color")
        if color.isValid():
            new_color = color.name()
            self.text_color = new_color
            # Update database
            if self.db_manager:
                result = self.db_manager.update_column_color(
                    self.name, "TextColor", new_color
                )
                if result.success:
                    self.db_manager.log.info(
                        f"Column '{self.name}' text color changed to {new_color}"
                    )
                else:
                    self.db_manager.log.error(
                        f"""Failed to update text color for column
                        '{self.name}': {result.message}"""
                    )

    # ------------------------------------------------------------------------------------------

    def _update_header_style(self):
        """Update the header's style sheet with current colors"""
        style = f"""
            QLabel {{
                background-color: {self._column_color};
                color: {self._text_color};
                border: 1px solid #dcdcdc;
                border-radius: 15px;
                padding: 4px;
                font-size: 14px;
                font-weight: bold;
            }}
        """
        self.header.setStyleSheet(style)

    # ------------------------------------------------------------------------------------------

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

        # Apply initial header styling
        self._update_header_style()

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
