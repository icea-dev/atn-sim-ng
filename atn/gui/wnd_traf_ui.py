# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'wnd_traf.ui'
#
# Created: Mon Apr  3 16:01:04 2017
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

class Ui_frm_trf(object):
    def setupUi(self, frm_trf):
        frm_trf.setObjectName(_fromUtf8("frm_trf"))
        frm_trf.resize(585, 236)
        self.verticalLayout = QtGui.QVBoxLayout(frm_trf)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gbx_tbl = QtGui.QGroupBox(frm_trf)
        self.gbx_tbl.setObjectName(_fromUtf8("gbx_tbl"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.gbx_tbl)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.qtw_trf = QtGui.QTableWidget(self.gbx_tbl)
        self.qtw_trf.setObjectName(_fromUtf8("qtw_trf"))
        self.qtw_trf.setColumnCount(0)
        self.qtw_trf.setRowCount(0)
        self.verticalLayout_2.addWidget(self.qtw_trf)
        self.verticalLayout.addWidget(self.gbx_tbl)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btn_cancel = QtGui.QPushButton(frm_trf)
        self.btn_cancel.setObjectName(_fromUtf8("btn_cancel"))
        self.horizontalLayout.addWidget(self.btn_cancel)
        self.btn_create = QtGui.QPushButton(frm_trf)
        self.btn_create.setObjectName(_fromUtf8("btn_create"))
        self.horizontalLayout.addWidget(self.btn_create)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(frm_trf)
        QtCore.QMetaObject.connectSlotsByName(frm_trf)

    def retranslateUi(self, frm_trf):
        frm_trf.setWindowTitle(_translate("frm_trf", "Scenario aircrafts: ", None))
        self.gbx_tbl.setTitle(_translate("frm_trf", "Aircrafts", None))
        self.btn_cancel.setText(_translate("frm_trf", "Cancel", None))
        self.btn_create.setText(_translate("frm_trf", "Create aircrafts", None))

