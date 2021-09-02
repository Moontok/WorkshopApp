# Module to handle connecting, scraping webpages, and getting file content.


from requests_html import Element, HTMLSession, HTMLResponse
from json import load, dump


class ConnectionTool:
    """Class that connects to target webpages and scrapes target information."""

    def __init__(self):
        self.session: HTMLSession = HTMLSession()
        self.connection_info: dict = self.setup_connection_info()

        self.intial_connection()


    def intial_connection(self) -> None:
        """Establishes an initial connection to the sign-in page."""

        login_page_content: HTMLResponse = self.session.get(self.connection_info["signin_page_url"])            
        login_data: dict = self.setup_login_information(login_page_content)

        self.session.post(self.connection_info["signin_page_url"], data=login_data)


    def get_instructor_page(self) -> list:
        """Scrapes the workshop information from the instructor page."""

        page_content: HTMLResponse = self.session.get(self.connection_info["instructor_page_url"])
        workshops_table: list =  page_content.html.find("table.mainBody tr")
        
        # Convert the workshopContent into a list of lists skipping the first row of the table:
        # ['Workshop Name', 'Workshop Date and Time', 'Workshop Enrollment']
        return[x.text.split("\n") for x in list(workshops_table)[1:]]


    def get_session_page_content(self, session_url: str) -> dict:
        """Returns the location and dates from session page."""

        session_page_content: HTMLResponse = self.session.get(session_url)
        workshop_information = dict()

        date_and_location_table = list(session_page_content.html.find("table.mainBody tr td"))
        date_and_location_filtered_content: list = date_and_location_table[6:]
        dates: str = ""
        for index, element in enumerate(date_and_location_filtered_content):            
            if index % 3 == 0:
                if dates == "":
                    dates = element.text
                else:
                    dates = f"{dates}_{element.text}"

        workshop_information["name"] = session_page_content.html.find("span#ctl00_mainBody_lblTitle", first=True).text
        workshop_information["dates"] = dates
        workshop_information["location"] = date_and_location_filtered_content[2].text
        workshop_information["description"] = session_page_content.html.find("span#ctl00_mainBody_lblDescription", first=True).text
        workshop_information["fee"] = session_page_content.html.find("span#ctl00_mainBody_lblFee", first=True).text
        workshop_information["credits"] = session_page_content.html.find("span#ctl00_mainBody_lblCredits", first=True).text
        workshop_information["seats_filled"] = session_page_content.html.find("span#ctl00_mainBody_lblSeatsFilled", first=True).text

        return workshop_information



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


if __name__ == "__main__":
    print("This is a module...")
