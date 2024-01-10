import io
import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
from datetime import datetime
from uimain import Ui_MainWindow
from uiadd import Ui_Form



DB_NAME = 'data/coffee.sqlite'


class AddWidget(QMainWindow, Ui_Form):
    def __init__(self, parent=None, id=None):
        super().__init__(parent)
        self.setupUi(self)
        self.id = id
        self.con = sqlite3.connect(DB_NAME)
        if self.id is not None:
            self.pushButton.clicked.connect(self.edit_elem)
            self.pushButton.setText('Отредактировать')
            self.setWindowTitle('Редактирование записи')
        else:
            self.pushButton.clicked.connect(self.add_elem)
            self.pushButton.setText('Добавить')
            self.setWindowTitle('Добавление записи')
        self.__is_adding_successful = False
        self.__is_editing_successful = False
        self.comboBox.addItems(['молотый', 'в зернах'])

    def add_elem(self):
        cur = self.con.cursor()
        try:
            id = cur.execute("SELECT max(id) FROM coffee").fetchone()[0] + 1
            title = self.title.toPlainText()
            roast = self.year.toPlainText()
            type = self.comboBox.currentText()
            descr = self.duration.toPlainText()
            if len(title) == 0:
                raise ValueError('title lenght == 0')
            if len(roast) == 0:
                raise ValueError('roast lenght == 0')
            if len(descr) == 0:
                raise ValueError('descr lenght == 0')
            new_data = (id, title, roast, type, descr)
            cur.execute("INSERT INTO coffee VALUES (?,?,?,?,?)", new_data)
            self.__is_adding_successful = True
        except ValueError:
            self.__is_adding_successful = False
            self.statusBar().showMessage("Неверно заполнена форма")
        else:
            self.con.commit()
            self.parent().update_results()
            self.close()

    def edit_elem(self):
        cur = self.con.cursor()
        try:
            title = self.title.toPlainText()
            roast = self.year.toPlainText()
            type = self.comboBox.currentText()
            descr = self.duration.toPlainText()
            if len(title) == 0:
                raise ValueError('title lenght == 0')
            if len(roast) == 0:
                raise ValueError('roast lenght == 0')
            if len(descr) == 0:
                raise ValueError('descr lenght == 0')
            for id in self.id:
                new_data = (title, roast, type, descr, id)
                que = "UPDATE coffee SET title = ?, roast = ?, type = ?, description = ? WHERE id = ?"
                cur.execute(que, new_data)
                self.con.commit()
            self.__is_editing_successful = True
        except ValueError:
            self.__is_editing_successful = False
            self.statusBar().showMessage("Неверно заполнена форма")
        else:
            self.con.commit()
            self.parent().update_results()
            self.close()

    def get_adding_verdict(self):
        return self.__is_adding_successful

    def get_editing_verdict(self):
        return self.__is_editing_successful



class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.con = sqlite3.connect(DB_NAME)
        self.update_results()
        self.addButton.clicked.connect(self.add)
        self.editButton.clicked.connect(self.edit)
        self.add_widget = None
        self.edit_widget = None

    def update_results(self):
        cur = self.con.cursor()
        que = "SELECT * FROM coffee "
        que = cur.execute(que)
        names = list(map(lambda x: x[0], cur.description))
        result = que.fetchall()
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]))
        self.tableWidget.setHorizontalHeaderLabels(names)
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
    def add(self):
        self.add_film_widget = AddWidget(self)
        self.add_film_widget.show()

    def edit(self):
        selected_rows = [item.row() for item in self.tableWidget.selectedItems()]
        if not selected_rows:
            self.statusBar().showMessage("Ничего не выбрано.")
        else:
            id_list = [self.tableWidget.item(row, 0).text() for row in selected_rows]
            self.statusBar().clearMessage()
            self.edit_widget = AddWidget(self, id_list)
            self.edit_widget.show()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MyWidget()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
