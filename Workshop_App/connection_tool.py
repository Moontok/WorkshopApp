# Module to handle connecting, scraping webpages, and getting file content.


# from requests_html import Element, HTMLSession, HTMLResponse
from requests import Session
from bs4 import BeautifulSoup
from json import load, dump


class ConnectionTool:
    """Class that connects to target webpages and scrapes target information."""

    def __init__(self):
        self.session: Session = Session()
        self.connection_info: dict = self.setup_connection_info()

        self.intial_connection()


    def intial_connection(self) -> None:
        """Establishes an initial connection to the sign-in page."""

        login_page_content = self.session.get(self.connection_info["signin_page_url"])            
        login_data: dict = self.setup_login_information(login_page_content)

        self.session.post(self.connection_info["signin_page_url"], data=login_data)

    def get_instructor_page(self) -> list:
        """Scrapes the workshop information from the instructor page."""

        html = self.session.get(self.connection_info["instructor_page_url"])
        bs_obj = BeautifulSoup(html.content, "html.parser")

        # Convert the workshopContent into a list of lists skipping the first row of the table:
        # ['Workshop Name', 'Workshop Date and Time', 'Workshop Enrollment']
        workshops_table = []
        for workshop in bs_obj.find("table", class_="mainBody").find_all("tr")[1:]:
            elements = workshop.find_all("td")[1:]
            name = elements[0].find("em").text
            date = str(elements[0]).split("<br/>")[1][0:-5]
            signed_up = elements[1].text
            workshops_table.append([name, date, signed_up])
        
        return workshops_table



    def get_session_page_content(self, session_url: str) -> dict:
        """Returns the location and dates from session page."""

        session_page_html: Session = self.session.get(session_url)
        
        bs_obj = BeautifulSoup(session_page_html.content, "html.parser")
        workshop_information = dict()

        date_and_location_table = bs_obj.find(class_="form-group col-xs-12 col-sm-12 mainBodySmall").find_all("tr")[2:]
        date_and_location_filtered_content = [x.text.strip().split("\n") for x in date_and_location_table if len(x.text.strip()) > 0]
        dates = [x[0] for x in date_and_location_filtered_content]

        workshop_information["name"] = bs_obj.find(id="ctl00_mainBody_lblTitle").text
        workshop_information["dates"] = "_".join(dates)
        workshop_information["location"] = date_and_location_filtered_content[0][2]
        workshop_information["description"] = bs_obj.find(id="ctl00_mainBody_lblDescription").text
        workshop_information["fee"] = bs_obj.find(id="ctl00_mainBody_lblFee").text
        workshop_information["credits"] = bs_obj.find(id="ctl00_mainBody_lblCredits").text
        workshop_information["seats_filled"] = bs_obj.find(id="ctl00_mainBody_lblSeatsFilled").text

        return workshop_information



    def get_participant_page(self, id: str) -> list:
        """Scrapes the participant information for a target workshop based in provided ID."""

        participant_url: str = f'{self.connection_info["participant_page_base_url"]}{id}'
        page_html: Session = self.session.get(participant_url)
        bs_obj = BeautifulSoup(page_html.content, "html.parser")
        elements = bs_obj.find(id="RadGrid1_ctl00").find_all("tr")[1:]

        participants = []

        for element in elements:
            signed_up = element.find_all("td")[1:]
            if len(signed_up) > 0:
                participants.append([signed_up[0].text, signed_up[1].text, signed_up[2].text])
        
        return participants


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


    def setup_login_information(self, login_page_content) -> dict:
        """Setup login information and return it."""
        
        login_data: dict = {
            "ctl00$mainBody$txtUserName": self.connection_info["user_name"],
            "ctl00$mainBody$txtPassword": self.connection_info["password"],
            "ctl00$mainBody$btnSubmit": "Submit",
        }

        bs_obj = BeautifulSoup(login_page_content.content, "html.parser")
        login_data["__EVENTVALIDATION"] = bs_obj.find("input", attrs={"name":"__EVENTVALIDATION"})["value"]
        login_data["__VIEWSTATE"] = bs_obj.find("input", attrs={"name":"__VIEWSTATE"})["value"]

        return login_data


    def close_session(self) -> None:
        """For good measures, closes the HTMLSession."""

        self.session.close()


if __name__ == "__main__":
    print("This is a module...")
