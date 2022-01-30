# This is a module created to support workshop_program.py.


from json import load
from connection_tool import ConnectionTool
from re import search
from datetime import datetime
from database import WorkshopDatabase


class WorkshopsTool:
    def __init__(self):
        self.number_of_workshops: int = 0
        self.number_of_participants: int = 0
        self.search_phrase: str = ""
        self.connector = ConnectionTool()
        self.searched_workshops = list()
        self.workshops_dict = dict()


    def setup_workshop_information(self) -> None:
        """Rip, organize, and clean the workshop information."""

        workshops_from_instructor_page: list = self.connector.get_instructor_page()

        workshops = list()        

        for workshop_info in workshops_from_instructor_page:
            workshop = dict()

            workshop["workshop_id"] = workshop_info[0][:6]
            workshop["workshop_start_date_and_time"] = workshop_info[1]          
            workshop["workshop_url"] = f'{self.connector.get_connection_info_for("base_workshop_url")}{workshop["workshop_id"]}'
            workshop_information: dict = self.connector.get_session_page_content(workshop["workshop_url"])
            workshop["workshop_name"] = workshop_information["name"]
            workshop["workshop_description"] = workshop_information["description"]
            workshop["workshop_signed_up"] = workshop_information["seats_filled"].split(" / ")[0]
            workshop["workshop_participant_capacity"] = workshop_information["seats_filled"].split(" / ")[1]
            workshop["workshop_location"] =  workshop_information["location"]            
            workshop["workshop_dates"] = workshop_information["dates"]
            workshop["workshop_credits"] = workshop_information["credits"]
            workshop["workshop_fees"] = workshop_information["fee"] 
            workshop["workshop_participant_info_list"] = self.construct_participant_info(workshop["workshop_id"])
            workshops.append(workshop)    
        
        self.construct_workshop_database(workshops)
        self.connector.close_session()

    def construct_participant_info(self, id: str) -> dict:
        """
        Returns a list of dictionaries with each participant's name, email, and school or
        returns an empty list if no participants were found.
        """

        content: list = self.connector.get_participant_page(id)

        participants = list()

        for item in content:
            if len(item) > 0:
                participant = dict()
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


    def get_last_search_phrase(self) -> str:
        """Returns the last thing searched. """
        return self.search_phrase


    def get_emails(self) -> str:
        """Returns a string of emails in a copy and past format for emailing participants."""

        emails = list()

        for workshop in self.searched_workshops:
            # Check if there is participant information in the workshop.
            if workshop["workshop_participant_info_list"] != []:
                for participant in workshop["workshop_participant_info_list"]:
                    # Add provided email for this participant.
                    emails.append(participant["email"])

        emails = ";\n".join(emails)

        if emails == "":
            return "*** NO EMAILS TO DISPLAY! ***"
        else:
            return emails


    def get_matching_workshops(self) -> list:
        """Return a list of workshops that are matching the current search phrase."""
        
        self.searched_workshops.clear()
        self.workshops_dict.clear()

        with WorkshopDatabase() as ws_db:
            self.number_of_participants = 0

            for workshop in ws_db.get_all_workshops():
                if search(self.search_phrase.lower(), workshop["workshop_name"].lower()) != None:
                    self.searched_workshops.append(workshop)
                    self.number_of_participants += int(workshop["workshop_signed_up"])

        self.number_of_workshops = len(self.searched_workshops)

        return self.searched_workshops


    def get_matching_workshops_by_date_range(self, start_date: tuple, end_date: tuple) -> list:
        """Returns al ist of matching workshops base on a provided date range."""

        # Get a copy of all workshops that match the entered search phrase.
        workshops_to_check: list = self.get_matching_workshops()[:]
        self.searched_workshops.clear()

        searching_start_date: datetime = datetime(*start_date[:3])
        searching_end_date: datetime = datetime(*end_date[:3])

        self.number_of_participants = 0
        
        for workshop in workshops_to_check:
            workshop_start_date: datetime = datetime.strptime(workshop["workshop_start_date_and_time"], "%m/%d/%Y %I:%M %p")            

            if workshop_start_date >= searching_start_date and workshop_start_date <= searching_end_date:
                self.searched_workshops.append(workshop)
                self.number_of_participants += int(workshop["workshop_signed_up"])

        self.number_of_workshops = len(self.searched_workshops)
        return self.searched_workshops


    def get_matching_workshops_by_id(self, search_workshop_id: str) -> list:
        """
        Find workshops based on the workshopID and return when found.
        This will take priority over phrase or date search.
        """

        self.searched_workshops.clear()

        with WorkshopDatabase() as ws_db:
            self.number_of_participants = 0

            for workshop in ws_db.get_all_workshops():
                if search_workshop_id == workshop["workshop_id"]:
                    self.searched_workshops.append(workshop)
                    self.number_of_participants = int(workshop["workshop_signed_up"])
                    self.number_of_workshops = 1

                    return self.searched_workshops

        self.number_of_workshops = 0
        return self.search_workshops


    def get_most_recent_search_results(self) -> list:
        """Return the most recent workshop search results."""

        return self.searched_workshops    

    
    def get_co_op_info(self) -> dict:
        """Load and get the Session Location information from the co_op_names.json file."""

        with open("co_op_names.json", "r") as f:
            return load(f)


    def set_search_phrase(self, phrase: str) -> None:
        """Sets the phrase to be used in the search process."""

        symbols_to_replace: str = "[]\\.^$*+{}|()"
        for symbol in symbols_to_replace:
            phrase: str = phrase.replace(symbol, f"\\{symbol}")

        self.search_phrase = phrase


if __name__ == "__main__":
    print("This is a module...")
