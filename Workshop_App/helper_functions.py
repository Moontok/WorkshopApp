import os
from openpyxl import Workbook
from openpyxl.styles import Font
from gui_window import GuiWindow
from PyQt5.QtWidgets import QFileDialog, QMainWindow
from workshops import WorkshopsTool


def generate_workshop_info(ui: GuiWindow, ws: WorkshopsTool) -> None:
    """Output the desired content based on selected options."""

    ui.textOutputField.clear()
    ws.set_search_phrase(ui.lineEditPhrase.text())
    workshops = list()

    workshops = get_workshops(ui, ws)

    button_check: bool = check_button_options(ui)

    text_to_display: str = get_workshop_display_text(ui, ws, workshops, button_check)

    ui.textOutputField.clear()
    ui.textOutputField.insertPlainText(text_to_display)


def get_workshops(ui: GuiWindow, ws: WorkshopsTool) -> list:
    """Return the correct workshops based on selected options."""

    if ui.lineEditWorkshopID.text() != "":
        workshops = ws.get_matching_workshops_by_id(ui.lineEditWorkshopID.text())
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


def get_workshop_display_text(ui: GuiWindow, ws: WorkshopsTool, workshops: list, button_check: bool) -> str:
    display_text = list()
    display_text.append(f"Number of matching workshops: {ws.get_number_of_workshops()}\n\n")
    display_text.append(f"Total Signed Up: {ws.get_number_of_participants()}\n\n")

    if button_check:
        display_text = setup_workshop_information_text(ui, display_text, workshops)

    display_text.append(f"All emails for these workshops:\n\n{ws.get_emails(workshops)}")
    
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

def export_workshops_info(ui: GuiWindow, ws: WorkshopsTool) -> str:
    """Returns a selected directory."""

    file_name: str = "workshop_info.xlsx"
    base_directory: str = str(QFileDialog.getExistingDirectory(None, "Select Directory"))

    file_path: str = os.path.join(base_directory, file_name)

    ws.set_search_phrase(ui.lineEditPhrase.text())

    workshops: list = get_workshops(ui, ws)

    workbook = Workbook()
    workbook["Sheet"].title = "Workshops"

    workshops_sheet = workbook.active
    attendance_sheet = workbook.create_sheet("Attendance")
    attendance_sheet.append(["TRAINING NAME"])
    attendance_sheet.append(["TRAINING DATES"])
    attendance_sheet.append([])
    attendance_sheet.append(["COOP", "Name", "Email", "District", "Hours", "Dates", "Attended"])
    
    for workshop in workshops:
        coop_part: str = ""
        for letter in workshop[2]:
            if letter.isalpha():
                coop_part += letter
            else:
                if len(coop_part) == 0:
                    coop_part = "DeQueen_Mena"
                break

        row = workshop[1:6]
        row.append(coop_list(coop_part))
        row.append(workshop[6])

        workshops_sheet.append(row)
        
        sheet = workbook.create_sheet(coop_part)        
        sheet.append(row)

        if len(workshop[7]) > 0:
            for partipant in workshop[7]:
                attendance_row: list = list(partipant)
                attendance_row.insert(0, coop_part)
                attendance_sheet.append(attendance_row)
                sheet.append(list(partipant))

    
    format_sheet(attendance_sheet)

    workbook.save(filename=file_path)


def format_sheet(worksheet) -> None:

    worksheet["A1"].font = Font(size=14, bold=True, italic=True, color="FF0000")    
    worksheet["B1"].font = Font(size=14, bold=True, color="FF0000")

    for column in "ABCDEFG":
        worksheet[f"{column}4"].font = Font(size=14, bold=True)

def coop_list(coop: str) -> str:
    coops: dict = {
        "AFESC":"Session Link for Arch Ford ESC Area Educators",
        "ARESC":"Session Link for Arkansas River ESC Area Educators",
        "CRESC":"Session Link for Crowley’s Ridge ESC Area Educators",
        "DSC":"Session Link for Dawson ESC Area Educators",
        "DeQueen_Mena":"Session Link for DeQueen/Mena ESC Area Educators",
        "GREC":"Session Link for Great Rivers ESC Area Educators",
        "GFESC":"Session Link for Guy Fenter ESC Area Educators",
        "NAESC":"Session Link for Northcentral ESC Area Educators",
        "NEA":"Session Link for Northeast ESC Area Educators",
        "NWAESC":"Session Link for Northwest ESC Area Educators",
        "OUR":"Session Link for O.U.R. ESC Area Educators",
        "SCSC":"Session Link for Southcentral ESC Area Educators",
        "SE":"Session Link for Southeast ESC Area Educators",
        "SWAEC":"Session Link for Southwest ESC Area Educators",
        "WDMESC":"Session Link for Wilbur ESC Area Educators"
    }

    coop_match = coops.get(coop, "???Location???")

    return coop_match

    
if __name__ == '__main__':
    print('This is a module...')