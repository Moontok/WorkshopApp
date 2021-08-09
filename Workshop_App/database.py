from sqlite3 import connect, OperationalError

class WorkshopDatabase:
    '''Database to store workshop information for quicker access during use.'''

    def __init__(self):
        self.connection = connect('workshops.db')
        self.c = self.connection.cursor()

    def createWorkshopsTables(self) -> None:
        '''Setup workshop database.'''

        # Clear the tables in the database.
        self.dropTables()

        self.c.execute('''CREATE TABLE IF NOT EXISTS workshops (
                    id INTEGER PRIMARY KEY,
                    workshopID TEXT NOT NULL,
                    workshopName TEXT NOT NULL,
                    workshopStartDateAndTime TEXT NOT NULL,
                    workshopSignedUp TEXT NOT NULL,
                    workshopParticipantCapacity TEXT NOT NULL,
                    workshopURL TEXT NOT NULL
                    );''')

        self.c.execute('''CREATE TABLE IF NOT EXISTS participantInformation (
                    id INTEGER PRIMARY KEY,
                    workshopID TEXT NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    school TEXT NOT NULL
                    );''')


    def addWorkshop(self, wsDict: dict) -> None:
        '''Add a workshop to database.'''

        self.c.execute('INSERT INTO workshops (workshopID, workshopName, workshopStartDateAndTime, workshopSignedUp, workshopParticipantCapacity, workshopURL) VALUES (?,?,?,?,?,?)',
            (wsDict['workshopID'], wsDict['workshopName'], wsDict['workshopStartDateAndTime'], wsDict['workshopSignedUp'], wsDict['workshopParticipantCapacity'], wsDict['workshopURL']))

        for participant in wsDict['workshopParticipantInfoList']:
            self.c.execute('INSERT INTO participantInformation (workshopID, name, email, school) VALUES (?,?,?,?)',
                (wsDict['workshopID'], participant['name'], participant['email'], participant['school']))

        self.connection.commit()


    def getAllWorkshops(self) -> list:
        '''Return all workshops in database for testing purposes.'''

        workshops: list = []

        try:
            for workshop in self.c.execute('SELECT * FROM workshops'):
                workshops.append(workshop)                
        except OperationalError:
            print('No database located.')

        return workshops


    def getParticipantInfoForWorkshop(self, workshopID):
        '''Retrieve the partipant information that corresponds to the id.'''
        return self.c.execute('SELECT name, email, school FROM participantInformation WHERE workshopID = ?', (workshopID,))


    def dropTables(self):
        ''' Clear all tables in the database.'''

        self.c.execute('DROP TABLE IF EXISTS workshops;',)
        self.c.execute('DROP TABLE IF EXISTS participantInformation;',)


    def closeConnection(self):
        ''' Closes the database connection.'''

        self.c.close()
        self.connection.close()


if __name__ == '__main__':
    print('This is a module...')
    