from workshops import WorkshopsTool
from gui_window import GuiWindow

   
def get_base_display_text(ui: GuiWindow, ws: WorkshopsTool, workshops: list, button_check: bool):
    display_text = list()
    display_text.append(f"Number of matching workshops: {ws.get_number_of_workshops()}\n\n")
    display_text.append(f"Total Signed Up: {ws.get_number_of_participants()}\n\n")

    if button_check:
        display_text = setup_workshop_information_text(ui, display_text, workshops)

    display_text.append(f"All emails for these workshops:\n\n{ws.get_emails(workshops)}")
    
    return display_text


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


def setup_workshop_information_text(ui: GuiWindow, display_text: str, workshops: list) -> str:
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