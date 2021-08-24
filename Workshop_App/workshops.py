# This is a module created to support workshopProgramMain.py.
# This has the Workshops class that is used to pull and format the information
# for each workshop from the workshop url.


from requests_html import Element, HTMLSession, HTMLResponse
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

        with HTMLSession() as session:
            login_page_content: HTMLResponse = session.get(connection_info["signin_page_url"])

            login_data: dict = self.setup_login_information(login_page_content, connection_info)

            session.post(connection_info["signin_page_url"], data=login_data)
            instructor_page_content: HTMLResponse = session.get(connection_info["instructor_page_url"])

            # Collect all workshops that are listed on the webpage.
            workshops_content: list = instructor_page_content.html.find("table.mainBody tr")

            # Convert the workshopContent into a list of lists skipping the first row of the table.
            # The content of each element is as follows:
            # ['Workshop Name', 'Workshop Date and Time', 'Workshop Enrollment']
            workshops_content = [x.text.split("\n") for x in list(workshops_content)[1:]]

            url_base: str = connection_info["base_workshop_url"]
            workshops: list = []

            for workshop_info in workshops_content:
                workshop: dict = {}

                workshop["workshop_id"] = workshop_info[0][:6]
                workshop["workshop_name"] = workshop_info[0][9:]
                workshop["workshop_start_date_and_time"] = workshop_info[1]
                workshop["workshop_signed_up"] = workshop_info[2].split(" / ")[0]
                workshop["workshop_participant_capacity"] = workshop_info[2].split(" / ")[1]
                workshop["workshop_url"] = f'{url_base}{workshop["workshop_id"]}'
                workshop["workshop_participant_info_list"] = self.get_participant_info(session, workshop["workshop_id"], connection_info["participant_page_base_url"])
                workshops.append(workshop)
        
        self.construct_workshop_database(workshops)

    def construct_workshop_database(self, workshops: list):
        """Create/update database and add all workshops to it."""
        
        ws_db: WorkshopDatabase = WorkshopDatabase()
        ws_db.create_workshops_tables()
        for workshop in workshops:
            ws_db.add_workshop(workshop)
        ws_db.close_connection()

    
    def get_participant_info(self, session: HTMLSession, id: str, participant_url: str) -> list:
        """
        Returns a list of a dictionary with each participant's name, email, and school.
        Returns an empty list if no participants were found.
        """

        page_content: HTMLResponse = session.get(f'{participant_url}{id}')
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
        self, search_workshop_id: str=None, start_date: tuple=None, end_date: tuple=None
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
        self, search_start_date: tuple, search_end_date: tuple, ws_db: WorkshopDatabase
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
                    searching_start_date: date = date(*search_start_date[:3])
                    searching_ending_date: date = date(*search_end_date[:3])
                    workshop_start_date: date = self.get_start_date(workshop)

                    if workshop_start_date >= searching_start_date and workshop_start_date <= searching_ending_date:
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


    def setup_login_information(self, login_page_content: HTMLResponse, connection_info: dict) -> dict:
        """Setup login information and return it."""
        
        login_data: dict = {
            "ctl00$mainBody$txtUserName": connection_info["user_name"],
            "ctl00$mainBody$txtPassword": connection_info["password"],
            "ctl00$mainBody$btnSubmit": "Submit",
        }

        event_match: Element = login_page_content.html.find("input#__EVENTVALIDATION", first=True)
        login_data["__EVENTVALIDATION"] = event_match.attrs["value"]
        
        view_state_match: Element = login_page_content.html.find("input#__VIEWSTATE", first=True)
        login_data["__VIEWSTATE"] = view_state_match.attrs["value"]

        return login_data

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

    def get_start_date(self, workshop: list) -> date:
        """
        Returns a date object for the start date of the provided workshop.
        Format: (year, month, day)
        """

        workshop: list = workshop[3].split(" ")
        workshop = [int(x) for x in workshop[0].split("/")]
        return date(workshop[2], workshop[0], workshop[1])

    def set_phrase(self, phrase: str) -> None:
        """Sets the phrase to be used in the search process."""

        symbols_to_replace: str = "[]\\.^$*+{}|()"
        for symbol in symbols_to_replace:
            phrase: str = phrase.replace(symbol, f"\\{symbol}")

        self.search_phrase = phrase

    def store_user_info(self) -> None:
        """Store the user information for later use in connection_info.json"""

        file_name: str = "connection_info.json"

        with open(file_name, "r") as f:
            connection_info: dict = load(f)

        with open(file_name, "w") as f:            
            connection_info: dict = load(f)
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
