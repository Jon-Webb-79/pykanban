import logging

from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import QDialog, QMenu, QMenuBar, QMessageBox

from pykanban.dialogs import NewDatabaseDialog

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
        Method that encodes the functionality of the Close attribute
        """
        print("Closed databases")

    # ------------------------------------------------------------------------------------------

    def delete_db(self):
        """
        Method that encodes the functionality of the Delete attribute
        """
        print("Deleted database")

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
