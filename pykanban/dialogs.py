import logging
import os

from PyQt6.QtWidgets import (
    QComboBox,
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


class DeleteDatabaseDialog(QDialog):
    """
    A dialog window for selecting and deleting an existing database file.
    This dialog provides a user interface with file selection, confirmation
    steps, and safety checks before deletion.

    The dialog includes:
    - A file browser to select .db files
    - A warning message about the irreversible nature of deletion
    - Confirmation buttons with cancel option
    - Input validation and safety checks

    Attributes:
        log (logging.Logger): Logger instance for tracking operations
        selected_path (str): Stores the currently selected database path
        path_edit (QLineEdit): Display field for selected database path
        delete_button (QPushButton): Button to confirm deletion (disabled by default)

    Args:
        log (logging.Logger): Logger instance for tracking operations
        parent (QWidget, optional): Parent widget for this dialog. Defaults to None.
    """

    def __init__(self, log: logging.Logger, parent=None):
        """
        Initialize the delete database dialog.

        Args:
            log (logging.Logger): Logger instance for tracking operations
            parent (QWidget, optional): Parent widget for this dialog. Defaults to None.
        """
        super().__init__(parent)
        self.log = log
        self.selected_path = ""
        self._setup_ui()
        self.log.info("Initialized DeleteDatabaseDialog")

    # ------------------------------------------------------------------------------------------

    def get_database_path(self) -> str | None:
        """Return the selected database path

        Returns:
            str | None: Path to the selected database if valid, None otherwise
        """
        return self.selected_path if self.selected_path else None

    # ------------------------------------------------------------------------------------------

    def _setup_ui(self):
        """Initialize the dialog's user interface"""
        self.setWindowTitle("Delete Database")
        self.setModal(True)

        # Create layouts
        main_layout = QVBoxLayout(self)
        path_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        # Create widgets for database selection
        path_label = QLabel("Database:")
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_database)

        # Create delete/cancel buttons
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._confirm_deletion)
        self.delete_button.setEnabled(False)  # Disabled until valid selection

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        # Add warning label
        warning_label = QLabel("⚠️ Warning: Database deletion cannot be undone!")
        warning_label.setStyleSheet("color: red;")

        # Arrange path selection widgets
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_button)

        # Arrange buttons
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(cancel_button)

        # Add all layouts to main layout
        main_layout.addLayout(path_layout)
        main_layout.addWidget(warning_label)
        main_layout.addLayout(button_layout)

    # ------------------------------------------------------------------------------------------

    def _browse_database(self):
        """Open file dialog to select an existing database"""
        self.log.debug("Opening database selection dialog")
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Database",
            "",
            "SQLite Database (*.db)",
        )
        if file_path:
            self.selected_path = file_path
            self.path_edit.setText(file_path)
            self.delete_button.setEnabled(True)
            self.log.info(f"User selected database: {file_path}")

    # ------------------------------------------------------------------------------------------

    def _confirm_deletion(self):
        """Show confirmation dialog before accepting"""
        if not self.selected_path:
            return

        confirm = QMessageBox.warning(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the database:\n{self.selected_path}\n\n"
            "This action cannot be undone!",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )

        if confirm == QMessageBox.StandardButton.Ok:
            self.accept()


# ==========================================================================================
# ==========================================================================================


class OpenDatabaseDialog(QDialog):
    """Dialog for opening an existing database file

    Provides a user interface for selecting and validating a .db file.
    """

    def __init__(self, log: logging.Logger, parent=None):
        """Initialize the open database dialog

        Args:
            log: Logger instance for tracking operations
            parent: Parent widget for this dialog
        """
        super().__init__(parent)
        self.log = log
        self.selected_path = ""
        self._setup_ui()
        self.log.info("Initialized OpenDatabaseDialog")

    # ------------------------------------------------------------------------------------------

    def get_database_path(self) -> str | None:
        """Return the selected database path

        Returns:
            str | None: Path to the selected database if valid, None otherwise
        """
        return self.selected_path if self.selected_path else None

    # ==========================================================================================

    def _setup_ui(self):
        """Initialize the dialog's user interface"""
        self.setWindowTitle("Open Database")
        self.setModal(True)

        # Create layouts
        main_layout = QVBoxLayout(self)
        path_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        # Create widgets for path selection
        path_label = QLabel("Database File:")
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_database)

        # Create accept/cancel buttons
        self.open_button = QPushButton("Open")
        self.open_button.clicked.connect(self._validate_and_accept)
        self.open_button.setEnabled(False)  # Disabled until valid selection

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        # Arrange path selection widgets
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_button)

        # Arrange buttons
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(cancel_button)

        # Add layouts to main layout
        main_layout.addLayout(path_layout)
        main_layout.addLayout(button_layout)

        self.log.debug("Completed UI setup for OpenDatabaseDialog")

    # ==========================================================================================

    def _browse_database(self):
        """Open file dialog to select an existing database"""
        self.log.debug("Opening database selection dialog")
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Database", "", "SQLite Database (*.db)"
        )

        if file_path:
            if file_path.lower().endswith(".db"):
                self.selected_path = file_path
                self.path_edit.setText(file_path)
                self.open_button.setEnabled(True)
                self.log.info(f"User selected database: {file_path}")
            else:
                self.log.warning(f"Invalid file selected: {file_path}")
                QMessageBox.warning(
                    self,
                    "Invalid File Type",
                    "Please select a valid SQLite database file (*.db)",
                )
                self.open_button.setEnabled(False)

    # ==========================================================================================

    def _validate_and_accept(self):
        """Perform final validation before accepting dialog"""
        if not self.selected_path:
            self.log.warning("No database file selected")
            QMessageBox.warning(
                self, "Invalid Selection", "Please select a database file."
            )
            return

        if not os.path.exists(self.selected_path):
            self.log.warning(f"Selected database does not exist: {self.selected_path}")
            QMessageBox.warning(
                self, "File Not Found", "The selected database file no longer exists."
            )
            return

        self.log.info(f"Database selection validated: {self.selected_path}")
        self.accept()


# ==========================================================================================
# ==========================================================================================


class NewColumnDialog(QDialog):
    """Dialog for creating a new Kanban column"""

    def __init__(self, log: logging.Logger, parent=None):
        """Initialize dialog

        Args:
            log: Logger instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.log = log
        self.column_name = ""
        self._setup_ui()
        self.log.info("Initialized NewColumnDialog")

    def get_column_name(self) -> str:
        """Return the entered column name

        Returns:
            str: The column name if valid, empty string otherwise
        """
        return self.column_name

    def _setup_ui(self):
        """Initialize the dialog's user interface"""
        self.setWindowTitle("Create New Column")
        self.setModal(True)

        # Create layouts
        main_layout = QVBoxLayout(self)
        name_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        # Create widgets for name input
        name_label = QLabel("Column Name:")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter column name")

        # Create accept/cancel buttons
        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self._validate_and_accept)
        self.create_button.setEnabled(False)  # Disabled until valid input

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        # Arrange name input widgets
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)

        # Arrange buttons
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(cancel_button)

        # Add all layouts to main layout
        main_layout.addLayout(name_layout)
        main_layout.addLayout(button_layout)

        # Connect signals
        self.name_edit.textChanged.connect(self._check_input_validity)

        self.log.debug("Completed UI setup for NewColumnDialog")

    def _check_input_validity(self):
        """Enable/disable create button based on input validity"""
        name = self.name_edit.text().strip()
        self.create_button.setEnabled(bool(name))

    def _validate_and_accept(self):
        """Validate input and accept dialog if valid"""
        name = self.name_edit.text().strip()

        if not name:
            self.log.warning("Column creation failed: Empty name")
            QMessageBox.warning(self, "Invalid Input", "Please provide a column name.")
            return

        self.column_name = name
        self.log.info(f"Column name validated: {name}")
        self.accept()


# ==========================================================================================
# ==========================================================================================


class DeleteColumnDialog(QDialog):
    """
    Dialog that allows users to select a Kanban column to delete.
    """

    def __init__(self, log, columns, parent=None):
        """
        Initialize the delete column dialog.

        Args:
            log: Logger instance
            columns: List of column names that can be deleted
            parent: Parent widget
        """
        super().__init__(parent)
        self.setObjectName("deleteColumnDialog")
        self.log = log
        self.selected_column = None  # Store selected column

        self.setWindowTitle("Delete Column")
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Instruction Label
        layout.addWidget(QLabel("Select a column to delete:"))

        # Dropdown menu for selecting a column
        self.column_selector = QComboBox()
        self.column_selector.addItems(columns)
        layout.addWidget(self.column_selector)

        # Confirm and Cancel buttons
        button_layout = QVBoxLayout()
        delete_button = QPushButton("Delete")
        delete_button.setObjectName("deleteButton")
        delete_button.clicked.connect(self._confirm_selection)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(delete_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def _confirm_selection(self):
        """
        Save the selected column and close the dialog.
        """
        self.selected_column = self.column_selector.currentText()
        self.log.info(f"User selected column '{self.selected_column}' for deletion.")
        self.accept()

    def get_selected_column(self):
        """
        Return the selected column name.

        Returns:
            str | None: Selected column name or None if canceled.
        """
        return self.selected_column


# ==========================================================================================
# ==========================================================================================
# eof
