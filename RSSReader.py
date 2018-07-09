"""RSS Reader

This is a simple RSS Reader. Given a url to an RSS feed it populates a table with the top articles from the feed.
Clicking an item in the table brings up a description of the article and double clicking opens the article in a webviewer.
"""
import sys
from PyQt5.QtWidgets import QFrame, QPushButton, QTableView, QAbstractItemView, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QTextEdit, QGridLayout, QApplication
from PyQt5.QtCore import pyqtSlot, QAbstractTableModel, QUrl, QVariant, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
import feedparser


class RssModel(QAbstractTableModel):
    """This is the model that handles the table data from the QTableView."""

    def __init__(self, datain, parent=None):
        """Initialization of the RssModel class.
        Utilizes QAbstractModel's init function and initializes the arraydata list.
        """
        QAbstractTableModel.__init__(self, parent)
        self.arraydata = datain

    def rowCount(self, parent):
        """Returns the number of rows in arraydata"""
        return len(self.arraydata)

    def columnCount(self, parent):
        """Returns the number of columns in arraydata"""
        if len(self.arraydata) > 0:
            return len(self.arraydata[0]) - 2
        return 0

    def data(self, index, role=Qt.DisplayRole):
        """Returns data for display by the table.
        Only returns data for columns 1 and 2 so the table only displays the Title and Website columns.
        """
        if not index.isValid():
            return QVariant()
        elif index.column() < 2:
            if role == Qt.DisplayRole:
                return QVariant(self.arraydata[index.row()][index.column()])
            return QVariant()
        return QVariant()

    def update(self, datain):
        """Sets the model data to the most recent data from the frame."""
        self.arraydata = datain
        self.layoutChanged.emit()

    def summary(self, index):
        """Returns the summary of the article at the given index."""
        return self.arraydata[index.row()][2]

    def url(self, index):
        """Returns the url of the article at the given index."""
        return self.arraydata[index.row()][3]

    def headerData(self, section, orientation, role):
        """Handles the header data for the table."""
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return ["Title", "Website"][section]
            if orientation == Qt.Vertical:
                return None


class RssFrame(QFrame):

    def __init__(self):
        """Initialization of the RssFrame class."""
        super().__init__()

        self.data = []

        self.resize(1200, 800)
        self.setWindowTitle('RSS Reader')

        self.urlButton = QPushButton("Get Feed")
        self.urlButton.clicked.connect(self.on_button_click)

        self.rssTable = QTableView()
        self.rssTable.clicked.connect(self.on_click)
        self.rssTable.doubleClicked.connect(self.on_double_click)
        self.rssModel = RssModel(self.data)
        self.rssTable.setModel(self.rssModel)
        self.rssTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.header = self.rssTable.horizontalHeader()
        self.header.setSectionResizeMode(QHeaderView.Stretch)

        feedURL = QLabel('Feed URL:')
        self.feedURLEdit = QLineEdit()
        self.browser = QWebEngineView()

        self.description = QTextEdit()
        self.description.setReadOnly(True)

        grid = QGridLayout()
        grid.setSpacing(10)

        sublayout = QHBoxLayout()
        sublayout.addWidget(feedURL)
        sublayout.addWidget(self.feedURLEdit)
        sublayout.addWidget(self.urlButton)

        grid.addLayout(sublayout, 1, 0, 1, 3)
        grid.addWidget(self.rssTable, 2, 0, 1, 1)
        grid.addWidget(self.browser, 2, 1, 1, 2)
        grid.addWidget(self.description, 3, 0, 1, 3)

        self.setLayout(grid)

        self.show()

    @pyqtSlot()
    def on_button_click(self):
        """Handles the Get Feed button.
        When the Get Feed button is pressed feedparser parses the RSS feed from the URL given.
        After feedparser handles the data we iterate through the data, extract the title, website, link, and summary
        of each article, and append that data as a new list in our 2D data list. Finally, the new data is sent to
        the table model for display.
        """
        rss = self.feedURLEdit.text()
        feed = feedparser.parse(str(rss))

        website = feed["feed"]["title"]
        for key in feed["entries"]:
            title = key["title"]
            link = key["link"]
            summary = key["summary"]
            self.data.append([title, website, summary, link])

        self.rssModel.update(self.data)
        self.rssTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    @pyqtSlot()
    def on_click(self):
        """Handles clicks to entries of the rss table.
        When an entry of the table is clicked the index of the clicked entry is retrieved. The retrieved index
        is then used to obtain the summary of the selected entry which is then wrapped in html tags for display
        and displayed in the summary text box.
        """
        index = self.rssTable.selectedIndexes()[0]
        html = "<html><body>%s</body></html>" % self.rssModel.summary(index)
        self.description.setHtml(html)

    @pyqtSlot()
    def on_double_click(self):
        """Handles double clicks to entries of the rss table.
        When an entry of the table is double clicked the index of the clicked entry is retrieved, the url is extracted,
        and the url is loaded in the QWebViewer.
        """
        index = self.rssTable.selectedIndexes()[0]
        url = QUrl(self.rssModel.url(index))
        self.browser.load(url)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    frame = RssFrame()
    sys.exit(app.exec_())
