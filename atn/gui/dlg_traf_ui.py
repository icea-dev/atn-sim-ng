# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dlg_traf.ui'
#
# Created: Thu Apr  6 11:31:12 2017
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

class Ui_dlg_trf(object):
    def setupUi(self, dlg_trf):
        dlg_trf.setObjectName(_fromUtf8("dlg_trf"))
        dlg_trf.resize(578, 300)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(dlg_trf.sizePolicy().hasHeightForWidth())
        dlg_trf.setSizePolicy(sizePolicy)
        self.verticalLayout = QtGui.QVBoxLayout(dlg_trf)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gbx_tbl = QtGui.QGroupBox(dlg_trf)
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
        self.btn_cancel = QtGui.QPushButton(dlg_trf)
        self.btn_cancel.setObjectName(_fromUtf8("btn_cancel"))
        self.horizontalLayout.addWidget(self.btn_cancel)
        self.btn_create = QtGui.QPushButton(dlg_trf)
        self.btn_create.setObjectName(_fromUtf8("btn_create"))
        self.horizontalLayout.addWidget(self.btn_create)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(dlg_trf)
        QtCore.QMetaObject.connectSlotsByName(dlg_trf)

    def retranslateUi(self, dlg_trf):
        dlg_trf.setWindowTitle(_translate("dlg_trf", "Scenario aircrafts:", None))
        self.gbx_tbl.setTitle(_translate("dlg_trf", "Aircrafts", None))
        self.btn_cancel.setText(_translate("dlg_trf", "Cancel", None))
        self.btn_create.setText(_translate("dlg_trf", "Create aircrafts", None))

