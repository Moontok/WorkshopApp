''' 
Workshop information gatherer.

This program gathers information about our teams workshops by
gathering the information directly from the website and storing
it into a searchable database.
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

    # Connect buttons and menu items.
    ui.buttonGetWorkshops.clicked.connect(lambda:generateWorkshopInfo(MainWindow, ui, ws))
    ui.actionIncrease_CTRL.triggered.connect(ui.increaseFont)
    ui.actionDecrease_CTRL.triggered.connect(ui.decreaseFont)
    ui.actionUpdate_Credentials.triggered.connect(lambda:ui.credsPopupBox(ws))
    ui.actionUpdate_Database.triggered.connect(lambda:updateDatabase(MainWindow, ws, ui))    

    MainWindow.show()

    updateDatabase(MainWindow, ws, ui) # Update database when app first launches.

    sys.exit(app.exec_())
    

def generateWorkshopInfo(MainWindow, ui, ws):
    '''Output the desired content based on a phrase.'''    

    ui.textOutputField.clear()    
    ws.setPhrase(ui.lineEditPhrase.text())
    
    if ui.lineEditWorkshopID.text() != '':
        workshops = ws.getMatchingWorkshops(searchWorkshopID=ui.lineEditWorkshopID.text())
    elif ui.checkBoxUseDate.isChecked():
        workshops = ws.getMatchingWorkshops(startDate=ui.calendarWidget_StartDate.selectedDate().getDate(),
                                            endDate=ui.calendarWidget_EndDate.selectedDate().getDate())
    else:
        workshops = ws.getMatchingWorkshops()

    displayText = []
    displayText.append(f'Number of matching workshops: {ws.getNumberOfWorkshops()}\n\n')
    displayText.append(f'Total Signed Up: {ws.getNumberOfParticipants()}\n\n')

    if buttonsChecked(ui):
        displayText = setupWorkshopInformation(ui, displayText, workshops)

    displayText.append(f'All emails for these workshops:\n\n{ws.getEmails(workshops)}')
    ui.textOutputField.clear()
    ui.textOutputField.insertPlainText(''.join(displayText))


def buttonsChecked(ui):
    ''' Return true if any button is checked. '''

    return ui.checkBoxWsID.isChecked() or ui.checkBoxWsStartDate.isChecked() or ui.checkBoxWsPartNumbers.isChecked() or ui.checkBoxWsName.isChecked() or ui.checkBoxWsURL.isChecked()

def setupWorkshopInformation(ui, displayText, workshops):
    '''
    Prepare the output of the workshops based on selected information.

    Useful information when using:
    Workshop Structure: [id, workshopID, workshopName, workshopStartDateAndTime, workshopSignedUp, workshopParticipantCapacity, workshopURL, [participantInfoList]]
    participantInfoList [name, email, school]
    '''

    for workshop in workshops:
        text = []
        if ui.checkBoxWsID.isChecked():
            text.append(f"{workshop[1]}") # workshopID
        if ui.checkBoxWsStartDate.isChecked():
            text.append(f"{workshop[3]}") # workshopStartDate
        if ui.checkBoxWsPartNumbers.isChecked():
            text.append(f"{workshop[4]}/{workshop[5]}") # workshopSignedUp/workshopParticipantCapacity
        if ui.checkBoxWsName.isChecked():
            text.append(f"{workshop[2]}") # workshopName
        if ui.checkBoxWsURL.isChecked():
            text.append(f"\n   Url: {workshop[6]}") # workshopURL

        displayText.append(" - ".join(text))            
        displayText.append('\n')

        if ui.checkBoxNames.isChecked() or ui.checkBoxEmails.isChecked() or ui.checkBoxSchools.isChecked():

            displayText.append('   Contact Information:\n')
        
            for participantInfo in workshop[7]: # participantInfoList
                text = []
                if ui.checkBoxNames.isChecked():
                    text.append(f"{participantInfo[0]}")
                if ui.checkBoxEmails.isChecked():
                    text.append(f"{participantInfo[1]}")
                if ui.checkBoxSchools.isChecked():
                    text.append(f"{participantInfo[2]}")
                displayText.append('    + ')
                displayText.append(' - '.join(text))
                displayText.append('\n')
        
        displayText.append('\n')

    return displayText

def updateDatabase(MainWindow, ws, ui):
    ''' Attempts to handle connecting to the website and database. '''

    ui.textOutputField.clear()

    try:
        ws.connectAndUpdateDatabase()    
        ui.textOutputField.insertPlainText(welcomeText())
    except ConnectionError:
        ui.textOutputField.insertPlainText(welcomeTextOffline())
    except TypeError:
        ui.textOutputField.insertPlainText('Something went wrong when connecting to server...\nTry again later.')
    except FileNotFoundError:
        ui.textOutputField.insertPlainText('Please enter your login credentials.')
    
    MainWindow.repaint()
    

def welcomeText():
    '''Text that first appears in output window.'''

    text = [
        'Welcome!',
        '',
        'This program will allow you to seach current workshops using a phrase.',
        'Type a phrase that you would like to search in the "Phrase:" field.',
        'The phrase does not have to be case sensative.',
        'Leave the "Phrase:" field blank to get all current workshops.']

    return '\n'.join(text)

def welcomeTextOffline():
    '''Text that first appears in output window.'''

    text = [
        'Cannot connect to server...',
        'You are in offline mode.',
        'You can access workshops from the last time your last successful connection.',
        'You can try to update your database when you have established an internet connection.']

    return '\n'.join(text)


if __name__ == '__main__':
    main()
