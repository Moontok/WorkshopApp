# Workshop information gatherer.

# This program gathers information about our teams workshops by
# gathering the information directly from the website and storing
# it into a searchable database.


import sys
import display_text
from requests.exceptions import ConnectionError
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
    ui.buttonGetWorkshops.clicked.connect(lambda: generate_workshop_info(ui, ws))
    ui.actionIncrease_CTRL.triggered.connect(ui.increase_font)
    ui.actionDecrease_CTRL.triggered.connect(ui.decrease_font)
    ui.actionUpdate_Credentials.triggered.connect(lambda: ui.creds_popup_box(ws))
    ui.actionUpdate_Database.triggered.connect( lambda: update_database(main_window, ws, ui))

    # Peform an initial update attempt of the database when the software is launched
    update_database(main_window, ws, ui)
    splash.close()
    main_window.show()
    sys.exit(app.exec_())


def generate_workshop_info(ui: GuiWindow, ws: WorkshopsTool) -> None:
    """Output the desired content based on selected options."""

    ui.textOutputField.clear()
    ws.set_search_phrase(ui.lineEditPhrase.text())
    workshops = list()

    if ui.lineEditWorkshopID.text() != "":
        workshops = ws.get_matching_workshops_by_id(ui.lineEditWorkshopID.text())
    elif ui.checkBoxUseDate.isChecked():
        starting_date: tuple = ui.calendarWidget_StartDate.selectedDate().getDate()
        ending_date: tuple = ui.calendarWidget_EndDate.selectedDate().getDate()        
        workshops  = ws.get_matching_workshops_by_date_range(starting_date, ending_date)
    else:
        workshops  = ws.get_matching_workshops()

    button_check: bool = check_button_options(ui)

    text_to_display = display_text.get_base_display_text(ui, ws, workshops, button_check)
    ui.textOutputField.clear()
    ui.textOutputField.insertPlainText("".join(text_to_display))


def check_button_options(ui: GuiWindow) -> bool:
    """Return true if any button is checked."""

    return (
        ui.checkBoxWsID.isChecked()
        or ui.checkBoxWsStartDate.isChecked()
        or ui.checkBoxWsPartNumbers.isChecked()
        or ui.checkBoxWsName.isChecked()
        or ui.checkBoxWsURL.isChecked()
    )


def update_database(main_window: QMainWindow, ws: WorkshopsTool, ui: GuiWindow) -> None:
    """Attempts to handle connecting to the website and database."""

    ui.textOutputField.clear()

    try:
        ws.setup_workshop_information()
        ui.textOutputField.insertPlainText(display_text.get_welcome_text())
    except ConnectionError:
        ui.textOutputField.insertPlainText(display_text.get_welcome_text_for_offline())
    except TypeError:
        ui.textOutputField.insertPlainText(display_text.get_server_error_text())
    except FileNotFoundError as e:
        ui.textOutputField.insertPlainText(display_text.get_missing_file_text())

    main_window.repaint()


if __name__ == "__main__":
    main()
