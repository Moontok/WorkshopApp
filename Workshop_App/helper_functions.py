from PyQt5.QtWidgets import QMainWindow
from json import load
from gui_window import GuiWindow
from workshop_tool import WorkshopsTool


def generate_workshop_info(ui: GuiWindow, ws: WorkshopsTool) -> None:
    """Output the desired content based on selected options."""

    ui.textOutputField.clear()
    ws.set_search_phrase(ui.lineEditPhrase.text())

    update_searched_workshops(ui, ws)

    button_check: bool = check_button_options(ui)

    text_to_display: str = get_workshop_display_text(ui, ws, button_check)

    ui.textOutputField.clear()
    ui.textOutputField.insertPlainText(text_to_display)


def update_searched_workshops(ui: GuiWindow, ws: WorkshopsTool) -> list:
    """Return the correct workshops based on selected options."""

    if ui.lineEditWorkshopID.text() != "":
        try:
            workshops = ws.get_matching_workshops_by_id(ui.lineEditWorkshopID.text())
        except AttributeError:
            workshops = []
    elif ui.checkBoxUseDate.isChecked():
        starting_date: tuple = ui.calendarWidget_StartDate.selectedDate().getDate()
        ending_date: tuple = ui.calendarWidget_EndDate.selectedDate().getDate()        
        workshops  = ws.get_matching_workshops_by_date_range(starting_date, ending_date)
    else:
        workshops  = ws.get_matching_workshops()

    return workshops


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
        ui.textOutputField.insertPlainText(get_welcome_text())
    except ConnectionError:
        ui.textOutputField.insertPlainText(get_welcome_text_for_offline())
    except TypeError:
        ui.textOutputField.insertPlainText(get_server_error_text())
    except FileNotFoundError as e:
        ui.textOutputField.insertPlainText(get_missing_file_text())

    main_window.repaint()


def get_workshop_display_text(ui: GuiWindow, ws: WorkshopsTool, button_check: bool) -> str:
    display_text = list()
    display_text.append(f"Number of matching workshops: {ws.get_number_of_workshops()}\n\n")
    display_text.append(f"Total Signed Up: {ws.get_number_of_participants()}\n\n")

    if button_check:
        display_text = setup_workshop_information_text(ui, display_text, ws)

    display_text.append(f"All emails for these workshops:\n\n{ws.get_emails()}")
    
    return "".join(display_text)


def get_welcome_text() -> str:
    """Get text that first appears in output window."""    

    welcome_text: list = [
        "Your database has been updated!",
        "",
        "This program will allow you to seach current workshops using a phrase, date range, or Session ID.",
        'Type a phrase that you would like to search in the "Phrase:" field.',
        'Leave the "Phrase:" field blank to get all current workshops.',
        "The Session ID search will take priority over phrase and date range search.",
    ] 

    return "\n".join(welcome_text)


def get_welcome_text_for_offline() -> str:
    """Get text that first appears in output window if offline."""

    offline_text: list = [
        "Cannot connect to server...",
        "You are in offline mode.",
        "You can access workshops from the last time your last successful connection.",
        "You can try to update your database when you have established an internet connection.",
    ]

    return "\n".join(offline_text)


def get_server_error_text() -> str:
    """Return server error message."""

    server_error_text: str = "Something went wrong when connecting to server...\nTry again later."

    return server_error_text


def get_missing_file_text() -> str:
    """Return missing file message. """

    missing_file_text: str = 'Missing "connection_info.json". Cannot update database.'

    return missing_file_text


def setup_workshop_information_text(ui: GuiWindow, display_text: str, ws: WorkshopsTool) -> str:
    """Prepare the output of the workshops based on selected information."""

    for workshop in ws.get_most_recent_search_results():
        text = list()
        if ui.checkBoxWsID.isChecked():
            text.append(f"{workshop['workshop_id']}")
        if ui.checkBoxWsStartDate.isChecked():
            text.append(f"{workshop['workshop_start_date_and_time']}")
        if ui.checkBoxWsPartNumbers.isChecked():
            text.append(f"{workshop['workshop_signed_up']}/{workshop['workshop_participant_capacity']}")
        if ui.checkBoxWsName.isChecked():
            text.append(f"{workshop['workshop_name']}")
        if ui.checkBoxWsURL.isChecked():
            text.append(f"\n   Url: {workshop['workshop_url']}")

        display_text.append(" - ".join(text))
        display_text.append("\n")

        if (
            ui.checkBoxNames.isChecked()
            or ui.checkBoxEmails.isChecked()
            or ui.checkBoxSchools.isChecked()
        ):

            display_text.append("   Contact Information:\n")

            for participant_info in workshop["workshop_participant_info_list"]:
                text = list()
                if ui.checkBoxNames.isChecked():
                    text.append(f'{participant_info["name"]}')
                if ui.checkBoxEmails.isChecked():
                    text.append(f'{participant_info["email"]}')
                if ui.checkBoxSchools.isChecked():
                    text.append(f'{participant_info["school"]}')
                display_text.append("    + ")
                display_text.append(" - ".join(text))
                display_text.append("\n")

        display_text.append("\n")

    return display_text

    
if __name__ == '__main__':
    print('This is a module...')
