from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore

class SplashScreen():
    ''' Class for creating a splash screen to be displayed while the program is loading.'''

    def __init__(self):
        self.splash: QLabel = QLabel()
        self.splash.setText('Updating Database. This will take a moment...')
        self.splash.setStyleSheet('padding:15px; font:30pt')
        self.splash.show()

        loop: QtCore.QEventLoop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(100, loop.quit)
        loop.exec_()


    def close(self) -> None:
        self.splash.close()

if __name__ == '__main__':
    print('This is a module...')