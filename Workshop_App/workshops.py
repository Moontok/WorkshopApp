'''
This is a module created to support workshopProgramMain.py.
This has the Workshops class that is used to pull and format the information
for each workshop from the workshop url.
'''

from requests import Session
from re import search
from bs4 import BeautifulSoup
from os import path, chdir
from json import load
from datetime import date
from database import WorkshopDatabase

class Workshops():
    '''A class that contains all the workshop data and methods to get and work on that data.'''

    def __init__(self):
        self.searchPhrase = ''
        self.numberOfWorkshops = 0
        self.numberOfParticipants = 0
        self.userName = ''
        self.userPassword = ''
        self.urlInfo = self.getURLInfo()

    def connectAndUpdateDatabase(self):
        '''Connects to the escWorks webpage, logins, gather workshops, and add them to the database.'''
        
        self.getUserInfo()         

        login_data = {
            'ctl00$mainBody$txtUserName': self.userName,
            'ctl00$mainBody$txtPassword': self.userPassword,
            'ctl00$mainBody$btnSubmit': 'Submit'
            }

        with Session() as s:
            url = self.urlInfo['signin']

            pageInfo = s.get(url)
            bsObj = BeautifulSoup(pageInfo.content, 'html.parser')

            login_data['__EVENTVALIDATION'] = bsObj.find('input', attrs={'name':'__EVENTVALIDATION'})['value']     
            login_data['__VIEWSTATE'] = bsObj.find('input', attrs={'name':'__VIEWSTATE'})['value']

            s.post(url, data=login_data)
            html = s.get(self.urlInfo['targetInfoURL'])
            bsObj = BeautifulSoup(html.content, 'html.parser')

            # Collect all workshops that are listed on the webpage.
            workshopsContent = bsObj.find('table', {'class':'mainBody'}).findAll(('tr'))    

            # Convert to list for slicing and remove table headers, blank lines, and non-workshop related information.
            # Specific to the layout of the content scraped.
            workshopsContent = [list(x)[3:-1:2] for x in workshopsContent[1:]]
            
            wsDB = WorkshopDatabase()
            wsDB.createWorkshopsTables()

            for workshopInfo in workshopsContent:
                workshopDict = {}

                workshopDict['workshopID'] = workshopInfo[0].contents[0].get_text()[:6]
                workshopDict['workshopName'] = workshopInfo[0].contents[0].get_text()[9:]
                workshopDict['workshopStartDateAndTime'] = workshopInfo[0].contents[3]
                workshopDict['workshopSignedUp'] = workshopInfo[1].contents[0].split(' / ')[0]
                workshopDict['workshopParticipantCapacity'] = workshopInfo[1].contents[0].split(' / ')[1]
                workshopDict['workshopURL'] = f'{self.urlInfo["urlBase"]}{workshopDict["workshopID"]}'
                workshopDict['workshopParticipantInfoList'] = self.getParticipantInfo(s, workshopDict['workshopID'])

                wsDB.addWorkshop(workshopDict)

            wsDB.closeConnection()


    def getParticipantInfo(self, session, ID):
        '''
        Returns a list of a dictionary with each participant's name, email, and school.
        Returns an empty list if no participants were found.
        '''

        url = f'{self.urlInfo["partInfoBaseURL"]}{ID}'
        html = session.get(url)

        bsObj = BeautifulSoup(html.content, 'html.parser')
        content = bsObj.find('table', {'id':'RadGrid1_ctl00'}).tbody.findAll('tr')

        participantsList = []

        for possibleParticipant in content:        
            participant = {}
            try:
                name = possibleParticipant.find('td').next_sibling
                email = name.next_sibling
                school = email.next_sibling

                participant['name'] = name.get_text()
                participant['email'] = email.get_text()
                participant['school'] = school.get_text()
                participantsList.append(participant)
            except AttributeError:
                continue

        return participantsList


    def getMatchingWorkshops(self, searchWorkshopID=None, startDate=None, endDate=None):
        '''Finds all workshops that match the search criteria.'''

        wsDB = WorkshopDatabase()
        workshopList = []

        self.numberOfParticipants = 0 # Clear out number of participants
        
        if searchWorkshopID != None:
            # Find workshops based on the workshopID and return when found.
            # Will iterate over all workshops incase of duplicate workshop IDs.
            # This will take priority over phrase or date search.
            for workshop in wsDB.getAllWorkshops():
                if searchWorkshopID == workshop[1]:
                    workshop = list(workshop)
                    wokrshop = workshop.append(self.makeParticipantList(wsDB, workshop))

                    workshopList.append(workshop)                    
                    self.numberOfParticipants += int(workshop[4])
        else:
            # Find workshops based on a search phrase.
            for workshop in wsDB.getAllWorkshops():
                if search(self.searchPhrase.lower(), workshop[2].lower()) != None:
                    workshop = list(workshop)
                    wokrshop = workshop.append(self.makeParticipantList(wsDB, workshop))

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

        wsDB.closeConnection()            
        self.numberOfWorkshops = len(workshopList)

        return workshopList


    def makeParticipantList(self, wsDB, workshop):
        ''' Return a list of all participants for selected workshop. '''

        participants = []
        for participant in wsDB.getParticipantInfoForWorkshop(workshop[1]):
            participants.append(participant)

        return participants

    
    def getNumberOfWorkshops(self):
        '''Returns the total number of workshops that match phrase.'''

        return self.numberOfWorkshops

    def getNumberOfParticipants(self):
        '''Returns the total number of participants for matching workshops.'''

        return self.numberOfParticipants


    def getEmails(self, workshops):
        '''Returns a string of emails in a copy and past format for emailing participants.'''

        emailList = []
        
        for workshop in workshops:
            # Check if there is participant information in the workshop.
            if workshop[7] != []:
                for participant in workshop[7]:
                    # Add provided email for this participant.
                    emailList.append(participant[1])

        emails = ';\n'.join(emailList)

        if emails == '':
            return '*** NO EMAILS TO DISPLAY! ***'
        else:
            return emails

    def getStartDate(self, workshop):
        '''
        Returns a tuple of integers for the start date of the provided workshop.
        Format: (year, month, day)
        '''

        workshop = workshop[3].split(' ')
        workshop = [int(x) for x in workshop[0].split('/')]
        return (workshop[2], workshop[0], workshop[1])

    def setPhrase(self, phrase):
        '''Sets the phrase to be used in the search process.'''
        
        replaceSymbols = '[]\\.^$*+{}|()'
        for symbol in replaceSymbols:
            phrase = phrase.replace(symbol, f'\\{symbol}')

        self.searchPhrase = phrase


    def storeUserInfo(self):
        '''Store the user information for later use in userInfo.txt'''

        with open('userInfo.txt', 'w') as f:
            f.write(f'{self.userName}\n')
            f.write(self.userPassword)


    def getUserInfo(self):
        '''Retreive the user from userInfo.txt file if it exists.'''
        
        with open('userInfo.txt', 'r') as f:
            self.userName = f.readline().strip()
            self.userPassword = f.readline().strip()


    def getURLInfo(self):
        '''Load and get the Url information from the URLInfo.json file.'''
        
        with open('URLInfo.json', 'r') as f:
            return load(f)

if __name__ == '__main__':
    print('This is a module...')

