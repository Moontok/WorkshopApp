# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'LoginPopup.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LoginDialog(object):
    def setupUi(self, LoginDialog):
        LoginDialog.setObjectName("LoginDialog")
        LoginDialog.resize(382, 161)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(LoginDialog.sizePolicy().hasHeightForWidth())
        LoginDialog.setSizePolicy(sizePolicy)
        LoginDialog.setMinimumSize(QtCore.QSize(382, 161))
        LoginDialog.setMaximumSize(QtCore.QSize(382, 161))
        self.widget = QtWidgets.QWidget(LoginDialog)
        self.widget.setGeometry(QtCore.QRect(10, 10, 361, 140))
        self.widget.setObjectName("widget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.labelInfo = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.labelInfo.setFont(font)
        self.labelInfo.setScaledContents(False)
        self.labelInfo.setAlignment(QtCore.Qt.AlignCenter)
        self.labelInfo.setObjectName("labelInfo")
        self.verticalLayout.addWidget(self.labelInfo)
        self.frameSpacer1 = QtWidgets.QFrame(self.widget)
        self.frameSpacer1.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameSpacer1.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameSpacer1.setObjectName("frameSpacer1")
        self.verticalLayout.addWidget(self.frameSpacer1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labelUsername = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.labelUsername.setFont(font)
        self.labelUsername.setObjectName("labelUsername")
        self.horizontalLayout.addWidget(self.labelUsername)
        self.inputUsername = QtWidgets.QLineEdit(self.widget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.inputUsername.setFont(font)
        self.inputUsername.setObjectName("inputUsername")
        self.horizontalLayout.addWidget(self.inputUsername)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.frameSpacer2 = QtWidgets.QFrame(self.widget)
        self.frameSpacer2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameSpacer2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameSpacer2.setObjectName("frameSpacer2")
        self.verticalLayout.addWidget(self.frameSpacer2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.labelPassword = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.labelPassword.setFont(font)
        self.labelPassword.setObjectName("labelPassword")
        self.horizontalLayout_2.addWidget(self.labelPassword)
        self.inputPassword = QtWidgets.QLineEdit(self.widget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.inputPassword.setFont(font)
        self.inputPassword.setObjectName("inputPassword")
        self.horizontalLayout_2.addWidget(self.inputPassword)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.widget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_3.addWidget(self.buttonBox)

        self.retranslateUi(LoginDialog)
        self.buttonBox.accepted.connect(LoginDialog.accept)
        self.buttonBox.rejected.connect(LoginDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(LoginDialog)

    def retranslateUi(self, LoginDialog):
        _translate = QtCore.QCoreApplication.translate
        LoginDialog.setWindowTitle(_translate("LoginDialog", "Dialog"))
        self.labelInfo.setText(_translate("LoginDialog", "Please enter your login credentials."))
        self.labelUsername.setText(_translate("LoginDialog", "Username: "))
        self.labelPassword.setText(_translate("LoginDialog", "Password:  "))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    LoginDialog = QtWidgets.QDialog()
    ui = Ui_LoginDialog()
    ui.setupUi(LoginDialog)
    LoginDialog.show()
    sys.exit(app.exec_())
