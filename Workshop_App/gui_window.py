'''
Helper module for workshopProgramMain.py.
This houses the GuiWindow which is a child class of Ui_MainWindow in workshopGUI.py.
This allows to extend the class with custom functionally and not worry about recreating 
the workshopGUI from QT Designer.
'''

from google_filename_dialog import Ui_GoogleFilenameDialog
from workshop_tool import WorkshopsTool
from PyQt5.QtWidgets import QDialog, QMessageBox, QLineEdit, QMainWindow
from login_dialog import Ui_LoginDialog
from workshop_gui import Ui_MainWindow
from typing import Optional


class GuiWindow(Ui_MainWindow):
    ''' 
    Class extension for Ui_MainWindow so original class can be udpated in QTdesigner.
    Extended functionallity is added here.
    '''

    def setup_ui(self, main_window: QMainWindow) -> None:
        super().setupUi(main_window)
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


    def creds_popup_box(self, ws: WorkshopsTool) -> None:
        '''Open a custom dialog box to update username and password.'''

        login_dialog = QDialog()
        ui = Ui_LoginDialog()
        ui.setupUi(login_dialog)
        ui.inputPassword.setEchoMode(QLineEdit.Password)
        login_dialog.show()
        ok: bool = login_dialog.exec_()        

        if ok and len(ui.inputUsername.text()) > 0 and len(ui.inputPassword.text()) > 0:
            user_name: str = ui.inputUsername.text()
            user_password: str = ui.inputPassword.text()
            ws.connector.store_user_info(user_name, user_password)
            self.change_creds_successful(True)
        else:
            self.change_creds_successful(False)


    def google_filename_popup_box(self) -> Optional[tuple]:
        '''Open a custom dialog box to export googlesheet to a folder.'''

        google_filename_dialog = QDialog()
        ui = Ui_GoogleFilenameDialog()
        ui.setupUi(google_filename_dialog)
        google_filename_dialog.show()
        ok: bool = google_filename_dialog.exec_()        
        
        if ok and len(ui.filename_edit.text()) > 0 and len(ui.folder_id_edit.text()) > 0:
            filename: str = ui.filename_edit.text()
            folder_url: str = ui.folder_id_edit.text()
            folder_id: str = self.strip_folder_id(folder_url)
            self.export_googlesheet_successful(True)
            return (filename, folder_id)
        else:
            self.export_googlesheet_successful(False)
            return None


    def strip_folder_id(self, url: str) -> str:
        """Returns teh folder ID"""

        return url.split("folders/")[1]


    def change_creds_successful(self, success: bool) -> None:
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


    def export_googlesheet_successful(self, success: bool) -> None:
        '''Pops-up message if successful filename and folder provided.'''

        msg = QMessageBox()
        msg.setWindowTitle('Results')

        if success:
            msg.setText('Your file is being created!')
            msg.setIcon(QMessageBox.Information)
        else:
            msg.setText('Your file has not been created!')
            msg.setIcon(QMessageBox.Critical)

        msg.exec_()


if __name__ == '__main__':
    print('This is a module...')
