# Workshop information gatherer.

# This program gathers information about our teams workshops by
# gathering the information directly from the website and storing
# it into a searchable database.


import sys
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

    display_text = list()
    display_text.append(f"Number of matching workshops: {ws.get_number_of_workshops()}\n\n")
    display_text.append(f"Total Signed Up: {ws.get_number_of_participants()}\n\n")

    if buttons_checked(ui):
        display_text = setupWorkshopInformation(ui, display_text, workshops)

    display_text.append(f"All emails for these workshops:\n\n{ws.get_emails(workshops)}")
    ui.textOutputField.clear()
    ui.textOutputField.insertPlainText("".join(display_text))


def buttons_checked(ui: GuiWindow) -> bool:
    """Return true if any button is checked."""

    return (
        ui.checkBoxWsID.isChecked()
        or ui.checkBoxWsStartDate.isChecked()
        or ui.checkBoxWsPartNumbers.isChecked()
        or ui.checkBoxWsName.isChecked()
        or ui.checkBoxWsURL.isChecked()
    )


def setupWorkshopInformation(ui: GuiWindow, display_text: str, workshops: list) -> str:
    """
    Prepare the output of the workshops based on selected information.

    Useful information when using:
    Workshop Structure: [id, workshopID, workshopName, workshopStartDateAndTime, workshopSignedUp, workshopParticipantCapacity, workshopURL, [participantInfoList]]
    participantInfoList [name, email, school]
    """

    for workshop in workshops:
        text = list()
        if ui.checkBoxWsID.isChecked():
            text.append(f"{workshop[1]}")
        if ui.checkBoxWsStartDate.isChecked():
            text.append(f"{workshop[3]}")
        if ui.checkBoxWsPartNumbers.isChecked():
            text.append(f"{workshop[4]}/{workshop[5]}")
        if ui.checkBoxWsName.isChecked():
            text.append(f"{workshop[2]}")
        if ui.checkBoxWsURL.isChecked():
            text.append(f"\n   Url: {workshop[6]}")

        display_text.append(" - ".join(text))
        display_text.append("\n")

        if (
            ui.checkBoxNames.isChecked()
            or ui.checkBoxEmails.isChecked()
            or ui.checkBoxSchools.isChecked()
        ):

            display_text.append("   Contact Information:\n")

            for participant_info in workshop[7]:
                text = list()
                if ui.checkBoxNames.isChecked():
                    text.append(f"{participant_info[0]}")
                if ui.checkBoxEmails.isChecked():
                    text.append(f"{participant_info[1]}")
                if ui.checkBoxSchools.isChecked():
                    text.append(f"{participant_info[2]}")
                display_text.append("    + ")
                display_text.append(" - ".join(text))
                display_text.append("\n")

        display_text.append("\n")

    return display_text


def update_database(main_window: QMainWindow, ws: WorkshopsTool, ui: GuiWindow) -> None:
    """Attempts to handle connecting to the website and database."""

    ui.textOutputField.clear()

    try:
        ws.setup_workshop_information()
        ui.textOutputField.insertPlainText(get_welcome_text())
    except ConnectionError:
        ui.textOutputField.insertPlainText(get_welcome_text_for_offline())
    except TypeError:
        ui.textOutputField.insertPlainText(
            "Something went wrong when connecting to server...\nTry again later."
        )
    except FileNotFoundError as e:
        if str(e).split("'")[-2] == "connection_info.json":
            ui.textOutputField.insertPlainText(
                'Missing "connection_info.json". Cannot update database.'
            )

    main_window.repaint()


def get_welcome_text() -> str:
    """Text that first appears in output window."""

    text: list = [
        "Your database has been updated!",
        "",
        "This program will allow you to seach current workshops using a phrase, date range, or Session ID.",
        'Type a phrase that you would like to search in the "Phrase:" field.',
        'Leave the "Phrase:" field blank to get all current workshops.',
        "The Session ID search will take priority over phrase and date range search.",
    ]

    return "\n".join(text)


def get_welcome_text_for_offline() -> str:
    """Text that first appears in output window."""

    text: list = [
        "Cannot connect to server...",
        "You are in offline mode.",
        "You can access workshops from the last time your last successful connection.",
        "You can try to update your database when you have established an internet connection.",
    ]

    return "\n".join(text)


if __name__ == "__main__":
    main()
