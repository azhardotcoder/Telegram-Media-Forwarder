import sys
import json
import asyncio
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox,
                           QCheckBox, QMessageBox, QProgressBar, QTabWidget,
                           QScrollArea, QFrame, QStyleFactory, QDialog, QRadioButton,
                           QFormLayout, QHBoxLayout, QAction)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QMetaType
from PyQt5.QtGui import QFont, QIcon
from telethon.sync import TelegramClient
from telethon import errors, events, types
import os
import time

# Fix for PyQt5 deprecation warnings
import sip
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)

class OTPDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Verification Code')
        self.setModal(True)
        self.setup_ui()
        self.setFixedSize(400, 250)  # Fixed size for better appearance

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)  # Add spacing between elements
        
        # Title with icon
        title_layout = QHBoxLayout()
        icon_label = QLabel("🔐")
        icon_label.setStyleSheet("font-size: 24px;")
        title_label = QLabel("Telegram Verification")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
        """)
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Info label with better formatting
        info_label = QLabel("Please enter the verification code sent to your\nTelegram app")
        info_label.setStyleSheet("""
            color: #34495e;
            font-size: 13px;
            margin: 10px 0;
        """)
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # OTP input with better styling
        self.otp_input = QLineEdit()
        self.otp_input.setPlaceholderText('Enter 5-digit code')
        self.otp_input.setMaxLength(5)
        self.otp_input.setAlignment(Qt.AlignCenter)
        self.otp_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                letter-spacing: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(self.otp_input)
        
        # Buttons with better styling
        button_layout = QHBoxLayout()
        
        self.verify_button = QPushButton('Verify')
        self.verify_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.verify_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.verify_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        # Add some padding to the dialog
        main_widget = QWidget()
        main_widget.setLayout(layout)
        main_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                padding: 20px;
            }
        """)
        
        dialog_layout = QVBoxLayout()
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(main_widget)
        self.setLayout(dialog_layout)

    def get_code(self):
        return self.otp_input.text().strip()

class LoadingDialog(QDialog):
    def __init__(self, message="Please wait...", parent=None):
        super().__init__(parent)
        self.setWindowTitle('Loading')
        self.setModal(True)
        self.setupUi(message)
        
    def setupUi(self, message):
        layout = QVBoxLayout()
        
        # Loading animation container
        loading_container = QFrame()
        loading_container.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        loading_layout = QVBoxLayout()
        
        # Loading spinner (using text-based animation)
        self.spinner_label = QLabel("⌛")
        self.spinner_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #3498db;
            }
        """)
        self.spinner_label.setAlignment(Qt.AlignCenter)
        loading_layout.addWidget(self.spinner_label)
        
        # Message label
        self.message_label = QLabel(message)
        self.message_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                margin-top: 10px;
            }
        """)
        self.message_label.setAlignment(Qt.AlignCenter)
        loading_layout.addWidget(self.message_label)
        
        # Progress text
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        self.progress_label.setAlignment(Qt.AlignCenter)
        loading_layout.addWidget(self.progress_label)
        
        loading_container.setLayout(loading_layout)
        layout.addWidget(loading_container)
        
        self.setLayout(layout)
        self.setFixedSize(300, 150)
        
        # Setup animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_spinner)
        self.animation_timer.start(100)
        self.spinner_frames = ["⌛", "⏳"]
        self.current_frame = 0
        
    def update_spinner(self):
        self.current_frame = (self.current_frame + 1) % len(self.spinner_frames)
        self.spinner_label.setText(self.spinner_frames[self.current_frame])
        
    def update_message(self, message):
        self.message_label.setText(message)
        
    def update_progress(self, progress):
        self.progress_label.setText(progress)
        
    def closeEvent(self, event):
        self.animation_timer.stop()
        super().closeEvent(event)

class ChatListThread(QThread):
    update_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)
    code_request_signal = pyqtSignal()
    login_success_signal = pyqtSignal()
    status_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(str)

    def __init__(self, api_id, api_hash, phone, load_chats=False):
        super().__init__()
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.client = None
        self.code = None
        self.code_ready = asyncio.Event()
        self.verification_timeout = 60
        self.load_chats = load_chats

    def set_verification_code(self, code):
        """Set the verification code and signal that it's ready"""
        self.code = code
        self.code_ready.set()  # Signal that the code is ready

    async def initialize_client(self):
        """Initialize client with better connection settings"""
        session_name = f'session_{self.phone}'
        
        # Create new session
        self.client = TelegramClient(
            session_name,
            self.api_id,
            self.api_hash,
            device_model="Desktop",
            system_version="Windows",
            app_version="1.0",
            retry_delay=1
        )
        await self.client.connect()
        return await self.client.is_user_authorized()

    async def get_chats(self):
        try:
            # Initialize client
            self.status_signal.emit("Connecting to Telegram...")
            self.progress_signal.emit("Step 1/3: Initializing connection...")
            
            is_authorized = await self.initialize_client()
            
            if not is_authorized:
                self.status_signal.emit("Requesting verification code...")
                self.progress_signal.emit("Step 2/3: Verification...")
                
                await self.client.send_code_request(self.phone)
                self.code_request_signal.emit()
                
                try:
                    await asyncio.wait_for(self.code_ready.wait(), timeout=self.verification_timeout)
                except asyncio.TimeoutError:
                    raise Exception("Verification timeout")
                
                if not self.code:
                    raise Exception("Verification cancelled")
                
                try:
                    self.status_signal.emit("Signing in...")
                    self.progress_signal.emit("Step 3/3: Authentication...")
                    await self.client.sign_in(self.phone, self.code)
                    self.login_success_signal.emit()
                except Exception as e:
                    raise Exception(f"Login failed: {str(e)}")
            else:
                self.status_signal.emit("Already authorized!")
                self.login_success_signal.emit()

            # Only load chats if specifically requested
            if self.load_chats:
                await self.load_chat_list()
            else:
                # Just disconnect if we're only doing login
                if self.client:
                    await self.client.disconnect()

        except Exception as e:
            self.error_signal.emit(str(e))
            if self.client:
                await self.client.disconnect()

    async def load_chat_list(self):
        """Separate method for loading chats"""
        try:
            self.status_signal.emit("Loading chats...")
            self.progress_signal.emit("Loading chat list...")
            
            dialogs = await self.client.get_dialogs()
            chat_list = []
            
            for dialog in dialogs:
                chat_type = "Unknown"
                chat_title = getattr(dialog.entity, 'title', None) or getattr(dialog.entity, 'first_name', 'Unknown')
                
                if isinstance(dialog.entity, types.User):
                    chat_type = "Private"
                elif isinstance(dialog.entity, (types.Chat, types.ChatForbidden)):
                    chat_type = "Group"
                elif isinstance(dialog.entity, types.Channel):
                    chat_type = "Channel"

                chat_info = {
                    'id': dialog.id,
                    'title': chat_title,
                    'type': chat_type,
                    'unread_count': dialog.unread_count
                }
                chat_list.append(chat_info)
                
            self.update_signal.emit(chat_list)
            self.status_signal.emit("Chats loaded successfully!")
            
        except Exception as e:
            self.error_signal.emit(f"Error loading chats: {str(e)}")
        finally:
            if self.client:
                await self.client.disconnect()

    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.get_chats())
        except Exception as e:
            self.error_signal.emit(f"Runtime error: {str(e)}")
        finally:
            loop.close()

class ForwarderThread(QThread):
    message_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    reconnect_signal = pyqtSignal()

    def __init__(self, api_id, api_hash, phone, source_id, dest_id, filters, forward_existing=True):
        super().__init__()
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.source_id = source_id
        self.dest_id = dest_id
        self.filters = filters
        self.is_running = True
        self.client = None
        self.retry_count = 0
        self.max_retries = 5
        self.reconnect_interval = 5
        self.forward_existing = forward_existing
        self.messages_processed = 0

    async def connect_client(self):
        try:
            if self.client and self.client.is_connected():
                return True

            self.client = TelegramClient(
                f'session_{self.phone}',
                self.api_id,
                self.api_hash,
                device_model="Desktop",
                system_version="Windows",
                app_version="1.0",
                retry_delay=1
            )
            await self.client.connect()
            
            if not await self.client.is_user_authorized():
                self.error_signal.emit("Please login first!")
                return False

            return True
        except Exception as e:
            self.error_signal.emit(f"Connection error: {str(e)}")
            return False

    async def forward_existing_messages(self):
        try:
            self.message_signal.emit("📥 Starting to copy messages...")
            
            # Get messages from source chat
            messages = []
            async for message in self.client.iter_messages(self.source_id, limit=None):
                if not self.is_running:
                    break
                    
                should_forward = False
                message_type = "Unknown"
                
                if message.text and self.filters['text']:
                    should_forward = True
                    message_type = "Text"
                elif message.media:
                    if hasattr(message.media, 'photo') and self.filters['media']:
                        should_forward = True
                        message_type = "Photo"
                    elif hasattr(message.media, 'document'):
                        if self.filters['media'] and getattr(message.media.document, 'mime_type', '').startswith('video/'):
                            should_forward = True
                            message_type = "Video"
                        elif self.filters['documents']:
                            should_forward = True
                            message_type = "Document"
                
                if should_forward:
                    messages.append((message, message_type))
            
            total_messages = len(messages)
            self.message_signal.emit(f"Found {total_messages} messages to copy...")
            
            # Copy messages in reverse order to maintain chronological order
            for i, (message, message_type) in enumerate(reversed(messages)):
                if not self.is_running:
                    break
                    
                try:
                    if message.text:
                        await self.client.send_message(self.dest_id, message.text)
                    if message.media:
                        await self.client.send_file(self.dest_id, message.media)
                    
                    self.messages_processed += 1
                    progress = int((self.messages_processed / total_messages) * 100)
                    self.progress_signal.emit(progress)
                    self.message_signal.emit(f"✅ Copied {message_type} message ({self.messages_processed}/{total_messages})")
                except Exception as send_error:
                    self.error_signal.emit(f"Error copying message: {str(send_error)}")
                
                # Add a small delay to avoid flooding
                await asyncio.sleep(0.5)
            
            self.message_signal.emit("✨ Finished copying messages!")
            
        except Exception as e:
            self.error_signal.emit(f"Error copying messages: {str(e)}")

    async def forward_messages(self):
        while self.is_running:
            try:
                if not await self.connect_client():
                    if self.retry_count >= self.max_retries:
                        self.error_signal.emit("Max reconnection attempts reached. Please restart the application.")
                        break
                    self.retry_count += 1
                    self.message_signal.emit(f"Reconnecting... Attempt {self.retry_count}/{self.max_retries}")
                    await asyncio.sleep(self.reconnect_interval)
                    continue

                self.retry_count = 0

                try:
                    source_entity = await self.client.get_entity(self.source_id)
                    dest_entity = await self.client.get_entity(self.dest_id)
                    
                    source_name = getattr(source_entity, 'title', None) or getattr(source_entity, 'first_name', 'Unknown') or str(self.source_id)
                    dest_name = getattr(dest_entity, 'title', None) or getattr(dest_entity, 'first_name', 'Unknown') or str(self.dest_id)
                    
                    self.message_signal.emit(f"Connected to source: {source_name}")
                    self.message_signal.emit(f"Connected to destination: {dest_name}")

                    if self.forward_existing:
                        await self.forward_existing_messages()
                        self.is_running = False
                        break

                except Exception as e:
                    self.error_signal.emit(f"Error validating chat IDs: {str(e)}")
                    continue

            except ConnectionError:
                if self.is_running:
                    self.message_signal.emit("📡 Connection lost. Attempting to reconnect...")
                    continue
            except Exception as e:
                self.error_signal.emit(f"Error in forward_messages: {str(e)}")
                if self.is_running:
                    await asyncio.sleep(self.reconnect_interval)
                    continue

        if self.client:
            await self.client.disconnect()

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.forward_messages())

    def stop(self):
        self.is_running = False

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Telegram Login')
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # API ID input
        self.api_id_input = QLineEdit()
        self.api_id_input.setPlaceholderText('Enter API ID')
        form_layout.addRow('API ID:', self.api_id_input)

        # API Hash input
        self.api_hash_input = QLineEdit()
        self.api_hash_input.setPlaceholderText('Enter API Hash')
        form_layout.addRow('API Hash:', self.api_hash_input)

        # Phone number input
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText('Enter phone number (with country code)')
        form_layout.addRow('Phone:', self.phone_input)

        # Add form to main layout
        layout.addLayout(form_layout)

        # Info text
        info_text = QLabel("To get API ID and Hash:\n1. Go to https://my.telegram.org\n2. Login with your phone number\n3. Go to 'API Development tools'\n4. Create a new application")
        info_text.setStyleSheet("QLabel { color: gray; }")
        layout.addWidget(info_text)

        # Buttons
        button_box = QHBoxLayout()
        self.login_button = QPushButton('Login')
        self.login_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.reject)
        
        button_box.addWidget(self.login_button)
        button_box.addWidget(self.cancel_button)
        layout.addLayout(button_box)

        self.setLayout(layout)

    def get_credentials(self):
        return {
            'api_id': self.api_id_input.text().strip(),
            'api_hash': self.api_hash_input.text().strip(),
            'phone': self.phone_input.text().strip()
        }

class TelegramForwarderUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_id = None
        self.api_hash = None
        self.phone = None
        self.chat_list = []
        self.original_chat_list = []
        self.filtered_source_chats = []
        self.filtered_dest_chats = []
        
        # Initialize UI first
        self.init_ui()
        
        # Try to load saved credentials and auto-login
        self.load_and_auto_login()

    def init_ui(self):
        self.setWindowTitle('Telegram Media Forwarder Pro')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            * {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QMainWindow {
                background-color: #ffffff;
            }
            QLabel {
                color: #2c3e50;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                min-height: 30px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #3498db;
            }
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
            }
            QFrame {
                border-radius: 5px;
            }
            QTabWidget::pane {
                border: none;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                color: #2c3e50;
                padding: 10px 20px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QCheckBox {
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QStatusBar {
                background-color: #f8f9fa;
                color: #2c3e50;
            }
        """)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Status Panel
        status_panel = QFrame()
        status_panel.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                padding: 10px;
                margin-bottom: 10px;
            }
        """)
        status_layout = QHBoxLayout()

        # Status indicators with better styling
        self.login_status = QPushButton("⭕ Not Logged In")
        self.login_status.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                padding: 8px 15px;
                text-align: left;
            }
        """)
        self.chat_status = QPushButton("⭕ Chats Not Loaded")
        self.chat_status.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                padding: 8px 15px;
                text-align: left;
            }
        """)
        self.forward_status = QPushButton("⭕ Forwarding Inactive")
        self.forward_status.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                padding: 8px 15px;
                text-align: left;
            }
        """)

        status_layout.addWidget(self.login_status)
        status_layout.addWidget(self.chat_status)
        status_layout.addWidget(self.forward_status)
        status_panel.setLayout(status_layout)
        layout.addWidget(status_panel)

        # Tabs
        tabs = QTabWidget()
        
        # Login tab (New)
        login_tab = QWidget()
        login_layout = QVBoxLayout()
        
        # Login form
        login_group = QFrame()
        login_group.setStyleSheet("QFrame { background-color: #f8f9fa; padding: 15px; }")
        login_form = QFormLayout()

        # API ID input
        self.api_id_input = QLineEdit()
        self.api_id_input.setPlaceholderText('Enter API ID')
        login_form.addRow('API ID:', self.api_id_input)

        # API Hash input
        self.api_hash_input = QLineEdit()
        self.api_hash_input.setPlaceholderText('Enter API Hash')
        login_form.addRow('API Hash:', self.api_hash_input)

        # Phone number input
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText('Enter phone number (with country code)')
        login_form.addRow('Phone:', self.phone_input)

        # Login button
        self.login_btn = QPushButton('Login')
        self.login_btn.clicked.connect(self.handle_login)
        
        # Info text with better instructions
        info_text = QLabel(
            "To get API ID and Hash:\n"
            "1. Go to https://my.telegram.org\n"
            "2. Login with your phone number\n"
            "3. Go to 'API Development tools'\n"
            "4. Create a new application\n\n"
            "Phone number format: +CountryCodeNumber\n"
            "Example: +919876543210"
        )
        info_text.setStyleSheet("QLabel { color: gray; }")

        login_form.addRow(info_text)
        login_form.addRow(self.login_btn)
        
        login_group.setLayout(login_form)
        login_layout.addWidget(login_group)
        login_tab.setLayout(login_layout)
        
        tabs.addTab(login_tab, "Login")

        # Setup tab
        setup_tab = QWidget()
        setup_layout = QVBoxLayout()
        
        # Phone number section
        phone_group = QFrame()
        phone_group.setStyleSheet("QFrame { background-color: #f8f9fa; padding: 15px; }")
        phone_layout = QVBoxLayout()
        
        phone_label = QLabel(f'Phone Number: {self.phone}')
        phone_layout.addWidget(phone_label)
        
        self.auth_label = QLabel('Checking registration status...')
        self.auth_label.setStyleSheet("font-weight: bold;")
        phone_layout.addWidget(self.auth_label)
        
        self.load_chats_btn = QPushButton('Load Chats')
        self.load_chats_btn.clicked.connect(self.load_chats)
        self.load_chats_btn.setEnabled(False)
        phone_layout.addWidget(self.load_chats_btn)
        
        phone_group.setLayout(phone_layout)
        setup_layout.addWidget(phone_group)

        # Chat selection section
        chat_group = QFrame()
        chat_group.setStyleSheet("QFrame { background-color: #f8f9fa; padding: 15px; margin-top: 10px; }")
        chat_layout = QHBoxLayout()

        # Source selection
        source_layout = QVBoxLayout()
        source_layout.addWidget(QLabel('Source Chat:'))
        
        # Source category filters
        source_filter_layout = QHBoxLayout()
        self.source_all_radio = QRadioButton('All')
        self.source_private_radio = QRadioButton('Private')
        self.source_group_radio = QRadioButton('Groups')
        self.source_channel_radio = QRadioButton('Channels')
        
        self.source_all_radio.setChecked(True)
        self.source_all_radio.toggled.connect(self.filter_source_by_category)
        self.source_private_radio.toggled.connect(self.filter_source_by_category)
        self.source_group_radio.toggled.connect(self.filter_source_by_category)
        self.source_channel_radio.toggled.connect(self.filter_source_by_category)
        
        source_filter_layout.addWidget(self.source_all_radio)
        source_filter_layout.addWidget(self.source_private_radio)
        source_filter_layout.addWidget(self.source_group_radio)
        source_filter_layout.addWidget(self.source_channel_radio)
        source_layout.addLayout(source_filter_layout)
        
        self.source_combo = QComboBox()
        self.source_combo.setPlaceholderText('Select source chat')
        source_layout.addWidget(self.source_combo)
        chat_layout.addLayout(source_layout)

        # Add some spacing
        spacer = QWidget()
        spacer.setFixedWidth(20)
        chat_layout.addWidget(spacer)

        # Destination selection
        dest_layout = QVBoxLayout()
        dest_layout.addWidget(QLabel('Destination Chat:'))
        
        # Destination category filters
        dest_filter_layout = QHBoxLayout()
        self.dest_all_radio = QRadioButton('All')
        self.dest_private_radio = QRadioButton('Private')
        self.dest_group_radio = QRadioButton('Groups')
        self.dest_channel_radio = QRadioButton('Channels')
        
        self.dest_all_radio.setChecked(True)
        self.dest_all_radio.toggled.connect(self.filter_dest_by_category)
        self.dest_private_radio.toggled.connect(self.filter_dest_by_category)
        self.dest_group_radio.toggled.connect(self.filter_dest_by_category)
        self.dest_channel_radio.toggled.connect(self.filter_dest_by_category)
        
        dest_filter_layout.addWidget(self.dest_all_radio)
        dest_filter_layout.addWidget(self.dest_private_radio)
        dest_filter_layout.addWidget(self.dest_group_radio)
        dest_filter_layout.addWidget(self.dest_channel_radio)
        dest_layout.addLayout(dest_filter_layout)
        
        self.dest_combo = QComboBox()
        self.dest_combo.setPlaceholderText('Select destination chat')
        dest_layout.addWidget(self.dest_combo)
        chat_layout.addLayout(dest_layout)

        chat_group.setLayout(chat_layout)
        setup_layout.addWidget(chat_group)

        # Filters section
        filter_group = QFrame()
        filter_group.setStyleSheet("QFrame { background-color: #f8f9fa; padding: 15px; margin-top: 10px; }")
        filter_layout = QVBoxLayout()
        filter_layout.addWidget(QLabel('Forward Filters:'))
        
        self.text_check = QCheckBox('Text Messages')
        self.media_check = QCheckBox('Media (Photos/Videos)')
        self.docs_check = QCheckBox('Documents')
        
        self.text_check.setChecked(True)
        self.media_check.setChecked(True)
        
        filter_layout.addWidget(self.text_check)
        filter_layout.addWidget(self.media_check)
        filter_layout.addWidget(self.docs_check)
        
        filter_group.setLayout(filter_layout)
        setup_layout.addWidget(filter_group)

        # Add progress bar in setup tab
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        setup_layout.addWidget(self.progress_bar)

        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton('▶ Start Forwarding')
        self.start_btn.clicked.connect(self.start_forwarding)
        self.start_btn.setEnabled(False)
        
        self.stop_btn = QPushButton('⏹ Stop Forwarding')
        self.stop_btn.clicked.connect(self.stop_forwarding)
        self.stop_btn.setEnabled(False)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        
        setup_layout.addLayout(button_layout)

        # Export button
        self.export_btn = QPushButton('📥 Export Chat List')
        self.export_btn.clicked.connect(self.export_chats)
        self.export_btn.setEnabled(False)
        setup_layout.addWidget(self.export_btn)

        setup_tab.setLayout(setup_layout)
        tabs.addTab(setup_tab, "Setup")

        # Logs tab
        logs_tab = QWidget()
        logs_layout = QVBoxLayout()
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        logs_layout.addWidget(QLabel('Activity Logs:'))
        logs_layout.addWidget(self.log_display)
        
        logs_tab.setLayout(logs_layout)
        tabs.addTab(logs_tab, "Logs")

        layout.addWidget(tabs)

        # Watermark
        watermark = QLabel('Made by azhardotcoder')
        watermark.setStyleSheet('color: #95a5a6; font-size: 10px; padding: 5px;')
        watermark.setAlignment(Qt.AlignRight)
        layout.addWidget(watermark)

        # Create menu bar
        menubar = self.menuBar()
        account_menu = menubar.addMenu('Account')
        
        # Add login/logout actions
        self.login_action = QAction('Login', self)
        self.login_action.triggered.connect(self.show_login_dialog)
        account_menu.addAction(self.login_action)
        
        self.logout_action = QAction('Logout', self)
        self.logout_action.triggered.connect(self.logout)
        account_menu.addAction(self.logout_action)

        self.show()

    def populate_combo_boxes(self, source_filter="", dest_filter=""):
        # Store current text to restore after clearing
        source_text = self.source_combo.currentText() if self.source_combo.lineEdit() else ""
        dest_text = self.dest_combo.currentText() if self.dest_combo.lineEdit() else ""
        
        # Clear existing items
        self.source_combo.clear()
        self.dest_combo.clear()
        
        # Filter and populate source chats
        self.filtered_source_chats = []
        for chat in self.original_chat_list:
            if source_filter.lower() in chat['title'].lower():
                display_text = f"{chat['title']} ({chat['type']}) [ID: {chat['id']}]"
                self.source_combo.addItem(display_text, chat['id'])
                self.filtered_source_chats.append(chat)
        
        # Filter and populate destination chats
        self.filtered_dest_chats = []
        for chat in self.original_chat_list:
            if dest_filter.lower() in chat['title'].lower():
                display_text = f"{chat['title']} ({chat['type']}) [ID: {chat['id']}]"
                self.dest_combo.addItem(display_text, chat['id'])
                self.filtered_dest_chats.append(chat)
        
        # Restore the search text
        if source_filter:
            self.source_combo.setEditText(source_text)
        if dest_filter:
            self.dest_combo.setEditText(dest_text)

    def filter_source_by_category(self):
        self.source_combo.clear()
        category = None
        
        if self.source_private_radio.isChecked():
            category = "Private"
        elif self.source_group_radio.isChecked():
            category = "Group"
        elif self.source_channel_radio.isChecked():
            category = "Channel"
            
        for chat in self.original_chat_list:
            if category is None or chat['type'] == category:
                display_text = f"{chat['title']} ({chat['type']})"
                # Add emoji based on chat type
                if chat['type'] == "Private":
                    display_text = f"👤 {display_text}"
                elif chat['type'] == "Group":
                    display_text = f"👥 {display_text}"
                elif chat['type'] == "Channel":
                    display_text = f"📢 {display_text}"
                self.source_combo.addItem(display_text, chat['id'])

    def filter_dest_by_category(self):
        self.dest_combo.clear()
        category = None
        
        if self.dest_private_radio.isChecked():
            category = "Private"
        elif self.dest_group_radio.isChecked():
            category = "Group"
        elif self.dest_channel_radio.isChecked():
            category = "Channel"
            
        for chat in self.original_chat_list:
            if category is None or chat['type'] == category:
                display_text = f"{chat['title']} ({chat['type']})"
                # Add emoji based on chat type
                if chat['type'] == "Private":
                    display_text = f"👤 {display_text}"
                elif chat['type'] == "Group":
                    display_text = f"👥 {display_text}"
                elif chat['type'] == "Channel":
                    display_text = f"📢 {display_text}"
                self.dest_combo.addItem(display_text, chat['id'])

    def update_status(self, status, is_active=True):
        if status == 'login':
            self.login_status.setText("✅ Logged In" if is_active else "⭕ Not Logged In")
            self.login_status.setStyleSheet(f"""
                QPushButton {{
                    background-color: {'#2ecc71' if is_active else '#e74c3c'};
                    padding: 8px 15px;
                    text-align: left;
                }}
            """)
        elif status == 'chats':
            self.chat_status.setText("✅ Chats Loaded" if is_active else "⭕ Chats Not Loaded")
            self.chat_status.setStyleSheet(f"""
                QPushButton {{
                    background-color: {'#2ecc71' if is_active else '#e74c3c'};
                    padding: 8px 15px;
                    text-align: left;
                }}
            """)
        elif status == 'forward':
            self.forward_status.setText("✅ Forwarding Active" if is_active else "⭕ Forwarding Inactive")
            self.forward_status.setStyleSheet(f"""
                QPushButton {{
                    background-color: {'#2ecc71' if is_active else '#e74c3c'};
                    padding: 8px 15px;
                    text-align: left;
                }}
            """)

    def update_chat_list(self, chats):
        self.chat_list = chats
        self.original_chat_list = chats.copy()
        
        # Initial population with all chats
        self.filter_source_by_category()
        self.filter_dest_by_category()
        
        self.start_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        self.update_status('chats', True)
        self.log_message("Chat list loaded successfully!")

    def logout(self):
        try:
            # Remove saved credentials
            if os.path.exists('credentials.json'):
                os.remove('credentials.json')
            
            # Remove session file
            session_file = f'session_{self.phone}.session'
            if os.path.exists(session_file):
                os.remove(session_file)
            
            # Clear UI fields
            self.api_id_input.clear()
            self.api_hash_input.clear()
            self.phone_input.clear()
            
            # Reset variables
            self.api_id = None
            self.api_hash = None
            self.phone = None
            
            # Update UI
            self.update_status('login', False)
            self.update_status('chats', False)
            self.load_chats_btn.setEnabled(False)
            self.start_btn.setEnabled(False)
            self.export_btn.setEnabled(False)
            
            self.log_message("Logged out successfully")
            QMessageBox.information(self, 'Success', 'Logged out successfully!')
        except Exception as e:
            self.log_error(f"Error during logout: {str(e)}")

    def handle_login(self):
        """Handle login button click"""
        try:
            api_id = self.api_id_input.text().strip()
            api_hash = self.api_hash_input.text().strip()
            phone = self.phone_input.text().strip()

            if not all([api_id, api_hash, phone]):
                QMessageBox.warning(self, 'Error', 'Please fill all fields!')
                return

            # Validate phone number format
            if not phone.startswith('+'):
                QMessageBox.warning(self, 'Error', 'Phone number must start with + and country code!')
                return

            try:
                self.api_id = int(api_id)
            except ValueError:
                QMessageBox.warning(self, 'Error', 'API ID must be a number!')
                return

            self.api_hash = api_hash
            self.phone = phone

            # Start authentication
            self.log_message("Starting authentication...")
            self.check_auth()

        except Exception as e:
            self.log_error(f"Login error: {str(e)}")

    def check_auth(self):
        if not all([self.api_id, self.api_hash, self.phone]):
            self.log_error("Missing login credentials!")
            return
            
        self.update_status('login', False)
        self.log_message("Starting authentication process...")
        
        try:
            # Initialize thread for login only (don't load chats)
            self.auth_thread = ChatListThread(self.api_id, self.api_hash, self.phone, load_chats=False)
            self.auth_thread.update_signal.connect(self.update_chat_list)
            self.auth_thread.error_signal.connect(self.handle_auth_error)
            self.auth_thread.code_request_signal.connect(self.show_otp_dialog)
            self.auth_thread.login_success_signal.connect(self.handle_login_success)
            self.auth_thread.status_signal.connect(self.log_message)
            self.auth_thread.progress_signal.connect(self.log_message)
            self.auth_thread.start()
        except Exception as e:
            self.log_error(f"Authentication error: {str(e)}")

    def handle_auth_error(self, error):
        self.log_error(error)
        self.update_status('login', False)
        QMessageBox.warning(self, 'Authentication Error', error)

    def handle_login_success(self):
        """Handle successful login and save credentials"""
        self.update_status('login', True)
        self.log_message("Successfully logged in!")
        self.load_chats_btn.setEnabled(True)
        
        # Save credentials after successful login
        self.save_credentials()

    def load_chats(self):
        self.log_message("Loading chats...")
        # Create new thread specifically for loading chats
        self.chat_list_thread = ChatListThread(self.api_id, self.api_hash, self.phone, load_chats=True)
        self.chat_list_thread.update_signal.connect(self.update_chat_list)
        self.chat_list_thread.error_signal.connect(self.log_error)
        self.chat_list_thread.status_signal.connect(self.log_message)
        self.chat_list_thread.progress_signal.connect(self.log_message)
        self.chat_list_thread.start()

    def start_forwarding(self):
        try:
            if not all([self.api_id, self.api_hash, self.phone]):
                QMessageBox.warning(self, 'Error', 'Please login first!')
                self.show_login_dialog()
                return

            source_id = self.source_combo.currentData()
            dest_id = self.dest_combo.currentData()

            if not all([source_id, dest_id]):
                QMessageBox.warning(self, 'Error', 'Please select source and destination chats!')
                return

            filters = {
                'text': self.text_check.isChecked(),
                'media': self.media_check.isChecked(),
                'documents': self.docs_check.isChecked()
            }

            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)

            self.forwarder_thread = ForwarderThread(
                self.api_id, 
                self.api_hash,
                self.phone,
                source_id,
                dest_id,
                filters,
                forward_existing=True
            )
            self.forwarder_thread.message_signal.connect(self.log_message)
            self.forwarder_thread.error_signal.connect(self.log_error)
            self.forwarder_thread.progress_signal.connect(self.update_progress)
            self.forwarder_thread.start()
            
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.update_status('forward', True)
            self.log_message("Starting to copy messages...")
            
        except Exception as e:
            self.log_error(f"Error starting forwarder: {str(e)}")

    def stop_forwarding(self):
        if hasattr(self, 'forwarder_thread'):
            self.forwarder_thread.stop()
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.update_status('forward', False)
            self.log_message("Forwarding stopped.")

    def export_chats(self):
        if not self.chat_list:
            QMessageBox.warning(self, 'Error', 'No chats to export!')
            return

        try:
            filename = f"chat_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.chat_list, f, indent=2, ensure_ascii=False)
            self.log_message(f"Chat list exported to {filename}")
            QMessageBox.information(self, 'Success', f'Chat list exported to {filename}')
        except Exception as e:
            self.log_error(f"Error exporting chats: {str(e)}")

    def log_message(self, message):
        self.log_display.append(f"[INFO] {message}")

    def log_error(self, error):
        self.log_display.append(f"[ERROR] {error}")
        self.statusBar().showMessage('Error occurred')

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        if value >= 100:
            self.progress_bar.setVisible(False)
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.update_status('forward', False)

    def show_login_dialog(self):
        dialog = LoginDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            credentials = dialog.get_credentials()
            if all(credentials.values()):
                try:
                    self.api_id = int(credentials['api_id'])
                    self.api_hash = credentials['api_hash']
                    self.phone = credentials['phone']
                    self.check_auth()
                except ValueError:
                    QMessageBox.warning(self, 'Error', 'API ID must be a number!')
                    self.show_login_dialog()
            else:
                QMessageBox.warning(self, 'Error', 'Please fill all fields!')
                self.show_login_dialog()

    def show_otp_dialog(self):
        self.log_message("Waiting for verification code input...")
        dialog = OTPDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            code = dialog.get_code()
            if code:
                self.log_message(f"Verification code entered: {code}")
                # Show loading dialog
                self.loading_dialog = LoadingDialog("Verifying code...", self)
                self.auth_thread.status_signal.connect(self.loading_dialog.update_message)
                self.auth_thread.progress_signal.connect(self.loading_dialog.update_progress)
                self.auth_thread.login_success_signal.connect(self.loading_dialog.accept)
                self.auth_thread.error_signal.connect(lambda x: self.loading_dialog.accept())
                
                self.auth_thread.set_verification_code(code)
                self.loading_dialog.exec_()
            else:
                self.log_message("No verification code entered")
                self.auth_thread.set_verification_code(None)
                self.log_error("Verification cancelled - no code entered")
        else:
            self.log_message("Verification dialog cancelled")
            self.auth_thread.set_verification_code(None)
            self.log_error("Verification cancelled by user")

    def load_and_auto_login(self):
        """Load saved credentials and attempt auto-login"""
        try:
            if os.path.exists('credentials.json'):
                with open('credentials.json', 'r') as f:
                    credentials = json.load(f)
                    
                if all(key in credentials for key in ['api_id', 'api_hash', 'phone']):
                    self.api_id_input.setText(str(credentials['api_id']))
                    self.api_hash_input.setText(credentials['api_hash'])
                    self.phone_input.setText(credentials['phone'])
                    
                    self.api_id = int(credentials['api_id'])
                    self.api_hash = credentials['api_hash']
                    self.phone = credentials['phone']
                    
                    # Auto start authentication
                    self.log_message("Found saved credentials, attempting auto-login...")
                    self.check_auth()
        except Exception as e:
            self.log_error(f"Error loading saved credentials: {str(e)}")

    def save_credentials(self):
        """Save credentials securely"""
        try:
            credentials = {
                'api_id': self.api_id,
                'api_hash': self.api_hash,
                'phone': self.phone
            }
            
            with open('credentials.json', 'w') as f:
                json.dump(credentials, f)
                
            self.log_message("Credentials saved successfully")
        except Exception as e:
            self.log_error(f"Error saving credentials: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Set application-wide font
    default_font = QFont('Segoe UI', 9)  # Windows default system font
    fallback_fonts = ['Arial', 'MS Shell Dlg 2', 'Helvetica']
    
    for fallback in fallback_fonts:
        default_font.insertSubstitution('Segoe UI', fallback)
    
    app.setFont(default_font)
    
    # Set style
    app.setStyle(QStyleFactory.create('Fusion'))
    
    # Set stylesheet
    app.setStyleSheet("""
        * {
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QMainWindow {
            background-color: #ffffff;
        }
        QLabel {
            color: #2c3e50;
            font-size: 12px;
            font-weight: bold;
        }
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
            min-height: 35px;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:disabled {
            background-color: #bdc3c7;
        }
    """)
    
    ex = TelegramForwarderUI()
    sys.exit(app.exec_()) 