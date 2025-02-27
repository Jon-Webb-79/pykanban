import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QMenu,
    QMessageBox,
    QScrollArea,
    QTabWidget,
    QWidget,
)

from pykanban.dialogs import NewColumnDialog
from pykanban.widgets import KanbanColumn

# ==========================================================================================
# ==========================================================================================

# File:    tabs.py
# Date:    January 25, 2025
# Author:  Jonathan A. Webb
# Purpose: Contains code for the tabs within the application
# ==========================================================================================
# ==========================================================================================
# Insert Code here


class KanbanTabManager(QTabWidget):

    class KanbanColumnContainer(QWidget):
        """Container widget for Kanban columns that supports drag and drop"""

        def __init__(self, parent=None, log=None, db_manager=None):
            """Initialize the column container

            Args:
                parent: Parent widget
                log: Logger instance
                db_manager: Database manager for fetching column order
            """
            super().__init__(parent)
            self.log = log
            self.db_manager = db_manager
            self.setObjectName("columnContainer")

            # Dictionary to track column order: {column_name: order}
            self.column_order = {}

            # Track the column currently being dragged
            self.dragged_column = None

            # Track column positions (left edge x-coordinate)
            self.column_positions = []

            # Enable dropping
            self.setAcceptDrops(True)

            # Create layout for columns
            self.column_layout = QHBoxLayout(self)
            self.column_layout.setSpacing(10)
            self.column_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            # Setup context menu
            self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        def refresh_column_order(self):
            """Refresh the column order dictionary from the database"""
            if not self.db_manager:
                print("Cannot refresh column order: no database manager")
                return

            # Load active columns
            result = self.db_manager.load_columns()
            if result.success:
                # Clear existing order dictionary
                self.column_order.clear()

                # Get column data which includes (name, number, column_color, text_color)
                columns = result.data

                # Fetch the actual order values from the database
                for column_data in columns:
                    name = column_data[0]  # Name is the first element

                    # Query the database for this column's order
                    order_query = """
                    SELECT "Order"
                    FROM Columns
                    WHERE Name = ? AND deletion_date IS NULL;
                    """

                    with self.db_manager.db_manager.connection() as db:
                        order_result = db.execute_query(order_query, (name,))
                        if order_result.success and order_result.data.next():
                            order = order_result.data.value("Order")
                            self.column_order[name] = order
                        else:
                            print(f"Could not find order for column: {name}")

                print(f"Refreshed column order: {self.column_order}")
            else:
                print(f"Failed to load columns: {result.message}")

        def update_column_positions(self):
            """Update the positions of columns for drag reference"""
            self.column_positions = []

            # For each column widget, store its position
            for i in range(self.column_layout.count()):
                widget = self.column_layout.itemAt(i).widget()
                if widget and hasattr(widget, "name"):
                    # Store the left edge x-coordinate, width, and widget reference
                    pos = widget.pos().x()
                    self.column_positions.append((pos, widget.width(), widget))
                    print(
                        f"""Added column position:
                        {widget.name} at x={pos}, width={widget.width()}"""
                    )

            print(f"Updated column positions: {len(self.column_positions)} columns")

        def dragEnterEvent(self, event):
            """Handle drag enter events

            Accept the drag if it's coming from a Kanban column

            Args:
                event: Drag enter event
            """
            # Accept the drag if we're dragging a Kanban column
            if event.mimeData().hasText():
                # Get the column name from the mime data
                column_name = event.mimeData().text()

                # Only accept if it's not a fixed column
                if column_name not in ["Ready to Start", "Complete"]:
                    event.accept()

                    # Store the dragged column
                    self.dragged_column = column_name

                    # Save a copy of the original order
                    self.original_column_order = self.column_order.copy()

                    # Update column positions for reference
                    self.update_column_positions()

                    print(f"Started dragging column: {column_name}")
                    print(f"Current order: {self.column_order}")
                else:
                    event.ignore()
                    print(f"Rejected drag for fixed column: {column_name}")
            else:
                event.ignore()

        def dragMoveEvent(self, event):
            """Handle drag move events

            Show visual feedback about where the column would be placed

            Args:
                event: Drag move event
            """
            # Accept the drag if we're dragging a Kanban column
            if event.mimeData().hasText():
                # Get the column name
                column_name = event.mimeData().text()

                # Only handle non-fixed columns
                if column_name not in ["Ready to Start", "Complete"]:
                    event.accept()

                    # Calculate new position and update order dictionary
                    self.calculate_new_order(event.position().x(), column_name)
                else:
                    event.ignore()
            else:
                event.ignore()

        def calculate_new_order(self, x_pos, column_name):  # noqa: C901
            """Calculate the new order for the dragged column

            Args:
                x_pos: Current x position of the drag
                column_name: Name of the column being dragged
            """
            # Find the position in the layout where the column would be dropped
            target_index = 0

            # Skip if we have no column positions
            if not self.column_positions:
                print("No column positions available")
                return

            # Determine where the column would be inserted based on x position
            for i, (pos, width, widget) in enumerate(self.column_positions):
                # If widget is the dragged column, skip it
                if hasattr(widget, "name") and widget.name == column_name:
                    continue

                # If past the middle of this column
                if x_pos > pos + (width / 2):
                    target_index = i + 1
                else:
                    break

            # Find the order of "Ready to Start" and "Complete" columns
            ready_order = None
            complete_order = None
            for name, order in self.column_order.items():
                if name == "Ready to Start":
                    ready_order = order
                elif name == "Complete":
                    complete_order = order

            if ready_order is not None and target_index <= ready_order:
                target_index = ready_order + 1  # Place after "Ready to Start"
            elif complete_order is not None and target_index >= complete_order:
                target_index = complete_order - 1  # Place before "Complete"

            # Get current order of the dragged column
            current_order = self.column_order.get(column_name, 0)
            if current_order == 0:
                print(f"Column {column_name} not found in order dictionary")
                return

            # Calculate new order value
            new_order = target_index

            # Only update if order actually changes
            if new_order != current_order:
                print(f"Moving {column_name} from order {current_order} to {new_order}")

                # Update the order dictionary with the new values
                # Create a working copy so we don't modify while iterating
                new_order_dict = self.column_order.copy()

                # Adjust all columns between old and new position
                if new_order > current_order:
                    # Moving right: Shift columns between old and new position left
                    for col, order in new_order_dict.items():
                        if col != column_name and current_order < order <= new_order:
                            new_order_dict[col] = order - 1
                else:
                    # Moving left: Shift columns between new and old position right
                    for col, order in new_order_dict.items():
                        if col != column_name and new_order <= order < current_order:
                            new_order_dict[col] = order + 1

                # Set new order for dragged column
                new_order_dict[column_name] = new_order

                # Update the column_order dictionary
                self.column_order = new_order_dict

                # Print the changes for debugging
                print(f"Updated order: {self.column_order}")

        def dropEvent(self, event):
            """Handle drop events

            For now, we just ignore the drop and reset columns to their original positions

            Args:
                event: Drop event
            """
            # Print the final calculated order for reference
            print(f"Final calculated order (not persisted): {self.column_order}")

            # Reset to original order
            if hasattr(self, "original_column_order"):
                self.column_order = self.original_column_order.copy()
                print(f"Reset to original order: {self.column_order}")

            # Reset dragged column reference
            self.dragged_column = None

            # Ignore the drop to let the column snap back to original position
            event.ignore()

            print("Drop ignored - column will reset to original position")

    """Manages multiple tabs including Kanban board display

    Creates and manages tabs for task queue, Kanban board, statistics,
    and blocked tasks. Sets up scrollable container for Kanban columns.

    Attributes:
        task_queue_tab: Tab for task queue view
        kanban_tab: Tab containing Kanban board
        statistics_tab: Tab for statistics view
        stuck_tab: Tab for blocked tasks
        column_layout: Layout managing Kanban columns
    """

    def __init__(self, db_manager=None, log: logging.Logger = None, parent=None):
        """Initialize tab manager with empty tabs

        Args:
            db_manager: Database manager instance
            log: Logger instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.db_manager = db_manager
        self.log = log

        self.task_queue_tab = QWidget()
        self.kanban_tab = QWidget()
        self.statistics_tab = QWidget()
        self.stuck_tab = QWidget()
        self._setup_kanban_board()

        self.addTab(self.task_queue_tab, "Task Queue")
        self.addTab(self.kanban_tab, "Kanban")
        self.addTab(self.statistics_tab, "Statistics")
        self.addTab(self.stuck_tab, "Blocked")

    # ------------------------------------------------------------------------------------------

    def update_column(self, name: str, number: int):
        """Update task count for specified column

        Args:
            name: Name of column to update
            number: New task count
        """
        for i in range(self.column_layout.count()):
            column = self.column_layout.itemAt(i).widget()
            if column.name == name:
                column.update_task_count(number)
                break

    # ------------------------------------------------------------------------------------------

    def add_column(
        self,
        name: str,
        number: int = 0,
        column_color: str = "#b8daff",
        text_color: str = "#000000",
    ):
        """Add new column to Kanban board

        Creates a new KanbanColumn widget with specified properties and adds it to
        the board layout. The column is initialized with the provided colors and
        connected to the database manager for persistent color updates.

        Args:
            name: Column header text
            number: Initial task count (defaults to 0)
            column_color: Background color for column header in hex format
            (defaults to light blue) text_color: Text color for column header in
            hex format (defaults to black)

        Note:
            The db_manager property must be set before calling this method for color
            persistence to work. The database manager is passed to each KanbanColumn
            to enable direct updates of color changes to the database.
        """
        column = KanbanColumn(
            name=name,
            number=number,
            column_color=column_color,
            text_color=text_color,
            parent=self.column_container,
            db_manager=self.db_manager,
        )
        self.column_layout.addWidget(column)
        if self.log:
            self.log.info(f"Added Kanban column: {name} with color {column_color}")

        # Refresh column order after adding a column
        self.column_container.refresh_column_order()

    # ------------------------------------------------------------------------------------------

    @property
    def db_manager(self):
        """Get the current database manager instance

        Returns:
            The database manager object used for column operations
        """
        return self._db_manager

    # ------------------------------------------------------------------------------------------

    @db_manager.setter
    def db_manager(self, manager):
        """Set the database manager instance

        Args:
            manager: KanbanDatabaseManager instance for column operations
        """
        self._db_manager = manager
        print(f"Database manager updated: {manager is not None}")

        # Update column container with new db_manager if it exists
        if hasattr(self, "column_container"):
            self.column_container.db_manager = manager
            # Refresh column order with new database
            if manager is not None:
                self.column_container.refresh_column_order()

    # ------------------------------------------------------------------------------------------

    def clear_columns(self):
        """Remove all columns from the Kanban board"""
        # Clear all widgets from the column layout
        while self.column_layout.count():
            # Get the widget at index 0
            item = self.column_layout.takeAt(0)
            if item is not None and item.widget():
                # Hide and delete the widget
                widget = item.widget()
                widget.hide()
                widget.deleteLater()

        # Force a layout update
        self.column_layout.update()

        if self.log:
            self.log.debug("Cleared all columns from Kanban board")

    # ==========================================================================================

    def _setup_kanban_board(self):
        """Configure layout for Kanban board tab
        Creates horizontal scrollable area to contain Kanban columns
        """
        self.kanban_layout = QHBoxLayout(self.kanban_tab)
        self.kanban_layout.setSpacing(10)
        self.kanban_layout.setContentsMargins(10, 10, 10, 10)

        self.scroll = QScrollArea()
        self.scroll.setObjectName("kanbanScrollArea")
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Use enhanced KanbanColumnContainer with db_manager parameter
        self.column_container = self.KanbanColumnContainer(
            log=self.log, db_manager=self.db_manager
        )
        self.column_container.customContextMenuRequested.connect(self._show_context_menu)

        # Get reference to the column layout from our container
        self.column_layout = self.column_container.column_layout

        self.scroll.setWidget(self.column_container)
        self.kanban_layout.addWidget(self.scroll)

    # ------------------------------------------------------------------------------------------

    def _show_context_menu(self, position):
        """Show context menu for column container

        Args:
            position: Mouse position where menu should appear
        """
        if not self.db_manager:
            # No database open, don't show menu
            return

        context_menu = QMenu(self)
        create_action = context_menu.addAction("Create New Column")

        # Show the menu and get selected action
        action = context_menu.exec(self.column_container.mapToGlobal(position))

        if action == create_action:
            # Create new column using the existing dialog
            dialog = NewColumnDialog(self.log, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                column_name = dialog.get_column_name()

                try:
                    # Get the order value (before Complete)
                    result = self.db_manager.get_order_for_new_column()
                    if not result.success:
                        raise Exception(f"Failed to get column order: {result.message}")

                    new_order = result.data

                    # Add the column
                    result = self.db_manager.add_column(name=column_name, order=new_order)

                    if result.success:
                        # Clear existing columns
                        self.clear_columns()

                        # Reload columns from database
                        load_result = self.db_manager.load_columns()
                        if load_result.success:
                            for (
                                name,
                                number,
                                column_color,
                                text_color,
                            ) in load_result.data:
                                self.add_column(name, number, column_color, text_color)

                            QMessageBox.information(
                                self,
                                "Success",
                                f"Column '{column_name}' created successfully.",
                            )
                        else:
                            raise Exception(
                                f"Failed to reload columns: {load_result.message}"
                            )
                    else:
                        QMessageBox.critical(
                            self, "Error", f"Failed to create column: {result.message}"
                        )

                except Exception as e:
                    self.log.error(f"Error creating column: {str(e)}")
                    QMessageBox.critical(
                        self, "Error", f"Failed to create column: {str(e)}"
                    )


# ==========================================================================================
# ==========================================================================================
# eof
