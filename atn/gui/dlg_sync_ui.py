# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dlg_sync.ui'
#
# Created: Mon Jul 10 15:38:29 2017
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

class Ui_dlg_sync(object):
    def setupUi(self, dlg_sync):
        dlg_sync.setObjectName(_fromUtf8("dlg_sync"))
        dlg_sync.resize(400, 300)
        self.horizontalLayout = QtGui.QHBoxLayout(dlg_sync)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.qtwTabFiles = QtGui.QTableWidget(dlg_sync)
        self.qtwTabFiles.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.qtwTabFiles.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.qtwTabFiles.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.qtwTabFiles.setObjectName(_fromUtf8("qtwTabFiles"))
        self.qtwTabFiles.setColumnCount(2)
        self.qtwTabFiles.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.qtwTabFiles.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.qtwTabFiles.setHorizontalHeaderItem(1, item)
        self.horizontalLayout.addWidget(self.qtwTabFiles)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.btnNew = QtGui.QPushButton(dlg_sync)
        self.btnNew.setObjectName(_fromUtf8("btnNew"))
        self.verticalLayout.addWidget(self.btnNew)
        self.btnUpdate = QtGui.QPushButton(dlg_sync)
        self.btnUpdate.setObjectName(_fromUtf8("btnUpdate"))
        self.verticalLayout.addWidget(self.btnUpdate)
        self.btnCancel = QtGui.QPushButton(dlg_sync)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.verticalLayout.addWidget(self.btnCancel)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(dlg_sync)
        QtCore.QMetaObject.connectSlotsByName(dlg_sync)

    def retranslateUi(self, dlg_sync):
        dlg_sync.setWindowTitle(_translate("dlg_sync", "Sync CORE - Track Generator", None))
        item = self.qtwTabFiles.horizontalHeaderItem(0)
        item.setText(_translate("dlg_sync", "CORE", None))
        item = self.qtwTabFiles.horizontalHeaderItem(1)
        item.setText(_translate("dlg_sync", "Track Generator", None))
        self.btnNew.setText(_translate("dlg_sync", "New", None))
        self.btnUpdate.setText(_translate("dlg_sync", "Update", None))
        self.btnCancel.setText(_translate("dlg_sync", "Cancel", None))

