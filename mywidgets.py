from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QGridLayout, QLineEdit, QMessageBox
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QKeyEvent

# variables and functions
from utils import MINIMUM_HEIGHT, MINIMUM_WIDTH, SMALL_FONT_SIZE, BIG_FONT_SIZE, TEXT_MARGIN
from utils import  isNumOrDot, isEmpty, isValidNumber, convertToNumber
import math


class MyWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # setting window   
        self.cw = QWidget()
        self.vLayout = QVBoxLayout()

        self.cw.setLayout(self.vLayout)
        self.setCentralWidget(self.cw)

    # adjust size by itself and blocks the fullscreen button
    def adjustFixedSize(self):
        self.adjustSize()
        self.setFixedSize(self.width(), self.height())

    def addWidgetToVLayout(self, widget: QWidget):
        self.vLayout.addWidget(widget)

    
    def makeMsgBox(self):
        return QMessageBox()

# Texts
class Info(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configStyle()


    def configStyle(self):
        self.setStyleSheet(f'font-size: {SMALL_FONT_SIZE}')
        self.setAlignment(Qt.AlignmentFlag.AlignRight)

#Display
class Display(QLineEdit):
    # creating signals to create shortcuts 
    eqPressed = Signal()
    delPressed = Signal()
    clearPressed = Signal()
    
    inputPressed = Signal(str)
    OperatorPressed = Signal(str)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configStyle()

    def configStyle(self):
        self.setStyleSheet(f'font-size: {BIG_FONT_SIZE}px;')

        # making the display slightly bigger and with margins
        self.setMinimumHeight(MINIMUM_HEIGHT)
        self.setMinimumWidth(MINIMUM_WIDTH)

        self.setAlignment(Qt.AlignmentFlag.AlignRight)

        margins = [TEXT_MARGIN for _ in range(4)]
        self.setTextMargins(*margins)

        self.setPlaceholderText('0')

    def keyPressEvent(self, event: QKeyEvent):
        text = event.text().strip()
        k = event.key()
        KEYS = Qt.Key

        # lists with special keys and operators 
        isEnter = k in [KEYS.Key_Enter, KEYS.Key_Return, KEYS.Key_Equal]
        isDelete = k in [KEYS.Key_Delete, KEYS.Key_Backspace, KEYS.Key_D]
        isEsc = k in [KEYS.Key_Escape, KEYS.Key_C]

        isOperator = k in [KEYS.Key_Plus, KEYS.Key_Minus, KEYS.Key_Slash, KEYS.Key_Asterisk,
                           KEYS.Key_P]

        # treating the speacial keys
        if isEnter:
            self.eqPressed.emit()
            return event.ignore()
        if isDelete:
            self.delPressed.emit()
            return event.ignore()
        if isEsc:
            self.clearPressed.emit()
            return event.ignore()
        
        if isOperator:
            # replacing p os it turns into the power symbol 
            if text.lower() == 'p':
                text = '^'
            self.OperatorPressed.emit(text)


        # if its not any of the special keys that we are already treated just return 
        if isEmpty(text):
            return event.ignore()
        
        # if its just a number (or a dot) return with it
        if isNumOrDot(text):
            self.inputPressed.emit(text)
            return event.ignore()

# Buttons
class Button(QPushButton): 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configStyle()

    # changing the button without affecting the dark style 
    def configStyle(self):
        font = self.font()
        font.setPixelSize(SMALL_FONT_SIZE)
        self.setFont(font)

        self.setMinimumSize(75, 75)    

class ButtonGrid(QGridLayout):
    def __init__(self, display: Display, info: 'Info', window: MyWindow, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # window and widgets that are going to interact with the buttons
        self.window = window
        self.info = info 
        self.display = display

        # buttons
        self._grid_mask = [     
            ['C', '◀', '^', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['N',  '0', '.', '='],
        ]

        # equation variables
        self._left = None 
        self._right = None
        self._op = None 

        # setting text on top of the display
        self._equation = ''
        self._equationInitialValue = 'Welcome'
        self.equation = self._equationInitialValue

        # connecting signals
        self.display.delPressed.connect(self._backspace)
        self.display.eqPressed.connect(self._eq)
        self.display.clearPressed.connect(self._clear)
        
        self.display.inputPressed.connect(self._insertToDisplay)
        self.display.OperatorPressed.connect(self._ConfigLeftOperator)
        self._makeGrid()

    @property
    def equation(self):
        return self._equation 

    @equation.setter
    def equation(self, value):
        self._equation = value
        self.info.setText(value)

    def _makeGrid(self):
        for i, row in enumerate(self._grid_mask):
            for j, button_text in enumerate(row):
                button = Button(button_text)

                # giving color and custom slots to the "special" buttons (commands and operators
                if not isNumOrDot(button_text) and not isEmpty(button_text):
                    button.setProperty('cssClass', 'specialButton')
                    self._configSpecialButton(button) 
                
                self.addWidget(button, i, j)
                
                slot = self._makeSlot(self._insertToDisplay, button_text)
                
                self._connectButtonClicked(button,slot)

    def _configSpecialButton(self, button: Button):
        text = button.text()
        
        # connecting the slots with the special buttons
        if text == 'C':
            self._connectButtonClicked(button, self._clear)
        
        elif text == 'N':
            self._connectButtonClicked(button, self._invertNumber)
        
        elif text in '+-/*^':
            slot = self._makeSlot(self._ConfigLeftOperator, text)
            self._connectButtonClicked(button, slot)
        
        elif text == '=':
            self._connectButtonClicked(button, self._eq)
        
        elif text == '◀':
            self._connectButtonClicked(button, self._backspace)

    
    # internal function to easily connect buttons to slots
    def _makeSlot(self, func, *args, **kwargs):
        @Slot(bool)
        def realSlot(_):
            func(*args, **kwargs)
        return realSlot

    
    def _connectButtonClicked(self, button: Button, slot):
        button.clicked.connect(slot)

    #slots
    @Slot()
    def _insertToDisplay(self, text):
        # looking at how the result is going to be so we can treat it 
        # if its not valid we just return without putting it on the display
        newDisplayValue = self.display.text() + text
        
        if not isValidNumber(newDisplayValue):
            return
        
        self.display.insert(text)
        self.display.setFocus()

    @Slot()
    # function to make negative numbers
    def _invertNumber(self):
        displayText = self.display.text()
        if not isValidNumber(displayText):
            return
        number = convertToNumber(displayText) * - 1
        self.display.setText(str(number))

    @Slot()
    # function to reset everything
    def _clear(self):
        self._left = None 
        self._right = None
        self._op = None 

        self.equation = self._equationInitialValue

        self.display.clear()
        self.display.setFocus()

    @Slot()
    def _backspace(self):
        self.display.backspace()
        self.display.setFocus()

    @Slot()
    def _ConfigLeftOperator(self, text):
        # our first number on the left of the equation
        displayText = self.display.text()

        self.display.clear()

        if not isValidNumber(displayText) and self._left is None:
            self._showError('Nothing on display!!')
            return 

        # Whats inside display text goes to _left
        if self._left is None:
            self._left = float(displayText)

        self._op = text 
        self.equation = f'{self._left} {self._op} ??'
        self.display.setFocus()

    @Slot()
    def _eq(self):
        displayText = self.display.text()

        if not isValidNumber(displayText) or self._left is None:
            self._showError('equation incomplete!')
            return 

        self._right = float(displayText)
        self.equation = f'{self._left} {self._op} {self._right}'
        result = 'error'

        try:
            # reading the power symbol so it actually does power operations
            if '^' in self.equation and isinstance(self._left, int | float):
                result = math.pow(self._left, self._right)
            else:
                # else its just going to do a normal operation +*/-
                result = eval(self.equation)
        # potential errors that are going to show msgboxes
        except ZeroDivisionError:
            self._showError('You are trying to divide with zero!')
        except OverflowError:
            self._showError('Number too big to work with!!')

        self.display.clear()
        self.info.setText(f'{self.equation} = {result}')
        
        # _left is going to be the result so the user can still work with it
        self._left = result 
        self._right = None

        if result == 'error':
            self._left = None

        self.display.setFocus()
    
    #Message boxes
    def _makeDialog(self, text):
        msgBox = self.window.makeMsgBox()
        msgBox.setText(text)
        return msgBox

    def _showInfo(self,text):
        msgBox = self._makeDialog(text)
        msgBox.setWindowTitle('Info')
        msgBox.setIcon(msgBox.Icon.Information)
        msgBox.exec()
        self.display.setFocus()

    def _showError(self,text):
        msgBox = self._makeDialog(text)
        msgBox.setWindowTitle('Error')
        msgBox.setIcon(msgBox.Icon.Warning)
        msgBox.exec()
        self.display.setFocus()

