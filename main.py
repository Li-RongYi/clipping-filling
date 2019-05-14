from ui import *
import sys
from paintboard import PaintBoard

class drawing(Ui_MainWindow):
    def __init__(self,MainWindow):
        super().setupUi(MainWindow)
        self.paintBoard = PaintBoard()
        self.horizontalLayout.addWidget(self.paintBoard)
        self.connect()

    def connect(self):
        self.pushButton.clicked.connect(self.paintBoard.mouse)
        self.pushButton_2.clicked.connect(self.paintBoard.clear)
        self.pushButton_3.clicked.connect(self.paintBoard.convexPolygon)
        self.pushButton_4.clicked.connect(self.paintBoard.polygon)
        self.pushButton_5.clicked.connect(self.paintBoard.sutherlandHodgman)
        self.pushButton_6.clicked.connect(self.paintBoard.vertexSorting)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = drawing(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

