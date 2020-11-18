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
                    name TEXT NOT NULL,
                    startDate TEXT NOT NULL,
                    participantNumberInfo TEXT NOT NULL,
                    uRL TEXT NOT NULL,
                    participantInfo TEXT NOT NULL
                    );''')


    def addWorkshop(self, wd):
        '''Add workshop to database.'''

        participantInfo = 'No participants'
        for participant in wd['participantInfoList']:
            if participantInfo == 'No participants':
                participantInfo = f'{"".join(participant)}'
            else:
                participantInfo = f'{participantInfo} -- {";".join(participant)}'

        self.c.execute('INSERT INTO workshops (id, name, startDate, participantNumberInfo, uRL, participantInfo) VALUES (?,?,?,?,?,?)',
            (wd['workshopID'], wd['workshopName'], wd['workshopStartDate'], wd['workshopParticipantNumberInfo'], wd['workshopURL'], participantInfo))
        self.connection.commit()


    def lookupWorkshop(self, wd):
        '''Lookup workshop and return it or None if workshop is not in database.'''

        for workshop in self.c.execute('SELECT * FROM workshops'):
            if workshop[0] == wd['workshopID']:
                return workshop
        return None


    def replaceWorkshop(self, wd):
        '''Replace any workshops if they already exist.'''

        self.c.execute('DELETE FROM workshops WHERE id = ?', (wd['workshopID'],))
        self.addWorkshop(wd)


    def showWorkshops(self):
        '''Print all workshops in database for testing purposes.'''

        for workshop in self.c.execute('SELECT * FROM workshops'):
            print('-')
            print(workshop)


if __name__ == '__main__':
    print('This is a module...')
    