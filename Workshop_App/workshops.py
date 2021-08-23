# This is a module created to support workshopProgramMain.py.
# This has the Workshops class that is used to pull and format the information
# for each workshop from the workshop url.


from requests_html import HTMLSession, HTMLResponse
from os import chdir
from pathlib import Path
from re import search
from json import load, dump
from datetime import date
from database import WorkshopDatabase


class Workshops:
    """A class that contains all the workshop data and methods to get and work on that data."""

    def __init__(self):
        self.search_phrase: str = ""
        self.number_of_workshops: int = 0
        self.number_of_participants: int = 0
        self.user_name: str = ""
        self.user_password: str = ""
        self.set_working_directory("Workshop_App")

    def connect_and_update_database(self) -> None:
        """Connects to the escWorks webpage, logins, gather workshops, and add them to the database."""

        connection_info: dict = self.get_connection_info()

        login_data: dict = {
            "ctl00$mainBody$txtUserName": connection_info["user_name"],
            "ctl00$mainBody$txtPassword": connection_info["password"],
            "ctl00$mainBody$btnSubmit": "Submit",
        }

        with HTMLSession() as session:
            url: str = connection_info["signin"]

            login_page_content = session.get(url)

            eventMatch = login_page_content.html.find(
                "input#__EVENTVALIDATION", first=True
            )
            login_data["__EVENTVALIDATION"] = eventMatch.attrs["value"]
            view_state_match: list = login_page_content.html.find("input#__VIEWSTATE", first=True)
            login_data["__VIEWSTATE"] = view_state_match.attrs["value"]

            session.post(url, data=login_data)
            instructor_page_content: HTMLResponse = session.get(connection_info["target_info_url"])

            # Collect all workshops that are listed on the webpage.
            workshops_content: list = instructor_page_content.html.find("table.mainBody tr")

            # Convert the workshopContent into a list of lists skipping the first row of the table.
            # The content of each element is as follows:
            # ['Workshop Name', 'Workshop Date and Time', 'Workshop Enrollment']
            workshops_content = [x.text.split("\n") for x in list(workshops_content)[1:]]

            ws_db: WorkshopDatabase = WorkshopDatabase()
            ws_db.create_workshops_tables()

            for workshop_info in workshops_content:
                workshops: dict = {}

                workshops["workshop_id"] = workshop_info[0][:6]
                workshops["workshop_name"] = workshop_info[0][9:]
                workshops["workshop_start_date_and_time"] = workshop_info[1]
                workshops["workshop_signed_up"] = workshop_info[2].split(" / ")[0]
                workshops["workshop_participant_capacity"] = workshop_info[2].split(" / ")[1]
                workshops["workshop_url"] = f'{connection_info["url_base"]}{workshops["workshop_id"]}'
                workshops["workshop_participant_info_list"] = self.get_participant_info(session, workshops["workshop_id"], connection_info)

                ws_db.add_workshop(workshops)

        ws_db.close_connection()

    def get_participant_info(self, session: HTMLSession, id: str, url_info: dict) -> list:
        """
        Returns a list of a dictionary with each participant's name, email, and school.
        Returns an empty list if no participants were found.
        """

        url: str = f'{url_info["part_info_base_url"]}{id}'
        page_content: HTMLResponse = session.get(url)
        content: list = page_content.html.find("div#RadGrid1_GridData tbody tr")

        # Convert the content into a list omitting the first element in each.
        content = [x.text.split("\n")[1:] for x in list(content)]

        participants: list = []

        for item in content:
            if len(item) > 0:
                participant = {}
                participant["name"] = item[0]
                participant["email"] = item[1]
                participant["school"] = item[2]
                participants.append(participant)

        return participants

    def get_matching_workshops(
        self, search_workshop_id=None, start_date=None, end_date=None
    ) -> list:
        """Finds all workshops that match the search criteria."""

        ws_db: WorkshopDatabase = WorkshopDatabase()
        workshops: list = []

        # Clear out number of participants
        self.number_of_participants = 0

        if search_workshop_id != None:
            workshops = self.find_with_workshop_id(search_workshop_id, ws_db)
        else:
            workshops = self.find_workshops_with_search_phrase(
                start_date, end_date, ws_db
            )

        ws_db.close_connection()
        self.number_of_workshops = len(workshops)

        return workshops

    def find_workshops_with_search_phrase(
        self, search_start_date: list, search_end_date: list, ws_db: WorkshopDatabase
    ) -> list:
        """Find workshops if a search phrase was provided in the application."""

        workshops: list = []

        for workshop in ws_db.get_all_workshops():
            if search(self.search_phrase.lower(), workshop[2].lower()) != None:
                workshop: list = list(workshop)
                workshop.append(self.make_participant_list(ws_db, workshop))

                if search_start_date == None or search_end_date == None:
                    # Search without date range.
                    workshops.append(workshop)
                    self.number_of_participants += int(workshop[4])
                else:
                    # Search with a date range.
                    search_start_date: date = date(search_start_date[0], search_start_date[1], search_start_date[2])
                    search_end_date: date = date(search_end_date[0], search_end_date[1], search_end_date[2])
                    workshop_date_info: tuple = self.get_start_date(workshop)
                    workshop_start_date = date(workshop_date_info[0], workshop_date_info[1], workshop_date_info[2])
                    if workshop_start_date >= search_start_date and workshop_start_date <= search_end_date:
                        workshops.append(workshop)
                        self.number_of_participants += int(workshop[4])

        return workshops

    def find_with_workshop_id(self, search_workshop_id: str, ws_db: WorkshopDatabase) -> list:
        """
        Find workshops based on the workshopID and return when found.
        Will iterate over all workshops incase of duplicate workshop IDs.
        This will take priority over phrase or date search.
        """

        workshops: list = []
        for workshop in ws_db.get_all_workshops():
            if search_workshop_id == workshop[1]:
                workshop = list(workshop)
                workshop.append(self.make_participant_list(ws_db, workshop))

                workshops.append(workshop)
                self.number_of_participants += int(workshop[4])

        return workshops

    def make_participant_list(self, ws_db: WorkshopDatabase, workshop: list) -> list:
        """Return a list of all participants for selected workshop."""

        participants: list = []
        for participant in ws_db.get_participant_info(workshop[1]):
            participants.append(participant)

        return participants

    def get_number_of_workshops(self) -> int:
        """Returns the total number of workshops that match phrase."""

        return self.number_of_workshops

    def get_number_of_participants(self) -> int:
        """Returns the total number of participants for matching workshops."""

        return self.number_of_participants

    def get_emails(self, workshops: list) -> str:
        """Returns a string of emails in a copy and past format for emailing participants."""

        emails: list = []

        for workshop in workshops:
            # Check if there is participant information in the workshop.
            if workshop[7] != []:
                for participant in workshop[7]:
                    # Add provided email for this participant.
                    emails.append(participant[1])

        emails = ";\n".join(emails)

        if emails == "":
            return "*** NO EMAILS TO DISPLAY! ***"
        else:
            return emails

    def get_start_date(self, workshop: list) -> tuple:
        """
        Returns a tuple of integers for the start date of the provided workshop.
        Format: (year, month, day)
        """

        workshop: list = workshop[3].split(" ")
        workshop: list = [int(x) for x in workshop[0].split("/")]
        return (workshop[2], workshop[0], workshop[1])

    def set_phrase(self, phrase: str) -> None:
        """Sets the phrase to be used in the search process."""

        replace_symbols: str = "[]\\.^$*+{}|()"
        for symbol in replace_symbols:
            phrase: str = phrase.replace(symbol, f"\\{symbol}")

        self.search_phrase = phrase

    def store_user_info(self) -> None:
        """Store the user information for later use in connection_info.json"""

        file_name: str = "connection_info.json"

        with open(file_name, "r") as f:
            connection_info: dict = load(f)

        with open(file_name, "w") as f:
            connection_info["user_name"] = f"{self.user_name}"
            connection_info["password"] = f"{self.user_password}"
            dump(connection_info, f, indent=4)

    def get_connection_info(self) -> dict:
        """Load and get the Url information from the connection_info.json file."""

        with open("connection_info.json", "r") as f:
            return load(f)

    def set_working_directory(self, target_dir: str) -> None:
        """Set the current directory to the <targetDir> dir if not already."""

        path: Path = Path(__file__)

        if path.parent.name != target_dir:
            parent_name: str = path.parent.name
            while parent_name != target_dir and path.name != parent_name:
                path: str = path.parent
            chdir(path)
        else:
            chdir(path.parent)


if __name__ == "__main__":
    print("This is a module...")
