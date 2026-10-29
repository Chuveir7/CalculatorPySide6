import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from mywidgets import MyWindow, ButtonGrid, Info, Display
from utils import ICON_PATH

from style import setupTheme

# setting app and hierarchy
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    setupTheme(app)

    window.setWindowTitle('Calculator')
    icon = QIcon(str(ICON_PATH))
    window.setWindowIcon(icon)

    info = Info()
    window.addWidgetToVLayout(info)
    
    display = Display()
    window.addWidgetToVLayout(display)
   
    bgrid = ButtonGrid(display=display, info=info, window=window) 
    window.vLayout.addLayout(bgrid)
    
    window.adjustFixedSize()
    window.show()
    app.exec()