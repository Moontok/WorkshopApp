# This is a module created to support workshop_program.py.


from requests_html import Element, HTMLSession, HTMLResponse
from os import chdir
from pathlib import Path
from re import search
from json import load, dump
from datetime import datetime
from database import WorkshopDatabase


class ConnectionTool:
    """Class that connects to target webpages and scrapes target information."""

    def __init__(self):
        self.session: HTMLSession = HTMLSession()
        self.connection_info: dict = self.setup_connection_info()

        self.set_working_directory("Workshop_App")
        self.intial_connection()


    def intial_connection(self) -> None:
        """Establishes an initial connection to the sign-in page."""

        login_page_content: HTMLResponse = self.session.get(self.connection_info["signin_page_url"])            
        login_data: dict = self.setup_login_information(login_page_content)

        self.session.post(self.connection_info["signin_page_url"], data=login_data)


    def get_instructor_page(self) -> list:
        """Scrapes the workshop information from the instructor page."""

        page_content: HTMLResponse = self.session.get(self.connection_info["instructor_page_url"])
        return page_content.html.find("table.mainBody tr")


    def get_participant_page(self, id: str) -> list:
        """Scrapes the participant information for a target workshop based in provided ID."""

        participant_url: str = f'{self.connection_info["participant_page_base_url"]}{id}'
        page_content: HTMLResponse = self.session.get(participant_url)
        return page_content.html.find("div#RadGrid1_GridData tbody tr")


    def setup_connection_info(self) -> dict:
        """Load and get the Url information from the connection_info.json file."""

        with open("connection_info.json", "r") as f:
            return load(f)


    def get_connection_info_for(self, item: str) -> str:
        """Return the connection information based on provided item."""

        return self.connection_info[item]


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

    
    def store_user_info(self, user_name: str, user_password: str) -> None:
        """Store the user information for later use in connection_info.json"""

        file_name: str = "connection_info.json"

        with open(file_name, "r") as f:
            connection_info: dict = load(f)

        with open(file_name, "w") as f:
            connection_info["user_name"] = user_name
            connection_info["password"] = user_password
            dump(connection_info, f, indent=4)


    def setup_login_information(self, login_page_content: HTMLResponse) -> dict:
        """Setup login information and return it."""
        
        login_data: dict = {
            "ctl00$mainBody$txtUserName": self.connection_info["user_name"],
            "ctl00$mainBody$txtPassword": self.connection_info["password"],
            "ctl00$mainBody$btnSubmit": "Submit",
        }

        event_match: Element = login_page_content.html.find("input#__EVENTVALIDATION", first=True)
        login_data["__EVENTVALIDATION"] = event_match.attrs["value"]
        
        view_state_match: Element = login_page_content.html.find("input#__VIEWSTATE", first=True)
        login_data["__VIEWSTATE"] = view_state_match.attrs["value"]

        return login_data


    def close_session(self) -> None:
        """For good measures, closes the HTMLSession."""

        self.session.close()


class WorkshopsTool:
    def __init__(self):
        self.number_of_workshops: int = 0
        self.number_of_participants: int = 0
        self.search_phrase: str = ""
        self.connector: ConnectionTool = ConnectionTool()


    def setup_workshop_information(self) -> None:
        """Rip, organize, and clean the workshop information."""

        workshops_content: list = self.connector.get_instructor_page()

        # Convert the workshopContent into a list of lists skipping the first row of the table:
        # ['Workshop Name', 'Workshop Date and Time', 'Workshop Enrollment']
        workshops_content = [x.text.split("\n") for x in list(workshops_content)[1:]]

        workshops: list = []

        for workshop_info in workshops_content:
            workshop: dict = {}

            workshop["workshop_id"] = workshop_info[0][:6]
            workshop["workshop_name"] = workshop_info[0][9:]
            workshop["workshop_start_date_and_time"] = workshop_info[1]
            workshop["workshop_signed_up"] = workshop_info[2].split(" / ")[0]
            workshop["workshop_participant_capacity"] = workshop_info[2].split(" / ")[1]
            workshop["workshop_url"] = f'{self.connector.get_connection_info_for("base_workshop_url")}{workshop["workshop_id"]}'
            workshop["workshop_participant_info_list"] = self.construct_participant_info(workshop["workshop_id"])
            workshops.append(workshop)
    
        
        self.construct_workshop_database(workshops)
        self.connector.close_session()


    def construct_participant_info(self, id: str) -> list:
        """
        Returns a list of dictionaries with each participant's name, email, and school or
        returns an empty list if no participants were found.
        """

        content: list = self.connector.get_participant_page(id)

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


    def construct_workshop_database(self, workshops: list):
        """Create/update database and add all workshops to it."""
        
        with WorkshopDatabase() as ws_db:                  
            ws_db.create_workshop_tables()
            for workshop in workshops:
                ws_db.add_workshop(workshop)


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


    def get_matching_workshops(self) -> list:
        """Return a list of workshops that are matching the current search phrase."""

        with WorkshopDatabase() as ws_db:
            workshops: list = []
            self.number_of_participants = 0

            for workshop in ws_db.get_all_workshops():
                if search(self.search_phrase.lower(), workshop[2].lower()) != None:
                    workshop: list = list(workshop)
                    workshop.append(self.make_participant_list(ws_db, workshop))
                    workshops.append(workshop)
                    self.number_of_participants += int(workshop[4])

        self.number_of_workshops = len(workshops)

        return workshops


    def get_matching_workshops_by_date_range(self, start_date: tuple, end_date: tuple) -> list:
        """Returns al ist of matching workshops base on a provided date range."""

        # Get all workshops that match the entered search phrase.
        workshops_to_check: list = self.get_matching_workshops()
        
        searching_start_date: datetime = datetime(*start_date[:3])
        searching_end_date: datetime = datetime(*end_date[:3])

        workshops: list = []
        self.number_of_participants = 0
        
        for workshop in workshops_to_check:
            workshop_start_date: datetime = datetime.strptime(workshop[3], "%m/%d/%Y %I:%M %p")            

            if workshop_start_date >= searching_start_date and workshop_start_date <= searching_end_date:
                workshops.append(workshop)
                self.number_of_participants += int(workshop[4])

        self.number_of_workshops = len(workshops)
        return workshops


    def get_matching_workshops_by_id(self, search_workshop_id: str) -> list:
        """
        Find workshops based on the workshopID and return when found.
        This will take priority over phrase or date search.
        """

        with WorkshopDatabase() as ws_db:
            workshops: list = []
            self.number_of_participants = 0

            for workshop in ws_db.get_all_workshops():
                if search_workshop_id == workshop[1]:
                    workshop = list(workshop)
                    workshop.append(self.make_participant_list(ws_db, workshop))

                    workshops.append(workshop)
                    self.number_of_participants = int(workshop[4])
                    self.number_of_workshops = 1

                    return workshops

        self.number_of_workshops = 0
        return workshops


    def set_search_phrase(self, phrase: str) -> None:
        """Sets the phrase to be used in the search process."""

        symbols_to_replace: str = "[]\\.^$*+{}|()"
        for symbol in symbols_to_replace:
            phrase: str = phrase.replace(symbol, f"\\{symbol}")

        self.search_phrase = phrase


    def make_participant_list(self, ws_db: WorkshopDatabase, workshop: list) -> list:
        """Return a list of all participants for selected workshop."""

        return [p for p in ws_db.get_participant_info(workshop[1])]


if __name__ == "__main__":
    print("This is a module...")
