'''
This is a module created to support workshopProgramMain.py.
This has the Workshops class that is used to pull and format the information
for each workshop from the workshop url.
'''

from requests import Session
from re import findall, search, M
from bs4 import BeautifulSoup
from os import path, chdir
from json import load

class Workshops():
    '''A class that contains all the workshop data and methods to get and work on that data.'''

    def __init__(self):
        self.workshopKeywords = ''
        self.userName = ''
        self.userPassword = ''
        self.workshopList = {}
        self.numberOfParticipants = 0
        self.urlInfo = self.getURLInfo()

    def connectAndGenerateInformation(self):
        '''Connect to the escWorks webpage, login, and collect page content.'''
                
        self.getUserInfo()            

        login_data = {
            'ctl00$mainBody$txtUserName': self.userName,
            'ctl00$mainBody$txtPassword': self.userPassword,
            'ctl00$mainBody$btnSubmit': 'Submit'
        }

        with Session() as s:
            #url = "https://www.escweb.net/ar_esc/security/signin.aspx"
            url = self.urlInfo['signin']

            pageInfo = s.get(url)
            soup = BeautifulSoup(pageInfo.content, 'html.parser')

            login_data['__EVENTVALIDATION'] = soup.find('input', attrs={'name':'__EVENTVALIDATION'})['value']
            login_data['__VIEWSTATE'] = soup.find('input', attrs={'name':'__VIEWSTATE'})['value']

            s.post(url, data=login_data)
            #rawPageContent = s.get('https://www.escweb.net/ar_esc/instructor/default.aspx').text
            rawPageContent = s.get(self.urlInfo['targetInfoURL']).text

            pageContent = self.findMatches(rawPageContent)
        
            self.cleanAndOrganizeInformation(s, pageContent)


    def findMatches(self, content):
        '''Finds all workshops that match the keywords defined.'''

        seekingText = f'em>.*{self.workshopKeywords}.*\\n.*/td>'
        rawList = findall(seekingText, content, M)
        return rawList


    def cleanAndOrganizeInformation(self, session, pageContent):
        '''
        This function searches through pageContent and finds specific data items:
        'workshopID', 'workshopName', 'workshopStartDate', 'workshopStartDate', 'workshopParticipantNumberInfo',
        'workshopURL', 'participantInfoList'
        '''

        workshops = []
        participantTotal = 0

        for training in pageContent:
            workshop = {}
            workshop['workshopID'] = search('[0-9]+', training)[0]
            
            rawName = search('-.*</em>', training)[0]
            workshop['workshopName'] = rawName[2:-5]
            
            workshop['workshopStartDate'] = search('[0-9]+/[0-9]+/[0-9]+', training)[0]

            workshop['workshopParticipantNumberInfo'] = search('[0-9]+ / [0-9]+', training)[0]
            #workshop['workshopURL'] = f'https://www.escweb.net/ar_esc/catalog/session.aspx?session_id={workshop["workshopID"]}'
            workshop['workshopURL'] = f'{self.urlInfo["urlBase"]}{workshop["workshopID"]}'

            workshop['participantInfoList'] = self.generateParticipantInfo(session, workshop['workshopID'])

            workshops.append(workshop)
            
            participantTotal += int(workshop['workshopParticipantNumberInfo'].split(' / ')[0])

        self.workshopList = workshops
        self.numberOfParticipants = participantTotal


    def generateParticipantInfo(self, session, ID):
        '''Returns the participant name, email, and school.'''

        #url = f'https://www.escweb.net/ar_esc/instructor/instructor.aspx?session_id={ID}'
        url = f'{self.urlInfo["partInfoBaseURL"]}{ID}'

        pageContent = session.get(url).text # Get the html for the above url.
        
        infoList = findall('">.*@.*</td>', pageContent) # Search for particpant information based on email address.

        cleanInfoList = []
        
        for participantInfo in infoList:
            splitList = participantInfo.split('<td>')
            name = splitList[0][2:-5]
            email = splitList[1][:-5]
            school = splitList[2][:-5]

            cleanInfoList.append([name, email, school])
        
        return cleanInfoList


    def getNumberOfWorkshops(self):
        '''Returns the total number of workshops that match keywords.'''

        return len(self.workshopList)


    def getEmails(self):
        '''Returns a string of emails in a copy and past format for emailing participants.'''

        emails = ''
        for workshop in self.workshopList:
            for participantInfo in workshop['participantInfoList']:
                emails = f'{emails}{participantInfo[1]};\n'

        return emails


    def getWorkshops(self):
        '''Returns a list of all the workshop dictionaries that matched the keywords.'''

        return self.workshopList


    def getTotalNumberOfParticipants(self):
        '''Return the total number of participants in all matching workshops.'''
        
        return self.numberOfParticipants


    def setKeywords(self, keywords):
        '''Sets the keywords to be used in the search process.'''

        self.workshopKeywords = keywords


    def storeUserInfo(self):
        '''Store the user information for later use in userInfo.txt'''

        dirPath = path.dirname(path.realpath(__file__))
        chdir(dirPath)

        with open('userInfo.txt', 'w') as f:
            f.write(f'{self.userName}\n')
            f.write(self.userPassword)


    def getUserInfo(self):
        '''Retreive the user from userInfo.txt file if it exists.'''

        dirPath = path.dirname(path.realpath(__file__))
        chdir(dirPath)
        
        with open('userInfo.txt', 'r') as f:
            self.userName = f.readline().strip()
            self.userPassword = f.readline().strip()


    def getURLInfo(self):
        '''Load and get the Url information from the URLInfo.json file.'''

        dirPath = path.dirname(path.realpath(__file__))
        chdir(dirPath)
        
        with open('URLInfo.json', 'r') as f:
            return load(f)


if __name__ == '__main__':
    print('This is a module...')
