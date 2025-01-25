from PyQt6.QtWidgets import QButtonGroup, QHBoxLayout, QRadioButton, QWidget

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
# eof
