'''
Helper module for workshopProgramMain.py.
This houses the GuiWindow which is a child class of Ui_MainWindow in workshopGUI.py.
This allows to extend the class with custom functionally and not worry about recreating 
the workshopGUI from QT Designer.
'''

from PyQt5.QtWidgets import QDialog, QMessageBox, QLineEdit
from loginDialog import Ui_LoginDialog
from workshopGUI import Ui_MainWindow


class GuiWindow(Ui_MainWindow):
    '''
    Class extension for Ui_MainWindow so original class can be udpated in QTdesigner.
    Extended functionallity is added here.
    '''

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.fontSize = 12
        self.smallestFontSize = 8
        self.largestFontSize = 52
        self.textOutputField.setReadOnly(True)

    def increaseFont(self):
        '''Increase output font if below size 52.'''

        if self.fontSize < self.largestFontSize:
            text = self.textOutputField.toPlainText()
            self.fontSize += 4
            self.textOutputField.setFontPointSize(self.fontSize)
            self.textOutputField.setText(text)

    
    def decreaseFont(self):
        '''Decrease output font if above size 8.'''

        if self.fontSize > self.smallestFontSize:
            text = self.textOutputField.toPlainText()
            self.fontSize -= 4
            self.textOutputField.setFontPointSize(self.fontSize)
            self.textOutputField.setText(text)


    def credsPopupBox(self, ws):
        ''' Open a custom dialog box to update username and password.'''

        LoginDialog = QDialog()
        ui = Ui_LoginDialog()
        ui.setupUi(LoginDialog)
        ui.inputPassword.setEchoMode(QLineEdit.Password)
        LoginDialog.show()
        ok = LoginDialog.exec_()
        

        if ok and len(ui.inputUsername.text()) > 0 and len(ui.inputPassword.text()) > 0:
            ws.userName = ui.inputUsername.text()
            ws.userPassword = ui.inputPassword.text()
            ws.storeUserInfo()
            self.changeCredsSuccessful(True)
        else:
            self.changeCredsSuccessful(False)


    def changeCredsSuccessful(self, success):
        '''Pops-up message if successful update of user information or not.'''

        msg = QMessageBox()
        msg.setWindowTitle('Results')

        if success:
            msg.setText('Your credentials have been updated!')
            msg.setIcon(QMessageBox.Information)
        else:
            msg.setText('Your credentials have NOT been updated!')
            msg.setIcon(QMessageBox.Critical)

        msg.exec_()


if __name__ == '__main__':
    print('This is a module...')
