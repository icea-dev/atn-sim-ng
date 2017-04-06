# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dlg_start.ui'
#
# Created: Thu Apr  6 11:31:13 2017
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_dlg_start(object):
    def setupUi(self, dlg_start):
        dlg_start.setObjectName(_fromUtf8("dlg_start"))
        dlg_start.resize(627, 253)
        self.verticalLayout_2 = QtGui.QVBoxLayout(dlg_start)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.lbl_text = QtGui.QLabel(dlg_start)
        self.lbl_text.setObjectName(_fromUtf8("lbl_text"))
        self.verticalLayout_2.addWidget(self.lbl_text)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.btn_upgrade = QtGui.QPushButton(dlg_start)
        self.btn_upgrade.setObjectName(_fromUtf8("btn_upgrade"))
        self.verticalLayout.addWidget(self.btn_upgrade)
        self.btn_run = QtGui.QPushButton(dlg_start)
        self.btn_run.setObjectName(_fromUtf8("btn_run"))
        self.verticalLayout.addWidget(self.btn_run)
        self.btn_cancel = QtGui.QPushButton(dlg_start)
        self.btn_cancel.setObjectName(_fromUtf8("btn_cancel"))
        self.verticalLayout.addWidget(self.btn_cancel)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(dlg_start)
        QtCore.QMetaObject.connectSlotsByName(dlg_start)

    def retranslateUi(self, dlg_start):
        dlg_start.setWindowTitle(_translate("dlg_start", "Start Simulation", None))
        self.lbl_text.setText(_translate("dlg_start", "<html><head/><body><p align=\"center\"><span style=\" font-size:16pt; color:#ff0000;\">The aircraft in the simulation scenario may have changed.</span></p><p align=\"center\"><span style=\" font-size:16pt; color:#ff0000;\">What do you want to do ?</span></p></body></html>", None))
        self.btn_upgrade.setText(_translate("dlg_start", "Upgrade the aircraft of the scenario", None))
        self.btn_run.setText(_translate("dlg_start", "Run the simulation without changing the aircraft", None))
        self.btn_cancel.setText(_translate("dlg_start", "Cancel the ATN simulation", None))

