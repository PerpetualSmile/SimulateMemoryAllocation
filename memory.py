from PyQt5 import Qt
from PyQt5 import QtCore,QtWidgets,QtGui
import sys
import PyQt5
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QInputDialog, QMessageBox, QTableWidgetItem
from PyQt5.QtGui import QPixmap, QImage
import cv2
import numpy as np
from matplotlib import pyplot as plt
from collections import OrderedDict

import window


class MainWindow():
    def __init__(self):
        app = QtWidgets.QApplication(sys.argv)
        MainWindow = QtWidgets.QMainWindow()
        self.ui = window.Ui_MainWindow()
        self.ui.setupUi(MainWindow)
        self.ui.label.setScaledContents(True)
        self.slot_init()
        self.intialize()
        MainWindow.show()
        sys.exit(app.exec_())

    def slot_init(self):
        self.ui.pushButton_2.clicked.connect(self.malloc)
        self.ui.pushButton_3.clicked.connect(self.mfree)
        self.ui.pushButton.clicked.connect(self.clear)
        self.ui.pushButton_4.clicked.connect(self.mcompress)

    def intialize(self):
        self.user_dict = OrderedDict()
        self.full = []
        self.empty = [(0, 1000)]
        self.show()

    def mlist(self):
        self.ui.tableWidget.setRowCount(len(self.full))
        self.ui.tableWidget_3.setRowCount(len(self.empty))
        self.block_list = []
        for i in self.full:
            self.block_list.append(i)
        for i in self.empty:
            self.block_list.append(i)
        self.block_list.sort()
        i = 0
        j = 0
        p_id = 0
        for block in self.block_list:
            if block in self.empty:
                temp1 = QTableWidgetItem(str(i + j))
                temp2 = QTableWidgetItem(str(block[0]))
                temp3 = QTableWidgetItem(str(block[1] - block[0]))
                temp4 = QTableWidgetItem(str('NULL'))
                self.ui.tableWidget_3.setItem(i, 0, temp1)
                self.ui.tableWidget_3.setItem(i, 1, temp2)
                self.ui.tableWidget_3.setItem(i, 2, temp3)
                self.ui.tableWidget_3.setItem(i, 3, temp4)

                i += 1
            else:
                for k, v in self.user_dict.items():
                    if v == block:
                        p_id = k
                        break
                temp1 = QTableWidgetItem(str(i + j))
                temp2 = QTableWidgetItem(str(block[0]))
                temp3 = QTableWidgetItem(str(block[1] - block[0]))
                temp4 = QTableWidgetItem(str(p_id))
                self.ui.tableWidget.setItem(j, 0, temp1)
                self.ui.tableWidget.setItem(j, 1, temp2)
                self.ui.tableWidget.setItem(j, 2, temp3)
                self.ui.tableWidget.setItem(j, 3, temp4)
                j += 1


    def malloc(self):
        pid, ok1 = QInputDialog.getInt(None, '分配内存', '进程号：')
        length, ok2 = QInputDialog.getInt(None, '分配内存', '作业长度：')
        if pid in self.user_dict:
            msgBox = QMessageBox()
            msgBox.setWindowTitle('错误')
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText("该进程号已经存在！")
            msgBox.setStandardButtons(QMessageBox.Retry | QMessageBox.Abort)
            msgBox.setDefaultButton(QMessageBox.Abort)
            reply = msgBox.exec()
            if reply == QMessageBox.Retry:
                self.malloc()
            return 0

        if length <= 0:
            msgBox = QMessageBox()
            msgBox.setWindowTitle('错误')
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText("作业长度不合法！")
            msgBox.setStandardButtons(QMessageBox.Retry | QMessageBox.Abort)
            msgBox.setDefaultButton(QMessageBox.Abort)
            reply = msgBox.exec()
            if reply == QMessageBox.Retry:
                self.malloc()
            return 0

        if length > sum(i[1] - i[0] for i in self.empty):
            msgBox = QMessageBox()
            msgBox.setWindowTitle('错误')
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText("内存空间不够！")
            msgBox.setStandardButtons(QMessageBox.Retry | QMessageBox.Abort)
            msgBox.setDefaultButton(QMessageBox.Abort)
            reply = msgBox.exec()
            if reply == QMessageBox.Retry:
                self.malloc()
            return 0

        if ok1 and ok2:
            if length > max(i[1] - i[0] for i in self.empty):
                msgBox = QMessageBox()
                msgBox.setWindowTitle('提示')
                msgBox.setIcon(QMessageBox.Information)
                msgBox.setText("内存需要紧缩！")
                msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                msgBox.setDefaultButton(QMessageBox.Ok)
                reply = msgBox.exec()
                if reply == QMessageBox.Cancel:
                    return 0
                self.mcompress()

            # 采用首次适应算法
            for block in self.empty:
                if length <= block[1] - block[0]:
                    self.empty.remove(block)
                    self.full.append((block[0], block[0] + length))
                    if length < block[1] - block[0]:
                        self.empty.append((block[0] + length, block[1]))
                    self.user_dict[pid] = (block[0], block[0] + length)
                    break
        self.show()



    def mfree(self):
        pid, ok = QInputDialog.getInt(None, '回收内存', '进程号：')
        if pid not in self.user_dict:
            msgBox = QMessageBox()
            msgBox.setWindowTitle('错误')
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText("该进程不存在！")
            msgBox.setStandardButtons(QMessageBox.Retry | QMessageBox.Abort)
            msgBox.setDefaultButton(QMessageBox.Abort)
            reply = msgBox.exec()
            if reply == QMessageBox.Retry:
                self.mfree()
            return 0
        if ok:
            index = self.full.index(self.user_dict[pid])
            if len(self.full) == 1:
                self.empty.clear()
                self.empty.append((0, 1000))
                self.full.remove(self.user_dict[pid])
                self.user_dict.pop(pid)
                self.show()
                return 0
            if index == 0:
                if self.full[index + 1][0] == self.full[index][1]:
                    self.empty.append((0, self.full[index][1]))
                    if (0, self.full[index][0]) in self.empty:
                        self.empty.remove((0, self.full[index][0]))
                else:
                    self.empty.append((0, self.full[index + 1][0]))
                    self.empty.remove((self.full[index][1], self.full[index + 1][0]))
                    if (0, self.full[index][0]) in self.empty:
                        self.empty.remove((0, self.full[index][0]))
                self.full.remove(self.user_dict[pid])
                self.user_dict.pop(pid)
                self.show()
                return 0

            if index == len(self.full) - 1:
                if self.full[index][0] == self.full[index - 1][1]:
                    self.empty.append((self.full[index][0], 1000))
                    if self.full[index][1] != 1000:
                        self.empty.remove((self.full[index][1], 1000))
                else:
                    self.empty.append((self.full[index - 1][1], 1000))
                    self.empty.remove((self.full[index - 1][1], self.full[index][0]))
                    if self.full[index][1] != 1000:
                        self.empty.remove((self.full[index][1], 1000))
                self.full.remove(self.user_dict[pid])
                self.user_dict.pop(pid)
                self.show()
                return 0

            # 前面一块满
            if self.full[index - 1][1] == self.full[index][0]:
                # 后面一块满
                if self.full[index + 1][0] == self.full[index][1]:
                    self.empty.append(self.user_dict[pid])
                # 前满后空
                else:
                    self.empty.append((self.full[index][0], self.full[index + 1][0]))
                    self.empty.remove((self.full[index][1], self.full[index + 1][0]))

            # 前面一块空
            else:
                # 后面一块满
                if self.full[index + 1][0] == self.full[index][1]:
                    self.empty.append((self.full[index - 1][1], self.full[index][1]))
                    self.empty.remove((self.full[index - 1][1], self.full[index][0]))
                # 后面一块空
                else:
                    self.empty.append((self.full[index - 1][1], self.full[index + 1][0]))
                    self.empty.remove((self.full[index - 1][1], self.full[index][0]))
                    self.empty.remove((self.full[index][1], self.full[index + 1][0]))
            self.full.remove(self.user_dict[pid])
            self.user_dict.pop(pid)
            self.show()

    def clear(self):
        self.intialize()


    # 内存紧缩
    def mcompress(self):
        len_list = [i[1] - i[0] for i in self.full]
        self.full.clear()
        self.empty.clear()
        start = 0
        for length in len_list:
            self.full.append((start, start + length))
            start += length
        self.empty.append((sum(len_list), 1000))
        temp = self.full.copy()
        for key, value in self.user_dict.items():
            for i in temp:
                if i[1] - i[0] == value[1] - value[0]:
                    self.user_dict[key] = (i[0], i[1])
                    temp.remove(i)
                    break
        self.show()

    def show(self):
        self.full.sort()
        self.empty.sort()

        l = []
        h = []
        w = []
        for block in self.full:
            l.append(block[0])
            h.append(100)
            w.append(block[1] - block[0])

        plt.figure(frameon=False)
        plt.bar(left=l, height=h, width=w, edgecolor='b', linewidth=1, align='edge', alpha=0.8)

        l = []
        h = []
        w = []
        for block in self.empty:
            l.append(block[0])
            h.append(100)
            w.append(block[1] - block[0])
        plt.bar(left=l, height=h, width=w, color='powderblue', edgecolor='b',  linewidth=1, align='edge', alpha=0.5)
        plt.axes().get_yaxis().set_visible(False)
        # plt.axes().get_xaxis().set_visible(False)
        ax = plt.axes()
        # 隐藏坐标系的外围框线
        for spine in ax.spines.values():
            spine.set_visible(False)
        plt.xticks([0, 200, 400, 600, 800, 1000], color='deepskyblue', alpha=0.7)
        ax.tick_params(width=0, color='deepskyblue')
        plt.savefig('Hist.png', bbox_inches="tight", transparent=True, dpi=100)
        pix = QPixmap("Hist.png")
        self.ui.label.setPixmap(pix)
        self.mlist()


if __name__ == "__main__":
    MainWindow()