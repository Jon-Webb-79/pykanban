import logging
import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QGridLayout, QMainWindow, QStatusBar, QWidget

from pykanban.custom_logger import setup_logging
from pykanban.database import KanbanDatabaseManager, QueryResult
from pykanban.menu_bar import MenuBar
from pykanban.tabs import KanbanTabManager
from pykanban.widgets import DayNightRadioButton

# ==========================================================================================
# ==========================================================================================

# File:    main.py
# Date:    January 21, 2025
# Author:  Jonathan A. Webb
# Purpose: This file contains functions and classes that integrate the application into
#          a Model, Controller architecture
# ==========================================================================================
# ==========================================================================================
# Insert Code here


class KanbanViewManager(QMainWindow):
    """
    Class that integrates the application into a main window with tabs. This tab
    will also act as the View class in a Model, View, Controller architecture

    :param day_theme: The title and path length to the .qss file containing the day
                      time theme for the application
    :param night_theme: The title and path length to the .qss file containing the night
                        time theme for the application
    """

    def __init__(self, day_theme: str, night_theme: str, log: logging.Logger):
        super().__init__()
        self.day_theme = day_theme
        self.night_theme = night_theme
        self.logger = log
        self.init_theme = False
        self.theme_status = None

        # Set layout structure for application
        self.grid = QGridLayout()

        # Set window properties
        self.setWindowTitle("Kanban Task Manager")
        # Get the screen size and set window size
        self._configure_window_size()

        # Set Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Add Widgets
        self._create_initial_widgets()
        self._arrange_widgets()

        # Create Menu Bar
        self.menu_bar = MenuBar(self, self.logger)
        self.setMenuBar(self.menu_bar)

        # Create Status Bar on bottom left corner
        self.setStatusBar(QStatusBar())

        self.set_day_theme()

    # ------------------------------------------------------------------------------------------

    def set_day_theme(self) -> None:
        """
        Toggles the application to the day time style sheet
        """
        if os.path.exists(self.day_theme):
            with open(self.day_theme) as file:
                style = file.read()
                if self.init_theme:
                    self.logger.info("Changing Kanban app to day theme")
                QApplication.instance().setStyleSheet(style)
                self.init_theme = True
                self.themestatus = self.day_theme
                self.repaint()
                self.tabs.repaint()
                for i in range(self.tabs.count()):
                    self.tabs.widget(i).repaint()

    # ------------------------------------------------------------------------------------------

    def set_night_theme(self) -> None:
        """
        Toggles the application to the night time style sheet
        """
        if os.path.exists(self.night_theme):
            with open(self.night_theme) as file:
                style = file.read()
                if self.init_theme:
                    self.logger.info("Changing Kanban app to night theme")
                QApplication.instance().setStyleSheet(style)
                self.init_theme = True
                self.theme_status = self.night_theme
                self.repaint()
                self.tabs.repaint()
                for i in range(self.tabs.count()):
                    self.tabs.widget(i).repaint()

    # ==========================================================================================
    # PRIVATE-LIKE METHODS

    def _create_initial_widgets(self) -> None:
        """This method instantiates all widgets for the todo_list application"""
        # Set control actuators that are persistent (not related to tabs)
        self.day_night_radio_button = DayNightRadioButton()

        # Setup Tab widget - Pass both db_manager and logger
        self.tabs = KanbanTabManager(
            db_manager=None, log=self.logger, parent=self.central_widget
        )

        # Ensure the radio button stays compact
        self.day_night_radio_button.setFixedWidth(150)

    # ------------------------------------------------------------------------------------------

    def _arrange_widgets(self) -> None:
        """
        This method arranges all of the widgets for the todo_list application
        """
        # Create a main layout
        self.grid = QGridLayout()
        self.grid.setContentsMargins(10, 10, 10, 10)

        # Add day night radio button to the top right
        self.grid.addWidget(
            self.day_night_radio_button,
            0,
            1,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop,
        )

        # Add the tab widget to take up the main space
        self.grid.addWidget(self.tabs, 1, 0, 1, 2)

        # Make the tab widget expand to fill space
        self.grid.setRowStretch(1, 1)
        self.grid.setColumnStretch(0, 1)

        self.central_widget.setLayout(self.grid)

    # ------------------------------------------------------------------------------------------

    def _configure_window_size(self) -> None:
        """
        Configures the window size based on the screen dimensions.
        Sets window to 75% of screen width and 80% of screen height by default.
        """
        # Get the primary screen
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()

        # Calculate desired window size (75% of screen width, 80% of screen height)
        desired_width = int(screen_geometry.width() * 0.75)
        desired_height = int(screen_geometry.height() * 0.80)

        # Set the window size
        self.resize(desired_width, desired_height)

        # Center the window on screen
        center_point = screen_geometry.center()
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())


# ==========================================================================================
# ==========================================================================================


class KanbanControllerManager(KanbanViewManager):
    """
    Class to control all aspects of the pykanban application

    :param day_theme: The title and path length to the .qss file containing the day
                      time theme for the application
    :param night_theme: The title and path length to the .qss file containing the night
                        time theme for the application
    """

    def __init__(self, day_sheet: str, night_sheet: str, log: logging.Logger):
        self.kanban_db = None  # Initialize as None
        self.log = log
        super().__init__(day_sheet, night_sheet, log)

        self.day_night_radio_button.day_button.clicked.connect(self.set_day_theme)
        self.day_night_radio_button.night_button.clicked.connect(self.set_night_theme)

    # ------------------------------------------------------------------------------------------

    def create_database(self, db_path: str) -> QueryResult:
        """Create and initialize a new Kanban database

        Args:
            db_path: Path where the database should be created

        Returns:
            QueryResult indicating success/failure of database creation
        """
        self.kanban_db = KanbanDatabaseManager(db_path, self.log)
        result = self.kanban_db.initialize_database()
        if result.success:
            self.tabs.db_manager = self.kanban_db
            self.load_kanban_board()
        return result

    # ------------------------------------------------------------------------------------------

    def load_kanban_board(self):
        """Load and display the Kanban board columns"""
        if self.kanban_db:
            result = self.kanban_db.load_columns()
            if result.success:
                for name, number, column_color, text_color in result.data:
                    self.tabs.add_column(name, number, column_color, text_color)


# ==========================================================================================
# ==========================================================================================


def main(day_sheet: str, night_sheet: str, log_path: str) -> None:
    # Initialize logging
    try:
        setup_logging(log_path, "log")
    except Exception as e:
        print(f"Logging setup failed: {e}")

    logger = logging.getLogger(__name__)
    logger.info("Initializing Kanban Session")

    # Verify files exist as part of debug error checking
    if not os.path.exists(day_sheet):
        logger.debug(f"Day Theme sheet {day_sheet} does not exist!")
    if not os.path.exists(night_sheet):
        logger.debug(f"Night Theme sheet {night_sheet} does not exist!")

    # begin Application
    app = QApplication(sys.argv)
    controller = KanbanControllerManager(day_sheet, night_sheet, logger)
    logger.info("Initializing Kanban to day theme")
    #    controller.set_day_theme()
    controller.show()
    app_result = app.exec()
    logger.info("Closed Kanban Session")
    sys.exit(app_result)


# ==========================================================================================
# ==========================================================================================
# eof
