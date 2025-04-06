# Telegram Media Forwarder

A powerful GUI application for forwarding messages and media between Telegram channels, groups, and chats.

## Features

- 🖼️ Modern and intuitive PyQt5-based user interface
- 🔄 Forward messages between any Telegram chats, channels, or groups
- 📁 Support for all types of media (photos, videos, documents, etc.)
- ⚡ Asynchronous operation for better performance
- 🔍 Advanced filtering options
- 💾 Session management for quick reconnection
- 📊 Progress tracking and status updates

## Prerequisites

- Python 3.7 or higher
- Telegram API credentials (api_id and api_hash)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/azhardotcoder/Telegram-Media-Forwarder.git
   cd Telegram-Media-Forwarder
   ```

2. Install required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Get your Telegram API credentials:
   - Go to https://my.telegram.org/auth
   - Log in with your phone number
   - Go to 'API development tools'
   - Create a new application
   - Copy your api_id and api_hash

## Usage

1. Run the application:

   ```bash
   python telegram_forwarder_ui_v2.py
   ```

2. First-time setup:
   - Enter your Telegram API credentials
   - Enter your phone number
   - Enter the verification code sent to your Telegram account

3. Forward messages:
   - Select source and destination chats
   - Configure filtering options (if needed)
   - Click "Start Forwarding"

## Security Notes

- Never share your Telegram API credentials
- The application stores session files locally for convenience
- Logout when you're done to clear sensitive data

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational purposes only. Please respect Telegram's terms of service and don't use this tool for spam or abuse.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.
