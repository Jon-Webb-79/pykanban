import logging
import os

from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import QDialog, QMenu, QMenuBar, QMessageBox

from pykanban.dialogs import DeleteDatabaseDialog, NewDatabaseDialog

# ==========================================================================================
# ==========================================================================================

# File:    menu_bar.py
# Date:    January 25, 2025
# Author:  Jonathan A. Webb
# Purpose: This file contains classes that build the menu bar options for the pykanban
#          application
# ==========================================================================================
# ==========================================================================================
# Insert Code here


class FileMenu:
    """
    Class that builds all functionality necessary to impliment the File attributes
    of the menu bar

    :param font: A font object to set text attributes
    """

    def __init__(self, controller, font: QFont, log: logging.Logger):
        self.controller = controller
        self.log = log
        self.font = font
        self.menu = QMenu("File")
        self.menu.menuAction().setStatusTip("File and I/O Options")

        self.menu.setFont(self.font)
        self._create_actions()
        self._add_actions()

    # ------------------------------------------------------------------------------------------

    def open_db(self):
        """
        Method that encodes the functionality of the Open attribute
        """
        print("Opened Database")

    # ------------------------------------------------------------------------------------------

    def new_db(self):
        """
        Method that encodes the functionality of the New attribute
        """
        dialog = NewDatabaseDialog(self.log, self.menu)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            db_path = dialog.get_database_path()
            self.log.info(f"User confirmed database creation at: {db_path}")

            result = self.controller.create_database(db_path)
            if result.success:
                self.log.info(
                    f"Successfully created and initialized database at: {db_path}"
                )
                QMessageBox.information(
                    self.menu, "Success", "Database created successfully."
                )
            else:
                self.log.error(f"Failed to initialize database: {result.message}")
                QMessageBox.critical(
                    self.menu, "Error", f"Failed to create database: {result.message}"
                )
        else:
            self.log.info("User cancelled database creation")

    # ------------------------------------------------------------------------------------------

    def close_db(self):
        """
        Method that closes the current database and clears all tabs
        """
        if not self.controller.kanban_db:
            self.log.info("No database is currently open")
            return

        # Call the controller's close_database method
        result = self.controller.close_database()

        if result.success:
            # Clear all columns from the Kanban board
            self._clear_kanban_board()
            self.log.info("Database closed and Kanban board cleared successfully")
        else:
            self.log.error(f"Failed to close database: {result.message}")
            # Try to clear the board anyway
            self._clear_kanban_board()

    # def close_db(self):
    #     """
    #     Method that encodes the functionality of the Close attribute
    #     """
    #     print("Closed databases")

    # ------------------------------------------------------------------------------------------

    def delete_db(self):
        """
        Method that handles database deletion with confirmation. Only allows deletion
        of .db files and prevents deletion of currently active database.
        """
        dialog = DeleteDatabaseDialog(self.log, self.menu)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            db_path = dialog.get_database_path()
            if not db_path:
                self.log.warning("No database selected for deletion")
                return

            # Verify file extension
            if not db_path.lower().endswith(".db"):
                error_msg = "Selected file is not a database (.db) file"
                self.log.error(error_msg)
                QMessageBox.critical(self.menu, "Error", error_msg)
                return

            # Check if this is the currently active database
            current_db_path = (
                self.controller.kanban_db.db_path if self.controller.kanban_db else None
            )
            if current_db_path and os.path.abspath(db_path) == os.path.abspath(
                current_db_path
            ):
                error_msg = "Cannot delete the currently active database"
                self.log.error(error_msg)
                QMessageBox.critical(self.menu, "Error", error_msg)
                return

            try:
                os.remove(db_path)
                self.log.info(f"Successfully deleted database: {db_path}")
                QMessageBox.information(
                    self.menu, "Success", "Database deleted successfully."
                )
            except OSError as e:
                error_msg = f"Failed to delete database: {e}"
                self.log.error(error_msg)
                QMessageBox.critical(self.menu, "Error", error_msg)
            except Exception as e:
                error_msg = f"Unexpected error while deleting database: {str(e)}"
                self.log.error(error_msg)
                QMessageBox.critical(self.menu, "Error", error_msg)
        else:
            self.log.info("User cancelled database deletion")

    # ==========================================================================================
    # PRIVATE LIKE METHODS

    def _create_actions(self):
        """
        Creates and connects slots for attributes of the File menu bar item
        """
        # Set up Open menu bar option
        self.open_action = QAction("Open")
        self.open_action.setFont(self.font)
        self.open_action.triggered.connect(self.open_db)
        self.open_action.setStatusTip("Open an existing database")
        self.open_action.setShortcut("Ctrl+Shift+O")

        # Set up New menu bar option
        self.new_action = QAction("New")
        self.new_action.setFont(self.font)
        self.new_action.triggered.connect(self.new_db)
        self.new_action.setStatusTip("Create a new database")
        self.new_action.setShortcut("Ctrl+Shift+N")

        # Set up Close menu bar option
        self.close_action = QAction("Close")
        self.close_action.setFont(self.font)
        self.close_action.triggered.connect(self.close_db)
        self.close_action.setStatusTip("Close current database")
        self.close_action.setShortcut("Ctrl+Shift+C")

        # Set up Delete menu bar option
        self.delete_action = QAction("Delete")
        self.delete_action.setFont(self.font)
        self.delete_action.triggered.connect(self.delete_db)
        self.delete_action.setStatusTip("Delete a database")
        self.delete_action.setShortcut("Ctrl+Shift+D")

    # ------------------------------------------------------------------------------------------

    def _add_actions(self):
        """
        Adds slots for the File menu bar item
        """
        self.menu.addAction(self.open_action)
        self.menu.addAction(self.new_action)
        self.menu.addAction(self.close_action)
        self.menu.addSeparator()  # Add visual separatio
        self.menu.addAction(self.delete_action)

    # ------------------------------------------------------------------------------------------

    def _clear_kanban_board(self):
        """
        Helper method to clear all columns from the Kanban board
        """
        try:
            # Get the column layout from the tabs
            column_layout = self.controller.tabs.column_layout

            # Remove all widgets from the layout
            while column_layout.count():
                # Get the widget at index 0
                item = column_layout.takeAt(0)
                if item is not None and item.widget():
                    # Hide and delete the widget
                    widget = item.widget()
                    widget.hide()
                    widget.deleteLater()

            # Force a layout update
            self.controller.tabs.column_layout.update()

            self.log.info("Successfully cleared Kanban board")

        except Exception as e:
            self.log.error(f"Error clearing Kanban board: {str(e)}")


# ==========================================================================================
# ==========================================================================================


class ColumnMenu:
    """
    Class that builds all functionality necessary to impliment the Column attributes
    of the menu bar

    :param font: A font object to set text attributes
    """

    def __init__(self, font: QFont):
        self.font = font
        self.menu = QMenu("Columns")
        self.menu.menuAction().setStatusTip("Kanban Column Options")

        self.menu.setFont(self.font)
        self._create_actions()
        self._add_actions()

    # ------------------------------------------------------------------------------------------

    def create_col(self):
        """
        Method that encodes the functionality of the Create Column attribute
        """
        print("Created a new Kanban Column")

    # ------------------------------------------------------------------------------------------

    def delete_col(self):
        """
        Method that encodes the functionality of the Delete Column attribute
        """
        print("Deleted a Kanban Column")

    # ------------------------------------------------------------------------------------------

    def unlock_col(self):
        """
        Method that encodes the functionality of the Unlock attribute
        """
        print("Unlocked Kanban Columns")

    # ------------------------------------------------------------------------------------------

    def lock_col(self):
        """
        Method that encodes the functionality of the Unlock attribute
        """
        print("Locked Kanban Columns")

    # ==========================================================================================
    # PRIVATE LIKE METHODS

    def _create_actions(self):
        """
        Creates and connects slots for attributes of the File menu bar item
        """
        # Set up Open menu bar option
        self.create_action = QAction("Create Column")
        self.create_action.setFont(self.font)
        self.create_action.triggered.connect(self.create_col)
        self.create_action.setStatusTip("Create a new Kanban column")
        self.create_action.setShortcut("Ctrl+Shift+X")

        # Set up Delete menu bar option
        self.delete_action = QAction("Delete Column")
        self.delete_action.setFont(self.font)
        self.delete_action.triggered.connect(self.delete_col)
        self.delete_action.setStatusTip("Delete a Kanban column")
        self.delete_action.setShortcut("Ctrl+Shift+S")

        # Set up Delete menu bar option
        self.unlock_action = QAction("Unlock")
        self.unlock_action.setFont(self.font)
        self.unlock_action.triggered.connect(self.unlock_col)
        self.unlock_action.setStatusTip("Unlock Kanban columns")
        self.unlock_action.setShortcut("Ctrl+Shift+U")

        # Set up Delete menu bar option
        self.lock_action = QAction("Lock")
        self.lock_action.setFont(self.font)
        self.lock_action.triggered.connect(self.lock_col)
        self.lock_action.setStatusTip("Lock Kanban columns")
        self.lock_action.setShortcut("Ctrl+Shift+L")

    # ------------------------------------------------------------------------------------------

    def _add_actions(self):
        """
        Adds slots for the File menu bar item
        """
        self.menu.addAction(self.create_action)
        self.menu.addAction(self.delete_action)
        self.menu.addSeparator()  # Add visual separatio
        self.menu.addAction(self.unlock_action)
        self.menu.addAction(self.lock_action)


# ==========================================================================================
# ==========================================================================================


class ProjectMenu:
    """
    Class that builds all functionality necessary to impliment the Project attributes
    of the menu bar

    :param font: A font object to set text attributes
    """

    def __init__(self, font: QFont):
        self.font = font
        self.menu = QMenu("Project")
        self.menu.menuAction().setStatusTip("Options to create and modify projects")

        self.menu.setFont(self.font)
        self._create_actions()
        self._add_actions()

    # ------------------------------------------------------------------------------------------

    def create_project(self):
        """
        Method that encodes the functionality of the Create Project attribute
        """
        print("Created a new Kanban Project")

    # ------------------------------------------------------------------------------------------

    def delete_project(self):
        """
        Method that encodes the functionality of the Delete Project attribute
        """
        print("Deleted a Kanban Project")

    # ------------------------------------------------------------------------------------------

    def modify_project(self):
        """
        Method that encodes the functionality of the modify project attribute
        """
        print("Modify a Kanban Project")

    # ==========================================================================================
    # PRIVATE LIKE METHODS

    def _create_actions(self):
        """
        Creates and connects slots for attributes of the File menu bar item
        """
        # Set up Open menu bar option
        self.create_action = QAction("Create Project")
        self.create_action.setFont(self.font)
        self.create_action.triggered.connect(self.create_project)
        self.create_action.setStatusTip("Create a new Kanban project")
        self.create_action.setShortcut("Ctrl+Shift+P")

        # Set up Delete menu bar option
        self.delete_action = QAction("Delete Project")
        self.delete_action.setFont(self.font)
        self.delete_action.triggered.connect(self.delete_project)
        self.delete_action.setStatusTip("Delete a Kanban project")
        self.delete_action.setShortcut("Ctrl+Shift+Q")

        # Set up Delete menu bar option
        self.modify_action = QAction("Unlock")
        self.modify_action.setFont(self.font)
        self.modify_action.triggered.connect(self.modify_project)
        self.modify_action.setStatusTip("Modify a Kanban project")
        self.modify_action.setShortcut("Ctrl+Shift+M")

    # ------------------------------------------------------------------------------------------

    def _add_actions(self):
        """
        Adds slots for the File menu bar item
        """
        self.menu.addAction(self.create_action)
        self.menu.addAction(self.modify_action)
        self.menu.addSeparator()  # Add visual separatio
        self.menu.addAction(self.delete_action)


# ==========================================================================================
# ==========================================================================================


class MenuBar(QMenuBar):
    """
    Custom implementation of the QMenuBar item.  This class integrates all menu
    bar classes into one implementation

    :param controller: A ToDoListController object
    """

    def __init__(self, controller, log: logging.Logger):
        super().__init__()
        font = QFont("Helvetica", 14)
        self.setFont(font)  # Set font for top-level menu
        self.file_menu = FileMenu(controller, font, log)
        self.col_menu = ColumnMenu(font)
        self.proj_menu = ProjectMenu(font)

        self.addMenu(self.file_menu.menu)
        self.addMenu(self.col_menu.menu)
        self.addMenu(self.proj_menu.menu)


# ==========================================================================================
# ==========================================================================================
# eof
