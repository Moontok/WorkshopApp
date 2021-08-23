'''
Helper module for workshopProgramMain.py.
This houses the GuiWindow which is a child class of Ui_MainWindow in workshopGUI.py.
This allows to extend the class with custom functionally and not worry about recreating 
the workshopGUI from QT Designer.
'''

from workshops import Workshops
from PyQt5.QtWidgets import QDialog, QMessageBox, QLineEdit
from login_dialog import Ui_LoginDialog
from workshop_gui import Ui_MainWindow


class GuiWindow(Ui_MainWindow):
    ''' 
    Class extension for Ui_MainWindow so original class can be udpated in QTdesigner.
    Extended functionallity is added here.
    '''

    def setup_ui(self, MainWindow):
        super().setup_ui(MainWindow)
        self.font_size: int = 12
        self.smallest_font_size: int = 8
        self.largest_font_size: int = 52
        self.textOutputField.setReadOnly(True)


    def increase_font(self) -> None:
        '''Increase output font if below size 52.'''

        if self.font_size < self.largest_font_size:
            text: str = self.textOutputField.toPlainText()
            self.font_size += 4
            self.textOutputField.setFontPointSize(self.font_size)
            self.textOutputField.setText(text)
    

    def decrease_font(self) -> None:
        '''Decrease output font if above size 8.'''

        if self.font_size > self.smallest_font_size:
            text: str = self.textOutputField.toPlainText()
            self.font_size -= 4
            self.textOutputField.setFontPointSize(self.font_size)
            self.textOutputField.setText(text)


    def creds_popup_box(self, ws: Workshops) -> None:
        ''' Open a custom dialog box to update username and password.'''

        login_dialog: QDialog = QDialog()
        ui: Ui_LoginDialog = Ui_LoginDialog()
        ui.setupUi(login_dialog)
        ui.inputPassword.setEchoMode(QLineEdit.Password)
        login_dialog.show()
        ok = login_dialog.exec_()        

        if ok and len(ui.inputUsername.text()) > 0 and len(ui.inputPassword.text()) > 0:
            ws.user_name = ui.inputUsername.text()
            ws.user_password = ui.inputPassword.text()
            ws.store_user_info()
            self.change_creds_successful(True)
        else:
            self.change_creds_successful(False)


    def change_creds_successful(self, success: bool) -> None:
        '''Pops-up message if successful update of user information or not.'''

        msg: QMessageBox = QMessageBox()
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
