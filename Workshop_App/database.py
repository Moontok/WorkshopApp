from sqlite3 import connect

class WorkshopDatabase:
    '''Database to store workshop information.'''

    def __init__(self):
        self.connection = connect('workshops.db')
        self.c = self.connection.cursor()
        self.createWorkshopsTable()

    def createWorkshopsTable(self):
        '''Setup database.'''

        self.c.execute('''CREATE TABLE IF NOT EXISTS workshops (
                     id INTEGER PRIMARY KEY,
                     workshopID TEXT NOT NULL,
                     workshopName TEXT NOT NULL,
                     workshopStartDate TEXT NOT NULL,
                     workshopParticipantNumberInfo TEXT NOT NULL,
                     workshopURL TEXT NOT NULL,
                     participantInfoList TEXT NOT NULL
                     );''')

    def addWorkshop(self, wd):
        print('Adding workshop...')
        self.c.execute(
            'INSERT INTO workshops (workshopID, workshopName, workshopStartDate, workshopParticipantNumberInfo, workshopURL, participantInfoList) VALUES (?,?,?,?,?,?)',
            (wd['workshopID'], wd['workshopName'], wd['workshopStartDate'], wd['workshopParticipantNumberInfo'], wd['workshopURL'], wd['participantInfoList']))
        self.conn.commit()

    def lookupWorkshop(self, workshopID):
        for workshop in self.c.execute('SELECT * FROM workshops'):
            if workshop[1] == workshopID:
                return workshop
        return None

    def showWorkshops(self):
        for workshop in self.c.execute('SELECT * FROM workshops'):
            print('-')
            print(workshop)
