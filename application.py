import sys
import string
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
import pandas as pd


button_labels = ['Молочные продукты', 'Напитки', 'Крупы', 
                 'Хлебобулочные изделия', 'Гигиена', 'Товары для дома',
                 'Алкоголь', 'Сладости', 'Замороженные продукты']

label_map = {
    'Молочные продукты': 0, 
    'Напитки': 1, 
    'Крупы': 2, 
    'Хлебобулочные изделия': 3, 
    'Гигиена': 4, 
    'Товары для дома': 5,
    'Алкоголь': 6, 
    'Сладости': 7, 
    'Замороженные продукты': 8
}

genders = ['Мужчина', 'Женщина', 'Не указано']

gender_map = {
    'Мужчина': 0, 
    'Женщина': 1, 
    'Не указано': 2
}

db_file_1 = 'db_1.csv'
db_file_2 = 'db_2.csv'
db_sep = ','

class App(QWidget):

    def __init__(self, db_path_1, db_path_2):
        super().__init__()
        self.cat_checkboxes = []
        self.gender_checkboxes = []
        self.data_path_1 = db_path_1
        self.data_path_2 = db_path_2
        self.predictive = True
        self.initUI()

    def execute_query(self, sel_labels=None, sel_genders=None, age_range=None):
        dp = self.data_path_1 if self.predictive else self.data_path_2
        with open(dp, 'r') as file:
            columns = file.readline().split(db_sep)
            columns = [i.replace('\n', '') for i in columns]

            category_index = columns.index('category')
            gender_index = columns.index('gender')
            age_index = columns.index('age')

            rows = []
            for srow in file:
                row = [i.replace('\n', '') for i in srow.split(db_sep)]
                if int(row[category_index]) not in sel_labels:
                    continue
                if int(row[gender_index]) not in sel_genders:
                    continue
                if age_range is not None:
                    if int(row[age_index]) < age_range[0] or int(row[age_index]) > age_range[1]:
                        continue
                rows.append(row[0])
                
        frame = pd.DataFrame(rows, columns=['phone'])
        return frame

    def initialize_label(self,):
        self.label = QLabel()
        self.label.setFixedWidth(300)
        self.label.setWordWrap(True)
        return self.label

    def hist_buttonClicked(self):

        self.predictive = False

        sel_labels = [label_map[i.text().replace('&', '')] for i in self.cat_checkboxes if i.isChecked()]
        sel_genders = [gender_map[i.text()] for i in self.gender_checkboxes if i.isChecked()]
        sel_ages = None
        if self.age_from.text() != string.whitespace and self.age_to.text() != string.whitespace:
            sel_ages = (int(self.age_from.text()), int(self.age_to.text()))

        frame = self.execute_query(sel_labels=sel_labels, sel_genders=sel_genders, age_range=sel_ages)

        self.records_count.setText(str(len(frame)))

        path = self.line_edit.text()
        frame.to_csv(path, index=False)

    def pred_buttonClicked(self):

        self.predictive = True

        sel_labels = [label_map[i.text().replace('&', '')] for i in self.cat_checkboxes if i.isChecked()]
        sel_genders = [gender_map[i.text()] for i in self.gender_checkboxes if i.isChecked()]
        sel_ages = None
        if self.age_from.text() != string.whitespace and self.age_to.text() != string.whitespace:
            sel_ages = (int(self.age_from.text()), int(self.age_to.text()))

        frame = self.execute_query(sel_labels=sel_labels, sel_genders=sel_genders, age_range=sel_ages)

        self.records_count.setText(str(len(frame)))

        path = self.line_edit.text()
        frame.to_csv(path, index=False)

    def initialize_select_button(self):
        self.select_button = QPushButton(text='Историческая выгрузка')
        self.select_button.clicked.connect(self.hist_buttonClicked)
        return self.select_button

    def initialize_smart_button(self):
        self.smart_button = QPushButton(text='Предиктивная выгрузка')
        self.smart_button.clicked.connect(self.pred_buttonClicked)
        return self.smart_button

    def initialize_cat_row(self, num):
        layout = QHBoxLayout()
        for label in button_labels[num * 3 : (num + 1) * 3]:
            cb = QCheckBox(label)
            layout.addWidget(cb)
            self.cat_checkboxes.append(cb)
        return layout

    def initialize_gender_row(self):
        layout = QHBoxLayout()
        for label in genders:
            cb = QCheckBox(label)
            layout.addWidget(cb)
            self.gender_checkboxes.append(cb)
        return layout

    def initialize_age_row(self):
        layout = QHBoxLayout()
        l1 = QLabel('От')
        self.age_from = QLineEdit()
        l2 = QLabel('до')
        self.age_to = QLineEdit()
        layout.addWidget(l1)
        layout.addWidget(self.age_from)
        layout.addWidget(l2)
        layout.addWidget(self.age_to)
        return layout

    def initialize_footer(self):
        layout = QHBoxLayout()
        self.line_edit = QLineEdit('Enter the path to result file')
        layout.addWidget(self.line_edit)
        layout.addWidget(self.initialize_smart_button())
        layout.addWidget(self.initialize_select_button())
        return layout

    def initUI(self):
        self.resize(600,400)
        self.setWindowTitle('Segmentation application')

        grid = QGridLayout(self)
        label = QLabel('Фильтрация и выгрузка данных')
        label.setMaximumHeight(100)
        label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        label.setFont(QtGui.QFont("Times", 16, QtGui.QFont.Bold))
        grid.addWidget(label, 0, 0, 1, 2)

        grid.addWidget(QLabel('Категория'), 1, 0, 3, 1)
        grid.addWidget(QLabel('Пол'), 4, 0, 1, 1)
        grid.addWidget(QLabel('Возраст'), 5, 0, 1, 1)

        grid.addLayout(self.initialize_cat_row(0), 1, 1, 1, 1)
        grid.addLayout(self.initialize_cat_row(1), 2, 1, 1, 1)
        grid.addLayout(self.initialize_cat_row(2), 3, 1, 1, 1)
        grid.addLayout(self.initialize_gender_row(), 4, 1, 1, 1)
        grid.addLayout(self.initialize_age_row(), 5, 1, 1, 1)

        grid.addWidget(QLabel('Обьем выгрузки'), 6, 0, 1, 1)
        self.records_count = QLabel()
        self.records_count.setFixedHeight(20)
        grid.addWidget(self.records_count, 6, 1, 1, 1)
        grid.addLayout(self.initialize_footer(), 7, 0, 1, 2)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App(db_file_1, db_file_2)
    sys.exit(app.exec_())