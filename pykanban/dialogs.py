import logging
import os

# from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

# ==========================================================================================
# ==========================================================================================

# File:    dialogs.py
# Date:    January 27, 2025
# Author:  Jonathan A. Webb
# Purpose: This code creates dialog windows
# ==========================================================================================
# ==========================================================================================


class NewDatabaseDialog(QDialog):
    """Dialog for creating a new database file with location selection"""

    def __init__(self, log: logging.Logger, parent=None):
        """
        Class provides a dialog box to manage the creation of a new database.

        :param log: A custom logger for logging information
        """
        super().__init__(parent)
        self.log = log
        self.selected_path = ""
        self.database_name = ""
        self._setup_ui()
        self.log.info("Initialized NewDatabaseDialog")

    # ------------------------------------------------------------------------------------------

    def get_database_path(self):
        """Return the full path for the new database

        Returns:
            str | None: Full path to the new database if valid, None otherwise
        """
        if self.database_name and self.selected_path:
            return os.path.join(self.selected_path, f"{self.database_name}.db")
        return None

    # ==========================================================================================

    def _setup_ui(self):
        """Initialize the dialog's user interface"""
        self.setWindowTitle("Create New Database")
        self.setModal(True)

        # Create layouts
        main_layout = QVBoxLayout(self)
        path_layout = QHBoxLayout()
        name_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        # Create widgets for path selection
        path_label = QLabel("Location:")
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_location)

        # Create widgets for database name
        name_label = QLabel("Database Name:")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter database name (with or without .db)")

        # Create accept/cancel buttons
        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self._validate_and_accept)
        self.create_button.setEnabled(False)  # Disabled until valid input

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        # Arrange path selection widgets
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_button)

        # Arrange name input widgets
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)

        # Arrange buttons
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(cancel_button)

        # Add all layouts to main layout
        main_layout.addLayout(path_layout)
        main_layout.addLayout(name_layout)
        main_layout.addLayout(button_layout)

        # Connect signals
        self.name_edit.textChanged.connect(self._check_input_validity)
        self.path_edit.textChanged.connect(self._check_input_validity)

        self.log.debug("Completed UI setup for NewDatabaseDialog")

    # ------------------------------------------------------------------------------------------

    def _browse_location(self):
        """Open file dialog to select database location"""
        self.log.debug("Opening directory selection dialog")
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory", "", QFileDialog.Option.ShowDirsOnly
        )
        if directory:
            self.selected_path = directory
            self.path_edit.setText(directory)
            self.log.info(f"User selected directory: {directory}")

    # ------------------------------------------------------------------------------------------

    def _clean_database_name(self, name: str) -> str:
        """Remove .db suffix if present and clean the database name

        Args:
            name: The input database name

        Returns:
            Cleaned database name without .db suffix
        """
        # First remove any .db suffix
        if name.lower().endswith(".db"):
            name = name[:-3]

        # Remove any leading/trailing whitespace
        return name.strip()

    # ------------------------------------------------------------------------------------------

    def _check_input_validity(self):
        """Enable/disable create button based on input validity"""
        path = self.path_edit.text()
        name = self._clean_database_name(self.name_edit.text())

        # Basic validation - allow letters, numbers, underscores, and hyphens
        valid = bool(path and name and name.replace("_", "").replace("-", "").isalnum())

        self.create_button.setEnabled(valid)

    # ------------------------------------------------------------------------------------------

    def _validate_and_accept(self):
        """Perform final validation and accept dialog if valid"""
        path = self.path_edit.text()
        name = self._clean_database_name(self.name_edit.text())

        if not path or not name:
            self.log.warning("Database creation failed: Missing path or name")
            QMessageBox.warning(
                self, "Invalid Input", "Please provide both a location and database name."
            )
            return

        if not name.replace("_", "").replace("-", "").isalnum():
            self.log.warning(f"Database creation failed: Invalid name format: {name}")
            QMessageBox.warning(
                self,
                "Invalid Name",
                """Database name must contain only letters, numbers,
                underscores, and hyphens.""",
            )
            return

        db_path = os.path.join(path, f"{name}.db")
        if os.path.exists(db_path):
            self.log.warning(f"Database creation failed: Path already exists: {db_path}")
            QMessageBox.warning(
                self,
                "Database Exists",
                f"""A database named '{name}.db' already exists in this
                location.\nPlease choose a different name.""",
            )
            self.name_edit.clear()
            self.name_edit.setFocus()
            return

        self.database_name = name
        self.selected_path = path
        self.log.info(f"Database creation dialog validated successfully for: {db_path}")
        self.accept()


# ==========================================================================================
# ==========================================================================================
# eof
