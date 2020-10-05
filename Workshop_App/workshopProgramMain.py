''' 
Workshop information gatherer.

This program gathers information about our teams workshops by
gathering the information directly from the website.
'''

import sys
from requests.exceptions import ConnectionError
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from workshops import Workshops
from guiWindow import GuiWindow

def main():
    '''Main'''

    ws = Workshops()

    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = GuiWindow()
    ui.setupUi(MainWindow)
    
    ui.textOutputField.insertPlainText(welcomeText())

    # Connect buttons and menu items.
    ui.buttonGetWorkshops.clicked.connect(lambda:generateWorkshopInfo(MainWindow, ui, ws))
    ui.actionIncrease_CTRL.triggered.connect(ui.increaseFont)
    ui.actionDecrease_CTRL.triggered.connect(ui.decreaseFont)
    ui.actionUpdate_Credentials.triggered.connect(lambda:ui.credsPopupBox(ws))

    MainWindow.show()
    sys.exit(app.exec_())

def generateWorkshopInfo(MainWindow, ui, ws):
    '''Output the desired content based on a phrase.'''

    ui.textOutputField.clear()
    
    ui.textOutputField.insertPlainText('Collecting all workshop information...')
    MainWindow.repaint() # Repaint Window to show text above.
    ws.setPhrase(ui.phraseInputField.text())

    try:
        ws.connectAndCollectInformation()
    except ConnectionError:
        ui.textOutputField.insertPlainText('Cannot connect to server...\nCheck internet connection.')
        return
    except TypeError:
        ui.textOutputField.insertPlainText('Something went wrong when connecting to server...\nTry again later.')
        return
    except FileNotFoundError:
        ui.textOutputField.insertPlainText('Please enter your login credentials.')
        return

    displayText = []
    displayText.append(f'\nNumber of matching workshops: {ws.getNumberOfWorkshops()}\n\n')
    displayText.append(f'Total Signed Up: {ws.getTotalNumberOfParticipants()}\n\n')

    # Useful information when using:
    # workshops keys:'workshopID', 'workshopName', 'workshopStartDate', 'workshopParticipantNumberInfo', 'workshopURL', 'participantInfoList'
    # participantInfoList [name, email, school]

    if buttonsChecked(ui):
        for workshop in ws.getWorkshops():
            text = []
            if ui.radioWsID.isChecked():
                text.append(f"{workshop['workshopID']}")
            if ui.radioWsStartDate.isChecked():
                text.append(f"{workshop['workshopStartDate']}")
            if ui.radioPartNumbers.isChecked():
                text.append(f"{workshop['workshopParticipantNumberInfo']}")
            if ui.radioWsName.isChecked():
                text.append(f"{workshop['workshopName']}")
            if ui.radioWsURLs.isChecked():
                text.append(f"\n   Url: {workshop['workshopURL']}")

            displayText.append(" - ".join(text))            
            displayText.append('\n')

            if ui.radioNames.isChecked() or ui.radioEmails.isChecked() or ui.radioSchool.isChecked():

                displayText.append('   Contact Information:\n')
            
                for participantInfo in workshop['participantInfoList']:
                    text = []
                    if ui.radioNames.isChecked():
                        text.append(f"{participantInfo[0]}")
                    if ui.radioEmails.isChecked():
                        text.append(f"{participantInfo[1]}")
                    if ui.radioSchool.isChecked():
                        text.append(f"{participantInfo[2]}")
                    displayText.append('    + ')
                    displayText.append(' - '.join(text))
                    displayText.append('\n')
            
            displayText.append('\n')
    
    displayText.append(f'All emails for these workshops:\n\n{ws.getEmails()}')
    ui.textOutputField.clear()
    ui.textOutputField.insertPlainText(''.join(displayText))


def welcomeText():
    '''Text that first appears in output window.'''

    text = [
        'Welcome!',
        '',
        'This program will allow you to seach current workshops using a phrase.',
        'Type a phrase that you would like to search in the "Search Phrase:" field.',
        'The phrase does not have to be case sensative.',
        'Leave the "Search Phrase:" field blank to get all current workshops.']

    return '\n'.join(text)


def buttonsChecked(ui):
    ''' Return true if any button is checked. '''

    return ui.radioWsID.isChecked() or ui.radioWsStartDate.isChecked() or ui.radioPartNumbers.isChecked() or ui.radioWsName.isChecked() or ui.radioWsURLs.isChecked()

if __name__ == '__main__':
    main()
