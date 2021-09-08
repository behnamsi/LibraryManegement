import os
import sys

from PyQt5.uic import loadUi
import pymysql
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QTableWidgetItem, QTableWidget
from PyQt5.QtWidgets import QMessageBox

# connect to your database
yourUsername = ''
yourPasswd = ''
yourLibrary = ''
myDB = pymysql.connect(
    host='localhost',
    user=yourUsername,
    passwd=yourPasswd,
    database=yourLibrary
)
myCursor = myDB.cursor()


# first and main page class
class MainPageScreen(QDialog):
    def __init__(self):
        super(MainPageScreen, self).__init__()
        # connect ui file to my class
        loadUi('main_page.ui', self)
        # buttons actions
        self.add_book_button.clicked.connect(self.goToAddBook)
        self.remove_book_button.clicked.connect(self.goToDeleteBook)
        self.list_book_button.clicked.connect(self.goToListBook)
        self.search_book_button.clicked.connect(self.goToSearchBook)
        self.rent_book_button.clicked.connect(self.goToRentBook)
        self.rented_book_button.clicked.connect(self.goToRentedBook)

    def goToAddBook(self):
        widget.setCurrentIndex(addScreenIndex)

    def goToDeleteBook(self):
        widget.setCurrentIndex(deleteScreenIndex)

    def goToListBook(self):
        widget.setCurrentIndex(listScreenIndex)

    def goToSearchBook(self):
        widget.setCurrentIndex(searchScreenIndex)

    def goToRentBook(self):
        widget.setCurrentIndex(rentScreenIndex)

    def goToRentedBook(self):
        widget.setCurrentIndex(rentedScreenIndex)


class AddBookScreen(QDialog):
    def __init__(self):
        super(AddBookScreen, self).__init__()
        loadUi('add_book_page.ui', self)
        self.back_button.clicked.connect(self.backMainPage)
        self.submit_button.clicked.connect(self.submitTheBook)
        self.refresh_button.clicked.connect(self.refreshTheBook)

    def backMainPage(self):
        widget.setCurrentIndex(mainScreenIndex)

    # restart the App to refresh data
    def refreshTheBook(self):
        os.execl(sys.executable, sys.executable, *sys.argv)

    def submitTheBook(self):
        # insert query of mysql
        insertString = f'insert into Books values("{self.id_edit.text()}","{self.title_edit.text()}","{self.author_edit.text()}",' \
                       f'"{self.genre_edit.text()}","{self.price_edit.text()}")'
        try:
            # check to see all the fields won't be empty
            if self.id_edit.text() and self.title_edit.text() and self.author_edit.text() and self.genre_edit.text() and self.price_edit.text() != '':
                myCursor.execute(insertString)
                myDB.commit()
                QMessageBox.about(self, 'database state', 'successfully added')
            else:
                QMessageBox.about(self, 'Error', 'fill all the boxes')
        except pymysql.err.IntegrityError as e:
            QMessageBox.about(self, 'Error', str(e))
        finally:
            self.id_edit.setText('')
            self.title_edit.setText('')
            self.author_edit.setText('')
            self.genre_edit.setText('')
            self.price_edit.setText('')


class DeleteBookScreen(QDialog):
    def __init__(self):
        super(DeleteBookScreen, self).__init__()
        loadUi('delete_book_page.ui', self)
        self.back_button.clicked.connect(self.backMainPage)
        self.submit_button.clicked.connect(self.deleteTheBook)
        self.refresh_button.clicked.connect(self.refreshTheBook)

    def backMainPage(self):
        widget.setCurrentIndex(mainScreenIndex)

    def refreshTheBook(self):
        os.execl(sys.executable, sys.executable, *sys.argv)

    def deleteTheBook(self):
        # for deleting a book from library most check if its rent or not
        deleteString = f'delete from Books where book_id = "{self.id_edit.text()}"'
        deleteRentString = f'delete from rented_books where book_id = "{self.id_edit.text()}"'

        try:
            # check to see its available or not
            myCursor.execute(f'select book_id from Books where book_id = "{self.id_edit.text()}"')
            strState = myCursor.fetchone()
            print(str(strState))
            if str(strState) == "None":
                QMessageBox.about(self, 'Error', "no book id such this")
            else:
                myCursor.execute(deleteRentString)
                myDB.commit()
                myCursor.execute(deleteString)
                myDB.commit()
                QMessageBox.about(self, 'Success message', "successfully deleted")
        except pymysql.err.DatabaseError as e:
            print(e)
            QMessageBox.about(self, "Error", str(e))
        finally:
            self.id_edit.setText('')


class BookListScreen(QDialog):
    def __init__(self):
        super(BookListScreen, self).__init__()
        loadUi('list_books_page.ui', self)
        self.back_button.clicked.connect(self.backMainPage)
        self.show_button.clicked.connect(self.showData)
        self.book_list.setColumnWidth(0, 109)
        self.book_list.setColumnWidth(1, 200)
        self.book_list.setColumnWidth(2, 200)
        self.book_list.setColumnWidth(3, 200)
        self.book_list.setColumnWidth(4, 200)

    def _loadData(self):
        try:
            # get all data to show
            myCursor.execute(f'select * from Books')
            fieldTuple = myCursor.fetchall()
            myDB.commit()
            # set list row num
            self.book_list.setRowCount(len(fieldTuple))
            row = 0
            for i in fieldTuple:
                self.book_list.setItem(row, 0, QtWidgets.QTableWidgetItem(i[0]))
                self.book_list.setItem(row, 1, QtWidgets.QTableWidgetItem(i[1]))
                self.book_list.setItem(row, 2, QtWidgets.QTableWidgetItem(i[2]))
                self.book_list.setItem(row, 3, QtWidgets.QTableWidgetItem(i[3]))
                self.book_list.setItem(row, 4, QtWidgets.QTableWidgetItem(i[4]))
                row += 1
        except pymysql.err.DatabaseError as e:
            QMessageBox.about(self, 'Error', str(e))

    def showData(self):
        self._loadData()

    def backMainPage(self):
        widget.setCurrentIndex(mainScreenIndex)
        self.book_list.setRowCount(0)


class SearchBookScreen(QDialog):
    def __init__(self):
        super(SearchBookScreen, self).__init__()
        loadUi('search_page.ui', self)
        self.back_button.clicked.connect(self.backMainPage)
        self.search_button.clicked.connect(self.searchBook)

    def backMainPage(self):
        widget.setCurrentIndex(mainScreenIndex)
        self.search_list.setRowCount(0)

    def searchBook(self):
        # defines search by which[id,title,author]
        fieldDB = ''
        if self.id_rbutton.isChecked():
            fieldDB = 'book_id'
        elif self.author_rbutton.isChecked():
            fieldDB = 'author'
        else:
            fieldDB = 'title'
        queryString = f'select * from Books where {fieldDB} = "{self.value_edit.text()}"'

        # filling the list
        try:
            myCursor.execute(queryString)
            myTuple = myCursor.fetchall()
            myDB.commit()
            self.search_list.setRowCount(len(myTuple))
            row = 0
            for i in myTuple:
                self.search_list.setItem(row, 0, QtWidgets.QTableWidgetItem(i[0]))
                self.search_list.setItem(row, 1, QtWidgets.QTableWidgetItem(i[1]))
                self.search_list.setItem(row, 2, QtWidgets.QTableWidgetItem(i[2]))
                self.search_list.setItem(row, 3, QtWidgets.QTableWidgetItem(i[3]))
                self.search_list.setItem(row, 4, QtWidgets.QTableWidgetItem(i[4]))
                row += 1
        except pymysql.err.DatabaseError as e:
            QMessageBox.about(self, 'Error', 'could not reach database')
        finally:
            self.value_edit.setText('')


class RentBookScreen(QDialog):
    def __init__(self):
        super(RentBookScreen, self).__init__()
        loadUi('rent_book_page.ui', self)
        self.back_button.clicked.connect(self.backMainPage)
        self.submit_button.clicked.connect(self.submitTheRent)
        self.refresh_button.clicked.connect(self.refreshTheApp)

    def refreshTheApp(self):
        os.execl(sys.executable, sys.executable, *sys.argv)

    def backMainPage(self):
        widget.setCurrentIndex(mainScreenIndex)

    def submitTheRent(self):
        # insert data into rent table of database
        queryString = f'insert into rented_books values ({self.id_edit.text()})'
        try:
            myCursor.execute(queryString)
            myDB.commit()
            QMessageBox.about(self, 'Success', 'rented successfully')
        except pymysql.err.DatabaseError as e:
            QMessageBox.about(self, 'Error', str(e) + '\n Enter a valid ID')
        finally:
            self.id_edit.setText('')
        print(queryString)


class RentedBookScreen(QDialog):
    def __init__(self):
        super(RentedBookScreen, self).__init__()
        loadUi('rented_book_page.ui', self)
        self.back_button.clicked.connect(self.backMainPage)
        self.submit_button.clicked.connect(self.submitTheRent)
        self.show_button.clicked.connect(self.showList)

    def backMainPage(self):
        widget.setCurrentIndex(mainScreenIndex)
        self.book_list.setRowCount(0)

    def showList(self):
        self._loadData()

    def submitTheRent(self):
        # delete data from rent books table
        queryString = f'delete from rented_books where book_id = "{self.id_edit.text()}"'

        if str(self.id_edit.text()) != '':
            myCursor.execute(f'select book_id from rented_books where book_id = "{self.id_edit.text()}"')
            strState = myCursor.fetchone()
            myDB.commit()
            print(str(strState))
            if str(strState) == "None":
                QMessageBox.about(self, 'Error', "no book id such this")
            else:
                try:
                    myCursor.execute(queryString)
                    myDB.commit()
                    QMessageBox.about(self, 'Success', 'Delivered to library')
                except pymysql.err.DatabaseError as e:
                    QMessageBox(self, 'Error', str(e))
        else:
            QMessageBox.about(self, 'Error', "fill the box")
        self._loadData()

    # load data (load data into my list)
    def _loadData(self):
        queryString = f'select Books.book_id,title,author,genre,price from Books,rented_books where Books.book_id=rented_books.book_id'
        try:
            myCursor.execute(queryString)
            myTuple = myCursor.fetchall()
            myDB.commit()
            self.book_list.setRowCount(len(myTuple))
            row = 0
            for i in myTuple:
                self.book_list.setItem(row, 0, QtWidgets.QTableWidgetItem(i[0]))
                self.book_list.setItem(row, 1, QtWidgets.QTableWidgetItem(i[1]))
                self.book_list.setItem(row, 2, QtWidgets.QTableWidgetItem(i[2]))
                self.book_list.setItem(row, 3, QtWidgets.QTableWidgetItem(i[3]))
                self.book_list.setItem(row, 4, QtWidgets.QTableWidgetItem(i[4]))
                row += 1
        except pymysql.err.DatabaseError:
            QMessageBox.about(self, 'Error', 'could not reach database')
        finally:
            self.id_edit.setText('')


# main program
app = QApplication(sys.argv)
mainPageScreen = MainPageScreen()
# used stack widget to use multi pages easily
widget = QtWidgets.QStackedWidget()
# made my window motionless
widget.setFixedSize(963, 802)
widget.addWidget(mainPageScreen)
mainScreenIndex = widget.currentIndex()

addScreen = AddBookScreen()
widget.addWidget(addScreen)
addScreenIndex = widget.currentIndex() + 1

deleteScreen = DeleteBookScreen()
widget.addWidget(deleteScreen)
deleteScreenIndex = widget.currentIndex() + 2

bookListScreen = BookListScreen()
widget.addWidget(bookListScreen)
listScreenIndex = widget.currentIndex() + 3

searchBookScreen = SearchBookScreen()
widget.addWidget(searchBookScreen)
searchScreenIndex = widget.currentIndex() + 4

rentBookScreen = RentBookScreen()
widget.addWidget(rentBookScreen)
rentScreenIndex = widget.currentIndex() + 5

rentedBookScreen = RentedBookScreen()
widget.addWidget(rentedBookScreen)
rentedScreenIndex = widget.currentIndex() + 6
widget.show()
try:
    sys.exit(app.exec_())
except FileNotFoundError as fe:
    print(fe)
