from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import QMenu, QMenuBar

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

    :param controller: A ToDoListController object
    """

    def __init__(self, font: QFont):
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
        print("Created New Database")

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

        # Set up New menu bar option
        self.new_action = QAction("New")
        self.new_action.setFont(self.font)
        self.new_action.triggered.connect(self.new_db)
        self.new_action.setStatusTip("Create a new database")

        # Set up Close menu bar option
        self.close_action = QAction("Close")
        self.close_action.setFont(self.font)
        self.close_action.triggered.connect(self.close_db)
        self.close_action.setStatusTip("Close current database")

        # Set up Delete menu bar option
        self.delete_action = QAction("Delete")
        self.delete_action.setFont(self.font)
        self.delete_action.triggered.connect(self.delete_db)
        self.delete_action.setStatusTip("Delete a database")

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


class MenuBar(QMenuBar):
    """
    Custom implementation of the QMenuBar item.  This class integrates all menu
    bar classes into one implementation

    :param controller: A ToDoListController object
    """

    def __init__(self):
        super().__init__()
        font = QFont("Helvetica", 14)
        self.setFont(font)  # Set font for top-level menu
        self.file_menu = FileMenu(font)

        self.addMenu(self.file_menu.menu)


# ==========================================================================================
# ==========================================================================================


# ==========================================================================================
# ==========================================================================================
# eof
