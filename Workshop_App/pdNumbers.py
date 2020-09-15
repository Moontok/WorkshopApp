from workshops import Workshops

def main():
    # Useful information when using:
    # workshops keys:'workshopID', 'workshopName', 'workshopStartDate', 'workshopParticipantNumberInfo', 'workshopURL', 'participantInfoList'
    # participantInfoList [name, email, school]
    
    trainingKeywords = 'Prep' # Keyword to search for in training titles.
    
    ws = Workshops()
    ws.setKeywords(trainingKeywords)
    ws.connectAndGenerateInformation()

    print('*'*20)
    print(f'\nKeywords: {trainingKeywords}\n')
    print(f'Number of matching workshops: {ws.getNumberOfWorkshops()}\n')
    
    print(f'Total Signed Up: {ws.getTotalNumberOfParticipants()}\n')

    for workshop in ws.getWorkshops():
        print(f"{workshop['workshopID']} - {workshop['workshopStartDate']} - {workshop['workshopParticipantNumberInfo']} - {workshop['workshopName']}")
        print(f"\tURL: {workshop['workshopURL']}")
        print('\tParticipants:')
        for participantInfo in workshop['participantInfoList']:
            print(f"\t\t{participantInfo[0]} - {participantInfo[1]}")
        print()

    print()
    print('Emails for this training:')
    print('-'*20)
    print(ws.getEmails())

    print()

if __name__ == '__main__':
    main()