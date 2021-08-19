"""
This is a module created to support workshopProgramMain.py.
This has the Workshops class that is used to pull and format the information
for each workshop from the workshop url.
"""

from requests_html import HTMLSession
from os import chdir
from pathlib import Path
from re import search
from json import load
from datetime import date
from database import WorkshopDatabase


class Workshops:
    """A class that contains all the workshop data and methods to get and work on that data."""

    def __init__(self):
        self.searchPhrase: str = ""
        self.numberOfWorkshops: int = 0
        self.numberOfParticipants: int = 0
        self.userName: str = ""
        self.userPassword: str = ""
        self.setWorkingDirectory("Workshop_App")

    def connectAndUpdateDatabase(self) -> None:
        """Connects to the escWorks webpage, logins, gather workshops, and add them to the database."""

        self.getUserInfo()
        urlInfo = self.getURLInfo()

        login_data: dict = {
            "ctl00$mainBody$txtUserName": self.userName,
            "ctl00$mainBody$txtPassword": self.userPassword,
            "ctl00$mainBody$btnSubmit": "Submit",
        }

        with HTMLSession() as s:
            url = urlInfo["signin"]

            loginPageContent = s.get(url)

            eventMatch = loginPageContent.html.find(
                "input#__EVENTVALIDATION", first=True
            )
            login_data["__EVENTVALIDATION"] = eventMatch.attrs["value"]
            viewStateMatch = loginPageContent.html.find("input#__VIEWSTATE", first=True)
            login_data["__VIEWSTATE"] = viewStateMatch.attrs["value"]

            s.post(url, data=login_data)
            instructorPageContent = s.get(urlInfo["targetInfoURL"])

        # Collect all workshops that are listed on the webpage.
        workshopsContent = instructorPageContent.html.find("table.mainBody tr")

        # Convert the workshopContent into a list of lists skipping the first row of the table.
        # The content of each element is as follows:
        # ['Workshop Name', 'Workshop Date and Time', 'Workshop Enrollment']
        workshopsContent = [x.text.split("\n") for x in list(workshopsContent)[1:]]

        wsDB = WorkshopDatabase()
        wsDB.createWorkshopsTables()

        for workshopInfo in workshopsContent:
            workshopDict = {}

            workshopDict["workshopID"] = workshopInfo[0][:6]
            workshopDict["workshopName"] = workshopInfo[0][9:]
            workshopDict["workshopStartDateAndTime"] = workshopInfo[1]
            workshopDict["workshopSignedUp"] = workshopInfo[2].split(" / ")[0]
            workshopDict["workshopParticipantCapacity"] = workshopInfo[2].split(" / ")[1]
            workshopDict["workshopURL"] = f'{urlInfo["urlBase"]}{workshopDict["workshopID"]}'
            workshopDict["workshopParticipantInfoList"] = self.getParticipantInfo(s, workshopDict["workshopID"], urlInfo)

            wsDB.addWorkshop(workshopDict)

        wsDB.closeConnection()

    def getParticipantInfo(self, session, ID, urlInfo) -> list:
        """Returns a list of a dictionary with each participant's name, email, and school.
        Returns an empty list if no participants were found.
        """

        url = f'{urlInfo["partInfoBaseURL"]}{ID}'
        pageContent = session.get(url)
        content = pageContent.html.find("div#RadGrid1_GridData tbody tr")

        # Convert the content into a list omitting the first element in each.
        content = [x.text.split("\n")[1:] for x in list(content)]

        participantsList = []

        for item in content:
            if len(item) > 0:
                participant = {}
                participant["name"] = item[0]
                participant["email"] = item[1]
                participant["school"] = item[2]
                participantsList.append(participant)

        return participantsList

    def getMatchingWorkshops(
        self, searchWorkshopID=None, startDate=None, endDate=None
    ) -> None:
        """Finds all workshops that match the search criteria."""

        wsDB: WorkshopDatabase = WorkshopDatabase()
        workshopList: list = []

        self.numberOfParticipants = 0  # Clear out number of participants

        if searchWorkshopID != None:
            workshopList = self.find_with_workshop_ID(searchWorkshopID, wsDB)
        else:
            workshopList = self.find_workshops_with_search_phrase(
                startDate, endDate, wsDB
            )

        wsDB.closeConnection()
        self.numberOfWorkshops = len(workshopList)

        return workshopList

    def find_workshops_with_search_phrase(
        self, startDate: list, endDate: list, wsDB: WorkshopDatabase
    ) -> list:
        """Find workshops if a search phrase was provided in the application."""

        workshopList: list = []

        for workshop in wsDB.getAllWorkshops():
            if search(self.searchPhrase.lower(), workshop[2].lower()) != None:
                workshop = list(workshop)
                workshop.append(self.makeParticipantList(wsDB, workshop))

                if startDate == None or endDate == None:
                    # Search without date range.
                    workshopList.append(workshop)
                    self.numberOfParticipants += int(workshop[4])
                else:
                    # Search with a date range.
                    startDateObj = date(startDate[0], startDate[1], startDate[2])
                    endDateObj = date(endDate[0], endDate[1], endDate[2])
                    wsStartDate = self.getStartDate(workshop)
                    wsStartDate = date(wsStartDate[0], wsStartDate[1], wsStartDate[2])
                    if wsStartDate >= startDateObj and wsStartDate <= endDateObj:
                        workshopList.append(workshop)
                        self.numberOfParticipants += int(workshop[4])

        return workshopList

    def find_with_workshop_ID(self, searchWorkshopID, wsDB, workshopList) -> list:
        """Find workshops based on the workshopID and return when found.
        Will iterate over all workshops incase of duplicate workshop IDs.
        This will take priority over phrase or date search.
        """

        workshopList = []
        for workshop in wsDB.getAllWorkshops():
            if searchWorkshopID == workshop[1]:
                workshop = list(workshop)
                workshop.append(self.makeParticipantList(wsDB, workshop))

                workshopList.append(workshop)
                self.numberOfParticipants += int(workshop[4])

        return workshopList

    def makeParticipantList(self, wsDB, workshop) -> list:
        """Return a list of all participants for selected workshop."""

        participants = []
        for participant in wsDB.getParticipantInfoForWorkshop(workshop[1]):
            participants.append(participant)

        return participants

    def getNumberOfWorkshops(self) -> int:
        """Returns the total number of workshops that match phrase."""

        return self.numberOfWorkshops

    def getNumberOfParticipants(self) -> int:
        """Returns the total number of participants for matching workshops."""

        return self.numberOfParticipants

    def getEmails(self, workshops) -> str:
        """Returns a string of emails in a copy and past format for emailing participants."""

        emailList = []

        for workshop in workshops:
            # Check if there is participant information in the workshop.
            if workshop[7] != []:
                for participant in workshop[7]:
                    # Add provided email for this participant.
                    emailList.append(participant[1])

        emails = ";\n".join(emailList)

        if emails == "":
            return "*** NO EMAILS TO DISPLAY! ***"
        else:
            return emails

    def getStartDate(self, workshop) -> tuple:
        """Returns a tuple of integers for the start date of the provided workshop.
        Format: (year, month, day)
        """

        workshop: list = workshop[3].split(" ")
        workshop: list = [int(x) for x in workshop[0].split("/")]
        return (workshop[2], workshop[0], workshop[1])

    def setPhrase(self, phrase: str) -> None:
        """Sets the phrase to be used in the search process."""

        replaceSymbols: str = "[]\\.^$*+{}|()"
        for symbol in replaceSymbols:
            phrase = phrase.replace(symbol, f"\\{symbol}")

        self.searchPhrase = phrase

    def storeUserInfo(self) -> None:
        """Store the user information for later use in userInfo.txt"""

        with open("userInfo.txt", "w") as f:
            f.write(f"{self.userName}\n")
            f.write(self.userPassword)

    def getUserInfo(self) -> None:
        """Retreive the user from userInfo.txt file if it exists."""

        with open("userInfo.txt", "r") as f:
            self.userName = f.readline().strip()
            self.userPassword = f.readline().strip()

    def getURLInfo(self) -> dict:
        """Load and get the Url information from the URLInfo.json file."""

        with open("URLInfo.json", "r") as f:
            return load(f)

    def setWorkingDirectory(self, targetDir: str) -> None:
        """Set the current directory to the <targetDir> dir if not already."""

        path: Path = Path(__file__)

        if path.parent.name != targetDir:
            parentName: str = path.parent.name
            while parentName != targetDir and path.name != parentName:
                path: str = path.parent
            chdir(path)
        else:
            chdir(path.parent)


if __name__ == "__main__":
    print("This is a module...")
