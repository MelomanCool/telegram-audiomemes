# Telegram AudioMemes
A Telegram bot that lets you send audio memes.


## Usage
Search using [inline mode](https://core.telegram.org/bots/inline).  
To get the name of a meme, reply to it with __name__ command.

Manage memes using following commands:
* __add__ – add a meme
* __cancel__ – cancel adding
* __rename__ – rename the meme (use replying to the meme)
* __delete__ – delete the meme (use replying to the meme)

(you can rename or delete only memes you've created yourself)


## Requirements

The code has been tested only on Python 3.4.

This bot uses following packages:
* `python_telegram_bot` – Telegram API wrapper.
* `fuzzywuzzy` – for meme searching.
* `pydub` – for converting `Audio` (mp3) to `Voice` (ogg) objects.

After cloning the repo, you can install requirements with pip:  
`pip3 install -r requirements.txt`


## Running the bot

1. Clone this repository:  
   `git clone https://github.com/MelomanCool/telegram-audiomemes.git`

2. Create a `config.py` file containing the api token you got from [@BotFather](https://telegram.me/BotFather):  
   `TOKEN = "YOUR_TOKEN"`

3. Run the bot:  
   `python3 main.py`
