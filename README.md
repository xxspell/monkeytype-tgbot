# MonkeyType Telegram Bot
This project is a Telegram bot that fetches typing test results from MonkeyType API, stores them in a local SQLite database, and sends updates to authorized users on Telegram.

## Features
 - Authentication: Uses MonkeyType's authentication API to get an auth token.
 - Data Fetching: Periodically fetches typing test results from the MonkeyType API.
 - Data Storage: Stores results in a local SQLite database.
 - Notification: Sends new results and overall statistics to authorized Telegram users.
 - Authorization: Users need to authorize themselves to receive updates.

## Installation

1. Clone the repository:
    ```bash
   git clone https://github.com/xxspell/monkeytype-tgbot.git
    cd monkeytype-tgbot
    ```
   
2. Install dependencies:
    ```bash
      poetry install
    ```

3. Create and configure the environment file:

    Copy the sample environment file and fill in the required values:
    ```bash
   cp .env.sample .env
    ```
   Edit the .env file to add your Telegram bot token, MonkeyType API credentials, and other configurations.

4. Run the bot:
    ```
    poetry run python src/main.py
   ```
   
## Usage
- `/start`: Starts the interaction with the bot. If the user is already authorized, it will greet them.
- `/auth`: Initiates the authorization process for a new user.
- `/verify <code>`: Verifies the authorization code provided to the user.