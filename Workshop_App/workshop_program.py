# Workshop information gatherer.

# This program gathers information about our teams workshops by
# gathering the information directly from the website and storing
# it into a searchable database.


import sys
import helper_functions
from PyQt5.QtWidgets import QApplication, QMainWindow
from workshops import WorkshopsTool
from gui_window import GuiWindow
from splash_screen import SplashScreen


def main() -> None:
    """Main"""

    app = QApplication(sys.argv)
    main_window = QMainWindow()
    ui = GuiWindow()
    ui.setup_ui(main_window)

    splash = SplashScreen()
    ws = WorkshopsTool()

    # Connect buttons and menu items.
    ui.buttonGetWorkshops.clicked.connect(lambda: helper_functions.generate_workshop_info(ui, ws))
    ui.actionIncrease_CTRL.triggered.connect(ui.increase_font)
    ui.actionDecrease_CTRL.triggered.connect(ui.decrease_font)
    ui.actionExport_Workshops_Info.triggered.connect(lambda: helper_functions.export_workshops_info(ui, ws))
    ui.actionUpdate_Credentials.triggered.connect(lambda: ui.creds_popup_box(ws))
    ui.actionUpdate_Database.triggered.connect( lambda: helper_functions.update_database(main_window, ws, ui))

    # Peform an initial update attempt of the database when the software is launched
    helper_functions.update_database(main_window, ws, ui)
    splash.close()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
