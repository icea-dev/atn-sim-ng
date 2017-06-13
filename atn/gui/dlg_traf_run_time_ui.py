# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dlg_traf_run_time.ui'
#
# Created: Fri May 26 10:41:24 2017
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

class Ui_dlg_traf_run_time(object):
    def setupUi(self, dlg_traf_run_time):
        dlg_traf_run_time.setObjectName(_fromUtf8("dlg_traf_run_time"))
        dlg_traf_run_time.resize(804, 173)
        self.verticalLayout_2 = QtGui.QVBoxLayout(dlg_traf_run_time)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.gbx_aircraft = QtGui.QGroupBox(dlg_traf_run_time)
        self.gbx_aircraft.setObjectName(_fromUtf8("gbx_aircraft"))
        self.verticalLayout = QtGui.QVBoxLayout(self.gbx_aircraft)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.qtw_traf = QtGui.QTableWidget(self.gbx_aircraft)
        self.qtw_traf.setRowCount(1)
        self.qtw_traf.setColumnCount(11)
        self.qtw_traf.setObjectName(_fromUtf8("qtw_traf"))
        item = QtGui.QTableWidgetItem()
        self.qtw_traf.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.qtw_traf.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.qtw_traf.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.qtw_traf.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.qtw_traf.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.qtw_traf.setHorizontalHeaderItem(5, item)
        item = QtGui.QTableWidgetItem()
        self.qtw_traf.setHorizontalHeaderItem(6, item)
        item = QtGui.QTableWidgetItem()
        self.qtw_traf.setHorizontalHeaderItem(7, item)
        item = QtGui.QTableWidgetItem()
        self.qtw_traf.setHorizontalHeaderItem(8, item)
        item = QtGui.QTableWidgetItem()
        self.qtw_traf.setHorizontalHeaderItem(9, item)
        item = QtGui.QTableWidgetItem()
        self.qtw_traf.setHorizontalHeaderItem(10, item)
        self.qtw_traf.horizontalHeader().setDefaultSectionSize(106)
        self.qtw_traf.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.qtw_traf)
        self.verticalLayout_2.addWidget(self.gbx_aircraft)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.btn_cancel = QtGui.QPushButton(dlg_traf_run_time)
        self.btn_cancel.setObjectName(_fromUtf8("btn_cancel"))
        self.horizontalLayout_2.addWidget(self.btn_cancel)
        self.btn_create = QtGui.QPushButton(dlg_traf_run_time)
        self.btn_create.setObjectName(_fromUtf8("btn_create"))
        self.horizontalLayout_2.addWidget(self.btn_create)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.retranslateUi(dlg_traf_run_time)
        QtCore.QMetaObject.connectSlotsByName(dlg_traf_run_time)

    def retranslateUi(self, dlg_traf_run_time):
        dlg_traf_run_time.setWindowTitle(_translate("dlg_traf_run_time", "Create aircraft at runtime:", None))
        self.gbx_aircraft.setTitle(_translate("dlg_traf_run_time", "Aircraft", None))
        item = self.qtw_traf.horizontalHeaderItem(0)
        item.setText(_translate("dlg_traf_run_time", "Latitude", None))
        item = self.qtw_traf.horizontalHeaderItem(1)
        item.setText(_translate("dlg_traf_run_time", "Longitude", None))
        item = self.qtw_traf.horizontalHeaderItem(2)
        item.setText(_translate("dlg_traf_run_time", "Type of Acft", None))
        item = self.qtw_traf.horizontalHeaderItem(3)
        item.setText(_translate("dlg_traf_run_time", "SSR", None))
        item = self.qtw_traf.horizontalHeaderItem(4)
        item.setText(_translate("dlg_traf_run_time", "Callsign", None))
        item = self.qtw_traf.horizontalHeaderItem(5)
        item.setText(_translate("dlg_traf_run_time", "Departure", None))
        item = self.qtw_traf.horizontalHeaderItem(6)
        item.setText(_translate("dlg_traf_run_time", "Arrival", None))
        item = self.qtw_traf.horizontalHeaderItem(7)
        item.setText(_translate("dlg_traf_run_time", "Heading", None))
        item = self.qtw_traf.horizontalHeaderItem(8)
        item.setText(_translate("dlg_traf_run_time", "Speed", None))
        item = self.qtw_traf.horizontalHeaderItem(9)
        item.setText(_translate("dlg_traf_run_time", "Altitude", None))
        item = self.qtw_traf.horizontalHeaderItem(10)
        item.setText(_translate("dlg_traf_run_time", "Procedure", None))
        self.btn_cancel.setText(_translate("dlg_traf_run_time", "Cancel", None))
        self.btn_create.setText(_translate("dlg_traf_run_time", "Create", None))

