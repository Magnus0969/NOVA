from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QWidget, QStackedWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy, QLabel, QFrame
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QFont, QTextCharFormat, QTextBlockFormat, QPixmap
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

# Set assistant name directly in the code since .env file is not accessible
Assistant_name = "NOVA"
current_dir = os.getcwd()
old_chat_msgs = ""
temp_dir_path = rf"{current_dir}\Frontend\Files"
graphics_dir_path = rf"{current_dir}\Frontend\Graphics"

def AnswerModifier(answer):
    lines= answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = "\n".join(non_empty_lines)
    return modified_answer

def QueryModifier(query):
    new_query = query.lower().strip()
    query_words = new_query.split()
    question_words= ["who", "what", "when", "where", "why", "how", "which","who's","what's","when's","where's","why's","how's","whose","whose's",
                     "can you", "could you", "would you", "is it", "are you", "do you", "has it", "have you", "had you", 
                     "may I", "might I", "shall I", "should I", "will I", "would I", "could I", "can I"]
    
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ["?", "!", "."]:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    
    else:
        if query_words[-1][-1] in ["?", "!", "."]:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    
    return new_query.capitalize()

def SetMicStatus(command):
    with open(rf"{temp_dir_path}\Mic.data", "w", encoding="utf-8") as file:
        file.write(command)

def GetMicStatus():
    with open(rf"{temp_dir_path}\Mic.data", "r", encoding="utf-8") as file:
        Status= file.read()
    return Status

def SetAssistantStatus(status):
    with open(rf"{temp_dir_path}\Status.data", "w", encoding="utf-8") as file:
        file.write(status)

def GetAssistantStatus():
    with open(rf"{temp_dir_path}\Status.data", "r", encoding="utf-8") as file:
        Status= file.read()
    return Status

def GraphicsDirectoryPath(filename):
    path=rf"{graphics_dir_path}\{filename}"
    return path

def TempDirectoryPath(filename):
    path= rf"{temp_dir_path}\{filename}"
    return path

def MicButtoninitialed():
    SetMicStatus("False")

def MicButtonClosed():
    SetMicStatus("True")

def ShowTextToScreen(text):
    with open(rf"{temp_dir_path}\Responses.data", "w", encoding="utf-8") as file:
        file.write(text)

class ChatSection(QWidget):
    
    def __init__(self):
        super(ChatSection,self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 40, 40, 80)
        layout.setSpacing(10)
        
        # Enhanced chat display
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QTextEdit.NoFrame)
        self.chat_text_edit.setStyleSheet("""
            background-color: #121212;
            border-radius: 12px;
            padding: 15px;
            color: #e0e0e0;
        """)
        layout.addWidget(self.chat_text_edit)
        
        # Set the overall widget style
        self.setStyleSheet("background-color: #000000;")
        
        # Configure layout properties
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        layout.setStretch(1, 1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        
        # Configure text appearance
        text_color = QColor(120, 170, 255)  # Modern blue color
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)
        
        # Setup animated GIF with improved positioning
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none; margin-bottom: 20px;")
        movie = QMovie(GraphicsDirectoryPath("Jarvis.gif"))
        max_gif_size_W = 480
        max_gif_size_H = 270
        movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()
        
        # Status label with improved styling
        self.label = QLabel("")
        self.label.setStyleSheet("""
            color: #3498db; 
            font-size: 16px; 
            margin-right: 195px; 
            border: none; 
            margin-top: -30px;
            font-weight: bold;
        """)
        self.label.setAlignment(Qt.AlignRight)
        
        # Add widgets to layout with better spacing
        layout.addWidget(self.gif_label)
        layout.addWidget(self.label)
        
        # Set font for chat text
        font = QFont("Segoe UI", 13)
        self.chat_text_edit.setFont(font)
        
        # Setup timer for message updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)
        
        # Install event filter
        self.chat_text_edit.viewport().installEventFilter(self)
        
        # Custom scrollbar styling
        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: #121212;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
                      
            QScrollBar::handle:vertical {
                background: #3498db;
                min-height: 20px;
                border-radius: 5px;
            }
                      
            QScrollBar::add-line:vertical {
                background: none;
                height: 0px;
            }
            
            QScrollBar::sub-line:vertical {
                background: none;
                height: 0px;
            }
            
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
                color: none;
            }
                      
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            
            QTextEdit {
                border: 1px solid #2c3e50;
                border-radius: 10px;
            }
        """)

    def loadMessages(self):
        global old_chat_msgs

        with open(TempDirectoryPath('Responses.data'), "r", encoding="utf-8") as file:
            msgs= file.read()

            if None == msgs:
                pass

            elif len(msgs)<=1:
                pass

            elif str(old_chat_msgs)==str(msgs):
                pass

            else:
                self.addMessage(message=msgs,color="White")
                old_chat_msgs= msgs
    
    def SpeechRecogText(self):
    
        with open(TempDirectoryPath('Status.data'), "r", encoding="utf-8") as file:
            msgs= file.read()
            self.label.setText(msgs)
    
    def load_icon(self,path,width=60,height=60):
        pixmap= QPixmap(path)
        new_pixmap= pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)
    
    def toggle_icon(self, event= None):
        
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('voice.png'), 60, 60)
            MicButtoninitialed()
        
        else:
            self.load_icon(GraphicsDirectoryPath('mic.png'), 60, 60)
            MicButtonClosed()
        
        self.toggled= not self.toggled
    
    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        format_m = QTextBlockFormat()
        format_m.setTopMargin(15)  # Increased margin for better readability
        format_m.setLeftMargin(15)
        format.setForeground(QColor(color))
        
        # Set font properties
        font = QFont("Segoe UI", 13)
        format.setFont(font)
        
        cursor.setCharFormat(format)
        cursor.setBlockFormat(format_m)
        cursor.insertText(message + '\n')
        self.chat_text_edit.setTextCursor(cursor)
        # Scroll to the bottom
        self.chat_text_edit.verticalScrollBar().setValue(
            self.chat_text_edit.verticalScrollBar().maximum()
        )

class InitialScreen(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Enhanced GIF display
        gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath("Jarvis.gif"))
        gif_label.setMovie(movie)
        max_gif_size_H = int(screen_width/16*9)
        movie.setScaledSize(QSize(screen_width, max_gif_size_H))
        gif_label.setAlignment(Qt.AlignCenter)
        movie.start()
        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Improved microphone button
        self.icon_label = QLabel()
        pixmap = QPixmap(GraphicsDirectoryPath("Mic_on.png"))
        new_pixmap = pixmap.scaled(70, 70)  # Slightly larger icon
        self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(170, 170)  # Larger clickable area
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("""
            background-color: #121212;
            border-radius: 85px;
            padding: 15px;
            border: 2px solid #3498db;
        """)
        
        self.toggled = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon
        
        # Enhanced status label
        self.label = QLabel("")
        self.label.setStyleSheet("""
            color: #3498db; 
            font-size: 18px; 
            margin-bottom: 20px;
            font-weight: bold;
        """)
        
        # Add widgets to layout with better spacing
        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 100)
        
        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: #000000;")
        
        # Setup timer for status updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

    def SpeechRecogText(self):
        with open(TempDirectoryPath('Status.data'), "r", encoding="utf-8") as file:
            msgs= file.read()
            self.label.setText(msgs)
    
    def load_icon(self,path,width=60,height=60):
        pixmap= QPixmap(path)
        new_pixmap= pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)
    
    def toggle_icon(self, event= None):

        if self.toggled:
            self.load_icon(GraphicsDirectoryPath("Mic_on.png"),60,60)
            MicButtoninitialed()
        
        else:
            self.load_icon(GraphicsDirectoryPath("Mic_off.png"),60,60)
            MicButtonClosed()
        
        self.toggled= not self.toggled
    
class ManageScreen(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        # Create main layout with better spacing
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Create a modern header
        header = QLabel("Chat Interface")
        header.setStyleSheet("""
            color: #3498db;
            font-size: 22px;
            font-weight: bold;
            padding: 10px;
            border-bottom: 1px solid #3498db;
        """)
        layout.addWidget(header)
        
        # Add the chat section with proper spacing
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            background-color: #000000;
            border-radius: 15px;
        """)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)

class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.initUI()
        self.current_screen = None
        self.stacked_widget = stacked_widget
    
    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Enhanced home button
        home_button = QPushButton()
        home_icon = QIcon(GraphicsDirectoryPath("Home.png"))
        home_button.setIcon(home_icon)
        home_button.setText(" Home")
        home_button.setStyleSheet("""
            height: 40px; 
            line-height: 40px; 
            background-color: #2c3e50; 
            color: white;
            border-radius: 5px;
            padding: 0 15px;
            font-weight: bold;
        """)

        # Enhanced chat button
        msg_button = QPushButton()
        msg_icon = QIcon(GraphicsDirectoryPath("Chats.png"))
        msg_button.setIcon(msg_icon)
        msg_button.setText(" Chat")
        msg_button.setStyleSheet("""
            height: 40px; 
            line-height: 40px; 
            background-color: #2c3e50; 
            color: white;
            border-radius: 5px;
            padding: 0 15px;
            font-weight: bold;
        """)

        # Window control buttons
        minimize_button = QPushButton()
        minimize_icon = QIcon(GraphicsDirectoryPath("Minimize2.png"))
        minimize_button.setIcon(minimize_icon)
        minimize_button.setStyleSheet("""
            background-color: #3498db;
            border-radius: 5px;
            padding: 5px;
        """)
        minimize_button.clicked.connect(self.minimizeWindow)

        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(GraphicsDirectoryPath("Maximize.png"))
        self.restore_icon = QIcon(GraphicsDirectoryPath("Minimize.png"))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet("""
            background-color: #2ecc71;
            border-radius: 5px;
            padding: 5px;
        """)
        self.maximize_button.clicked.connect(self.maximizeWindow)
        
        close_button = QPushButton()
        close_icon = QIcon(GraphicsDirectoryPath("Close.png"))
        close_button.setIcon(close_icon)
        close_button.setStyleSheet("""
            background-color: #e74c3c;
            border-radius: 5px;
            padding: 5px;
        """)
        close_button.clicked.connect(self.closeWindow)

        # Updated separator
        line_frame = QFrame()
        line_frame.setFixedHeight(1)
        line_frame.setFrameShape(QFrame.HLine)
        line_frame.setFrameShadow(QFrame.Sunken)
        line_frame.setStyleSheet("background-color: #3498db;")

        # Enhanced title label
        title_label = QLabel(f"{str(Assistant_name)}")
        title_label.setStyleSheet("""
            color: #3498db; 
            font-size: 20px;
            font-weight: bold;
            margin-left: 10px;
        """)
        
        # Connect button actions
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        msg_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        
        # Add widgets to layout
        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(msg_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)
        
        # Set up dragging
        self.draggable = True
        self.offset = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(18, 18, 18))  # Dark background
        super().paintEvent(event)
    
    def minimizeWindow(self):
        self.parent().showMinimized()
    
    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)
    
    def closeWindow(self):
        self.parent().close()
    
    def mousePressEvent(self, event):
        if self.draggable:
            self.offset= event.pos()
    
    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos= event.globalPos() - self.offset
            self.parent().move(new_pos)
    
    def showMessageScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()
        
        msg_screen= ManageScreen(self)
        layout= self.parent().layout()
        if layout is not None:
            layout.addWidget(msg_screen)
        self.current_screen= msg_screen
    
    def showInitialScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()
        
        initial_screen= InitialScreen(self)
        layout= self.parent().layout()
        if layout is not None:
            layout.addWidget(initial_screen)
        self.current_screen= initial_screen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()
    
    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        # Create central widget with proper styling
        central_widget = QWidget()
        central_widget.setStyleSheet("""
            background-color: #000000;
            border-radius: 10px;
        """)
        
        # Create stacked widget for screen management
        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        message_screen = ManageScreen()

        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        
        # Setup main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(stacked_widget)
        
        # Set window properties
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
                border: 1px solid #3498db;
                border-radius: 10px;
            }
        """)
        
        # Create and set the top bar
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(central_widget)

def GraphicUserInterface():
    app= QApplication(sys.argv)
    window= MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__== "__main__":
    GraphicUserInterface()