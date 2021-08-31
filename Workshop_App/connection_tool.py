# Module to handle connecting and scraping webpages.

from requests_html import Element, HTMLSession, HTMLResponse
from os import chdir
from pathlib import Path
from json import load, dump


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
