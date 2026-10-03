# -*- coding: utf-8 -*-
#
# 本文件由 Qt Designer 的 .ui 文件经 pyside6-uic 转换而来；原始 .ui 的来源与署名见
# LICENSE / AUTHORS.md。本项目对转换结果所做的修改：
# Copyright (c) 2026 bakeryg  —  SPDX-License-Identifier: MIT
# 项目地址: https://github.com/bakeryg/ArchivePasswordCracker
#
################################################################################
## Form generated from reading UI file 'MainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QDial, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QLCDNumber,
    QLabel, QLineEdit, QMainWindow, QProgressBar,
    QPushButton, QSizePolicy, QSlider, QSpacerItem,
    QSpinBox, QStatusBar, QTabWidget, QToolButton,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(662, 568)
        icon = QIcon()
        icon.addFile(u"icon.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setLayoutDirection(Qt.LeftToRight)
        MainWindow.setUnifiedTitleAndToolBarOnMac(True)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.dict_source = QTabWidget(self.centralwidget)
        self.dict_source.setObjectName(u"dict_source")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dict_source.sizePolicy().hasHeightForWidth())
        self.dict_source.setSizePolicy(sizePolicy)
        self.dict_source.setMaximumSize(QSize(16777215, 16777215))
        self.internal_dict = QWidget()
        self.internal_dict.setObjectName(u"internal_dict")
        self.verticalLayout_2 = QVBoxLayout(self.internal_dict)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.check_boxes = QHBoxLayout()
        self.check_boxes.setObjectName(u"check_boxes")
        self.checkBox_num = QCheckBox(self.internal_dict)
        self.checkBox_num.setObjectName(u"checkBox_num")
        self.checkBox_num.setChecked(True)

        self.check_boxes.addWidget(self.checkBox_num)

        self.checkBox_lower_letter = QCheckBox(self.internal_dict)
        self.checkBox_lower_letter.setObjectName(u"checkBox_lower_letter")

        self.check_boxes.addWidget(self.checkBox_lower_letter)

        self.checkBox_upper_letter = QCheckBox(self.internal_dict)
        self.checkBox_upper_letter.setObjectName(u"checkBox_upper_letter")

        self.check_boxes.addWidget(self.checkBox_upper_letter)

        self.checkBox_symbols = QCheckBox(self.internal_dict)
        self.checkBox_symbols.setObjectName(u"checkBox_symbols")

        self.check_boxes.addWidget(self.checkBox_symbols)


        self.verticalLayout_2.addLayout(self.check_boxes)

        self.digits_boxes = QHBoxLayout()
        self.digits_boxes.setObjectName(u"digits_boxes")
        self.digit_min = QSpinBox(self.internal_dict)
        self.digit_min.setObjectName(u"digit_min")
        self.digit_min.setMinimum(1)
        self.digit_min.setMaximum(8)

        self.digits_boxes.addWidget(self.digit_min)

        self.label_8 = QLabel(self.internal_dict)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setMaximumSize(QSize(16777215, 40))

        self.digits_boxes.addWidget(self.label_8, 0, Qt.AlignHCenter)

        self.digit_max = QSpinBox(self.internal_dict)
        self.digit_max.setObjectName(u"digit_max")
        self.digit_max.setMinimum(1)
        self.digit_max.setMaximum(8)

        self.digits_boxes.addWidget(self.digit_max)


        self.verticalLayout_2.addLayout(self.digits_boxes)

        self.export_boxes = QHBoxLayout()
        self.export_boxes.setObjectName(u"export_boxes")
        self.button_export = QPushButton(self.internal_dict)
        self.button_export.setObjectName(u"button_export")
        self.button_export.setMaximumSize(QSize(167, 16777215))

        self.export_boxes.addWidget(self.button_export)

        self.progress_export = QProgressBar(self.internal_dict)
        self.progress_export.setObjectName(u"progress_export")
        self.progress_export.setValue(0)

        self.export_boxes.addWidget(self.progress_export)

        self.export_path = QLineEdit(self.internal_dict)
        self.export_path.setObjectName(u"export_path")

        self.export_boxes.addWidget(self.export_path)

        self.button_export_path = QToolButton(self.internal_dict)
        self.button_export_path.setObjectName(u"button_export_path")

        self.export_boxes.addWidget(self.button_export_path)


        self.verticalLayout_2.addLayout(self.export_boxes)

        self.dict_source.addTab(self.internal_dict, "")
        self.external_dict = QWidget()
        self.external_dict.setObjectName(u"external_dict")
        self.gridLayout = QGridLayout(self.external_dict)
        self.gridLayout.setObjectName(u"gridLayout")
        self.dict_path = QLineEdit(self.external_dict)
        self.dict_path.setObjectName(u"dict_path")

        self.gridLayout.addWidget(self.dict_path, 0, 1, 1, 1)

        self.label_5 = QLabel(self.external_dict)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 0, 0, 1, 1)

        self.button_dict_path = QToolButton(self.external_dict)
        self.button_dict_path.setObjectName(u"button_dict_path")

        self.gridLayout.addWidget(self.button_dict_path, 0, 2, 1, 1)

        self.dict_source.addTab(self.external_dict, "")

        self.gridLayout_2.addWidget(self.dict_source, 1, 0, 1, 1)

        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy1)
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_6 = QLabel(self.groupBox_2)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_2.addWidget(self.label_6)

        self.core_num = QLCDNumber(self.groupBox_2)
        self.core_num.setObjectName(u"core_num")
        self.core_num.setAutoFillBackground(True)
        self.core_num.setFrameShape(QFrame.Box)
        self.core_num.setFrameShadow(QFrame.Raised)
        self.core_num.setSegmentStyle(QLCDNumber.Filled)
        self.core_num.setProperty(u"value", 1.000000000000000)

        self.horizontalLayout_2.addWidget(self.core_num)

        self.cpu_slider = QSlider(self.groupBox_2)
        self.cpu_slider.setObjectName(u"cpu_slider")
        self.cpu_slider.setMinimum(1)
        self.cpu_slider.setOrientation(Qt.Horizontal)

        self.horizontalLayout_2.addWidget(self.cpu_slider)

        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.batch_size = QLCDNumber(self.groupBox_2)
        self.batch_size.setObjectName(u"batch_size")
        self.batch_size.setProperty(u"intValue", 20000)

        self.horizontalLayout_2.addWidget(self.batch_size)

        self.dial = QDial(self.groupBox_2)
        self.dial.setObjectName(u"dial")
        self.dial.setMinimum(1)
        self.dial.setMaximum(20000)
        self.dial.setValue(20000)
        self.dial.setWrapping(False)
        self.dial.setNotchTarget(3.700000000000000)
        self.dial.setNotchesVisible(True)

        self.horizontalLayout_2.addWidget(self.dial)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)


        self.gridLayout_2.addWidget(self.groupBox_2, 0, 0, 1, 1)

        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_6.addWidget(self.label_2)

        self.zipfile_path = QLineEdit(self.groupBox)
        self.zipfile_path.setObjectName(u"zipfile_path")

        self.horizontalLayout_6.addWidget(self.zipfile_path)

        self.button_zipfile_path = QToolButton(self.groupBox)
        self.button_zipfile_path.setObjectName(u"button_zipfile_path")

        self.horizontalLayout_6.addWidget(self.button_zipfile_path)


        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_4.addWidget(self.label_3)

        self.extract_path = QLineEdit(self.groupBox)
        self.extract_path.setObjectName(u"extract_path")

        self.horizontalLayout_4.addWidget(self.extract_path)

        self.button_extract_path = QToolButton(self.groupBox)
        self.button_extract_path.setObjectName(u"button_extract_path")

        self.horizontalLayout_4.addWidget(self.button_extract_path)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.button_crack = QPushButton(self.groupBox)
        self.button_crack.setObjectName(u"button_crack")

        self.horizontalLayout_7.addWidget(self.button_crack, 0, Qt.AlignLeft)

        self.progress_crack = QProgressBar(self.groupBox)
        self.progress_crack.setObjectName(u"progress_crack")
        self.progress_crack.setValue(0)

        self.horizontalLayout_7.addWidget(self.progress_crack)

        self.label_password_is = QLabel(self.groupBox)
        self.label_password_is.setObjectName(u"label_password_is")

        self.horizontalLayout_7.addWidget(self.label_password_is, 0, Qt.AlignLeft)

        self.password = QLineEdit(self.groupBox)
        self.password.setObjectName(u"password")
        self.password.setReadOnly(True)

        self.horizontalLayout_7.addWidget(self.password)


        self.verticalLayout.addLayout(self.horizontalLayout_7)


        self.gridLayout_2.addWidget(self.groupBox, 3, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.button_about = QPushButton(self.centralwidget)
        self.button_about.setObjectName(u"button_about")

        self.horizontalLayout.addWidget(self.button_about)

        self.button_close = QPushButton(self.centralwidget)
        self.button_close.setObjectName(u"button_close")

        self.horizontalLayout.addWidget(self.button_close)


        self.gridLayout_2.addLayout(self.horizontalLayout, 4, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.cpu_slider.valueChanged.connect(self.core_num.display)
        self.button_export_path.clicked.connect(MainWindow.select_export_path)
        self.button_export.clicked.connect(MainWindow.on_export_dict)
        self.dial.valueChanged.connect(self.batch_size.display)
        self.progress_export.valueChanged.connect(MainWindow.on_export_progress_changed)
        self.button_zipfile_path.clicked.connect(MainWindow.select_zipfile_path)
        self.button_extract_path.clicked.connect(MainWindow.select_extract_path)
        self.button_close.clicked.connect(MainWindow.close)
        self.button_dict_path.clicked.connect(MainWindow.select_dict_path)
        self.button_crack.clicked.connect(MainWindow.on_crack_password)
        self.progress_crack.valueChanged.connect(MainWindow.on_crack_progress_changed)
        self.button_about.clicked.connect(MainWindow.on_about)

        self.dict_source.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"ArchivePasswordCracker", None))
#if QT_CONFIG(tooltip)
        self.dict_source.setToolTip(QCoreApplication.translate("MainWindow", u"切换破解方式", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.dict_source.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.dict_source.setWhatsThis(QCoreApplication.translate("MainWindow", u"切换破解方式", None))
#endif // QT_CONFIG(whatsthis)
#if QT_CONFIG(tooltip)
        self.checkBox_num.setToolTip(QCoreApplication.translate("MainWindow", u"0123456789", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.checkBox_num.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.checkBox_num.setWhatsThis(QCoreApplication.translate("MainWindow", u"\u5bc6\u7801\u662f\u5426\u5305\u542b\u6570\u5b57", None))
#endif // QT_CONFIG(whatsthis)
        self.checkBox_num.setText(QCoreApplication.translate("MainWindow", u"\u6570\u5b57\n"
"(0\uff5e9)", None))
#if QT_CONFIG(tooltip)
        self.checkBox_lower_letter.setToolTip(QCoreApplication.translate("MainWindow", u"abcdefghijklmnopqrstuvwxyz", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.checkBox_lower_letter.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.checkBox_lower_letter.setWhatsThis(QCoreApplication.translate("MainWindow", u"\u5bc6\u7801\u662f\u5426\u5305\u542b\u5c0f\u5199\u5b57\u6bcd", None))
#endif // QT_CONFIG(whatsthis)
        self.checkBox_lower_letter.setText(QCoreApplication.translate("MainWindow", u"\u5c0f\u5199\u5b57\u6bcd\n"
"(a\uff5ez)", None))
#if QT_CONFIG(tooltip)
        self.checkBox_upper_letter.setToolTip(QCoreApplication.translate("MainWindow", u"ABCDEFGHIJKLMNOPQRSTUVWXYZ", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.checkBox_upper_letter.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.checkBox_upper_letter.setWhatsThis(QCoreApplication.translate("MainWindow", u"\u5bc6\u7801\u662f\u5426\u5305\u542b\u5927\u5199\u5b57\u6bcd", None))
#endif // QT_CONFIG(whatsthis)
        self.checkBox_upper_letter.setText(QCoreApplication.translate("MainWindow", u"\u5927\u5199\u5b57\u6bcd\n"
"(A\uff5eZ)", None))
#if QT_CONFIG(tooltip)
        self.checkBox_symbols.setToolTip(QCoreApplication.translate("MainWindow", u"!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.checkBox_symbols.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.checkBox_symbols.setWhatsThis(QCoreApplication.translate("MainWindow", u"\u5bc6\u7801\u662f\u5426\u5305\u542b\u7279\u6b8a\u7b26\u53f7", None))
#endif // QT_CONFIG(whatsthis)
        self.checkBox_symbols.setText(QCoreApplication.translate("MainWindow", u"\u7279\u6b8a\u7b26\u53f7\n"
"(!\"#$%&...)", None))
#if QT_CONFIG(tooltip)
        self.digit_min.setToolTip(QCoreApplication.translate("MainWindow", u"\u8bbe\u7f6e\u6700\u4f4e\u4f4d\u6570", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.digit_min.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.digit_min.setWhatsThis(QCoreApplication.translate("MainWindow", u"\u8bbe\u7f6e\u6700\u4f4e\u4f4d\u6570", None))
#endif // QT_CONFIG(whatsthis)
        self.digit_min.setSuffix(QCoreApplication.translate("MainWindow", u"\u4f4d", None))
        self.digit_min.setPrefix("")
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"\u81f3", None))
#if QT_CONFIG(tooltip)
        self.digit_max.setToolTip(QCoreApplication.translate("MainWindow", u"\u8bbe\u7f6e\u6700\u9ad8\u4f4d\u6570", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.digit_max.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.digit_max.setWhatsThis(QCoreApplication.translate("MainWindow", u"\u8bbe\u7f6e\u6700\u9ad8\u4f4d\u6570", None))
#endif // QT_CONFIG(whatsthis)
        self.digit_max.setSuffix(QCoreApplication.translate("MainWindow", u"\u4f4d", None))
#if QT_CONFIG(tooltip)
        self.button_export.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.button_export.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.button_export.setWhatsThis("")
#endif // QT_CONFIG(whatsthis)
        self.button_export.setText(QCoreApplication.translate("MainWindow", u"\u5bfc\u51fa\u5b57\u5178", None))
#if QT_CONFIG(tooltip)
        self.progress_export.setToolTip(QCoreApplication.translate("MainWindow", u"\u5bfc\u51fa\u5b57\u5178\u8fdb\u5ea6", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.progress_export.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.progress_export.setWhatsThis(QCoreApplication.translate("MainWindow", u"\u5bfc\u51fa\u5b57\u5178\u8fdb\u5ea6", None))
#endif // QT_CONFIG(whatsthis)
#if QT_CONFIG(tooltip)
        self.export_path.setToolTip(QCoreApplication.translate("MainWindow", u"\u5bfc\u51fa\u5b57\u5178\u7684\u4fdd\u5b58\u8def\u5f84", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.export_path.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.export_path.setWhatsThis(QCoreApplication.translate("MainWindow", u"\u5bfc\u51fa\u5b57\u5178\u7684\u4fdd\u5b58\u8def\u5f84", None))
#endif // QT_CONFIG(whatsthis)
        self.export_path.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u5728\u6b64\u952e\u5165\u5bfc\u51fa\u5b57\u5178\u7684\u4fdd\u5b58\u8def\u5f84", None))
#if QT_CONFIG(tooltip)
        self.button_export_path.setToolTip(QCoreApplication.translate("MainWindow", u"\u70b9\u51fb\u9009\u62e9\u5bfc\u51fa\u5b57\u5178\u7684\u4fdd\u5b58\u8def\u5f84", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.button_export_path.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.button_export_path.setWhatsThis(QCoreApplication.translate("MainWindow", u"\u70b9\u51fb\u9009\u62e9\u5bfc\u51fa\u5b57\u5178\u7684\u4fdd\u5b58\u8def\u5f84", None))
#endif // QT_CONFIG(whatsthis)
        self.button_export_path.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.dict_source.setTabText(self.dict_source.indexOf(self.internal_dict), QCoreApplication.translate("MainWindow", u"枚举破解", None))
#if QT_CONFIG(tooltip)
        self.dict_path.setToolTip(QCoreApplication.translate("MainWindow", u"\u81ea\u5b9a\u4e49\u5b57\u5178\u4f4d\u7f6e", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.dict_path.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.dict_path.setWhatsThis(QCoreApplication.translate("MainWindow", u"\u81ea\u5b9a\u4e49\u5b57\u5178\u4f4d\u7f6e", None))
#endif // QT_CONFIG(whatsthis)
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"\u8bf7\u9009\u62e9\u81ea\u5b9a\u4e49\u5b57\u5178", None))
#if QT_CONFIG(tooltip)
        self.button_dict_path.setToolTip(QCoreApplication.translate("MainWindow", u"\u70b9\u51fb\u9009\u62e9\u81ea\u5b9a\u4e49\u5b57\u5178", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.button_dict_path.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.button_dict_path.setWhatsThis(QCoreApplication.translate("MainWindow", u"\u70b9\u51fb\u9009\u62e9\u81ea\u5b9a\u4e49\u5b57\u5178", None))
#endif // QT_CONFIG(whatsthis)
        self.button_dict_path.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.dict_source.setTabText(self.dict_source.indexOf(self.external_dict), QCoreApplication.translate("MainWindow", u"\u4f7f\u7528\u81ea\u5b9a\u4e49\u5b57\u5178", None))
#if QT_CONFIG(tooltip)
        self.groupBox_2.setToolTip(QCoreApplication.translate("MainWindow", u"\u914d\u7f6e\u540e\u53f0", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.groupBox_2.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.groupBox_2.setWhatsThis(QCoreApplication.translate("MainWindow", u"\u914d\u7f6e\u540e\u53f0", None))
#endif // QT_CONFIG(whatsthis)
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"\u914d\u7f6e\u540e\u53f0", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"\u4f7f\u7528\u6838\u5fc3\u6570\u91cf", None))
#if QT_CONFIG(tooltip)
        self.core_num.setToolTip(QCoreApplication.translate("MainWindow", u"\u540e\u53f0\u6d88\u8d39\u8005\u7684\u7ebf\u7a0b\u6570\u6216\u8fdb\u7a0b\u6570", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.core_num.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.core_num.setWhatsThis(QCoreApplication.translate("MainWindow", u"\u540e\u53f0\u6d88\u8d39\u8005\u7684\u7ebf\u7a0b\u6570\u6216\u8fdb\u7a0b\u6570", None))
#endif // QT_CONFIG(whatsthis)
#if QT_CONFIG(tooltip)
        self.cpu_slider.setToolTip(QCoreApplication.translate("MainWindow", u"\u6ed1\u52a8\u8c03\u8282\u540e\u53f0\u6d88\u8d39\u8005\u7684\u7ebf\u7a0b\u6570\u6216\u8fdb\u7a0b\u6570", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.cpu_slider.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.cpu_slider.setWhatsThis(QCoreApplication.translate("MainWindow", u"\u6ed1\u52a8\u8c03\u8282\u540e\u53f0\u6d88\u8d39\u8005\u7684\u7ebf\u7a0b\u6570\u6216\u8fdb\u7a0b\u6570", None))
#endif // QT_CONFIG(whatsthis)
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u5bc6\u7801\u6279\u91cf\u5904\u7406\u6570", None))
#if QT_CONFIG(tooltip)
        self.batch_size.setToolTip(QCoreApplication.translate("MainWindow", u"\u5bfc\u51fa\u6216\u5bfc\u5165\u5bc6\u7801\u65f6\u6279\u91cf\u5904\u7406\u5bc6\u7801\u6570\u91cf", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.batch_size.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.batch_size.setWhatsThis(QCoreApplication.translate("MainWindow", u"\u5bfc\u51fa\u6216\u5bfc\u5165\u5bc6\u7801\u65f6\u6279\u91cf\u5904\u7406\u5bc6\u7801\u6570\u91cf", None))
#endif // QT_CONFIG(whatsthis)
#if QT_CONFIG(tooltip)
        self.dial.setToolTip(QCoreApplication.translate("MainWindow", u"\u8f6c\u52a8\u8c03\u8282\u6279\u91cf\u5904\u7406\u5bc6\u7801\u7684\u6570\u91cf", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.dial.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.dial.setWhatsThis(QCoreApplication.translate("MainWindow", u"\u8f6c\u52a8\u8c03\u8282\u6279\u91cf\u5904\u7406\u5bc6\u7801\u7684\u6570\u91cf", None))
#endif // QT_CONFIG(whatsthis)
#if QT_CONFIG(tooltip)
        self.groupBox.setToolTip(QCoreApplication.translate("MainWindow", u"\u5f00\u59cb\u7834\u89e3", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.groupBox.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.groupBox.setWhatsThis(QCoreApplication.translate("MainWindow", u"\u5f00\u59cb\u7834\u89e3", None))
#endif // QT_CONFIG(whatsthis)
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"\u5f00\u59cb\u7834\u89e3", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u8bf7\u9009\u62e9\u538b\u7f29\u6587\u4ef6", None))
#if QT_CONFIG(tooltip)
        self.zipfile_path.setToolTip(QCoreApplication.translate("MainWindow", u"\u538b\u7f29\u6587\u4ef6\u4f4d\u7f6e", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.zipfile_path.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.zipfile_path.setWhatsThis(QCoreApplication.translate("MainWindow", u"\u538b\u7f29\u6587\u4ef6\u4f4d\u7f6e", None))
#endif // QT_CONFIG(whatsthis)
#if QT_CONFIG(tooltip)
        self.button_zipfile_path.setToolTip(QCoreApplication.translate("MainWindow", u"\u70b9\u51fb\u9009\u62e9\u538b\u7f29\u6587\u4ef6", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.button_zipfile_path.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.button_zipfile_path.setWhatsThis(QCoreApplication.translate("MainWindow", u"\u70b9\u51fb\u9009\u62e9\u538b\u7f29\u6587\u4ef6", None))
#endif // QT_CONFIG(whatsthis)
        self.button_zipfile_path.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\u8bf7\u9009\u62e9\u89e3\u538b\u4f4d\u7f6e", None))
#if QT_CONFIG(tooltip)
        self.extract_path.setToolTip(QCoreApplication.translate("MainWindow", u"\u89e3\u538b\u8def\u5f84", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.extract_path.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.extract_path.setWhatsThis(QCoreApplication.translate("MainWindow", u"\u89e3\u538b\u8def\u5f84", None))
#endif // QT_CONFIG(whatsthis)
#if QT_CONFIG(tooltip)
        self.button_extract_path.setToolTip(QCoreApplication.translate("MainWindow", u"\u70b9\u51fb\u9009\u62e9\u89e3\u538b\u4f4d\u7f6e", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.button_extract_path.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.button_extract_path.setWhatsThis(QCoreApplication.translate("MainWindow", u"\u70b9\u51fb\u9009\u62e9\u89e3\u538b\u4f4d\u7f6e", None))
#endif // QT_CONFIG(whatsthis)
        self.button_extract_path.setText(QCoreApplication.translate("MainWindow", u"...", None))
#if QT_CONFIG(tooltip)
        self.button_crack.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.button_crack.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.button_crack.setWhatsThis("")
#endif // QT_CONFIG(whatsthis)
        self.button_crack.setText(QCoreApplication.translate("MainWindow", u"\u5f00\u59cb\u7834\u89e3", None))
#if QT_CONFIG(tooltip)
        self.progress_crack.setToolTip(QCoreApplication.translate("MainWindow", u"\u7834\u89e3\u8fdb\u5ea6", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.progress_crack.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.progress_crack.setWhatsThis(QCoreApplication.translate("MainWindow", u"\u7834\u89e3\u8fdb\u5ea6", None))
#endif // QT_CONFIG(whatsthis)
        self.label_password_is.setText(QCoreApplication.translate("MainWindow", u"\u5bc6\u7801\u662f", None))
#if QT_CONFIG(tooltip)
        self.password.setToolTip(QCoreApplication.translate("MainWindow", u"\u7834\u89e3\u51fa\u7684\u538b\u7f29\u5bc6\u7801", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.password.setStatusTip("")
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.password.setWhatsThis(QCoreApplication.translate("MainWindow", u"\u7834\u89e3\u51fa\u7684\u538b\u7f29\u5bc6\u7801", None))
#endif // QT_CONFIG(whatsthis)
        self.button_about.setText(QCoreApplication.translate("MainWindow", u"\u5173\u4e8e\u8f6f\u4ef6", None))
        self.button_close.setText(QCoreApplication.translate("MainWindow", u"\u9000\u51fa", None))
    # retranslateUi

