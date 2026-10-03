# -*- coding: utf-8 -*-
#
# 本文件由 Qt Designer 的 .ui 文件经 pyside6-uic 转换而来；原始 .ui 的来源与署名见
# LICENSE / AUTHORS.md。本项目对转换结果所做的修改：
# Copyright (c) 2026 bakeryg  —  SPDX-License-Identifier: MIT
# 项目地址: https://github.com/bakeryg/ArchivePasswordCracker
#
################################################################################
## Form generated from reading UI file 'AboutDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QCommandLinkButton, QDialog, QGridLayout,
    QLabel, QSizePolicy, QSpacerItem, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(380, 320)
        icon = QIcon()
        icon.addFile(u"icon.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        Dialog.setWindowIcon(icon)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        font = QFont()
        font.setFamilies([u"\u534e\u6587\u884c\u6977"])
        font.setPointSize(12)
        self.label_2.setFont(font)

        self.gridLayout.addWidget(self.label_2, 1, 2, 1, 1)

        self.commandLinkButton_2 = QCommandLinkButton(Dialog)
        self.commandLinkButton_2.setObjectName(u"commandLinkButton_2")

        self.gridLayout.addWidget(self.commandLinkButton_2, 3, 2, 1, 1)

        self.commandLinkButton = QCommandLinkButton(Dialog)
        self.commandLinkButton.setObjectName(u"commandLinkButton")

        self.gridLayout.addWidget(self.commandLinkButton, 2, 2, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 0, 2, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 4, 2, 1, 1)

        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        # 原生成文件此处加载 ../res/QRcode.png（原作者的联系/收款项二维码），
        # 已移除：本项目不复用他人图片，该图不再显示。
        self.label.setVisible(False)

        self.gridLayout.addWidget(self.label, 0, 1, 5, 1)


        self.retranslateUi(Dialog)
        self.commandLinkButton.clicked.connect(Dialog.on_to_url)
        self.commandLinkButton_2.clicked.connect(Dialog.close)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"\u5173\u4e8e\u8f6f\u4ef6", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"ArchivePasswordCracker\n"
"\n"
"作者：bakeryg\n"
"\n"
"基于 Bandizip 引擎的压缩包密码破解工具\n"
"界面源自开源项目 GoogleLLP/Archive-password-cracker\n"
"原作者：宗祥瑞\n"
"破解引擎：Bandizip 的 bz.exe", None))
        self.commandLinkButton_2.setText(QCoreApplication.translate("Dialog", u"\u597d\u7684", None))
        self.commandLinkButton.setText(QCoreApplication.translate("Dialog", u"\u8bbf\u95ee\u9879\u76ee\u4e3b\u9875", None))
        self.label.setText("")
    # retranslateUi

