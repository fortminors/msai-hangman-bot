# Hangman bot developed as a part of Software Development Project in MSAI

## General information and APIs used

- This bot allows to play [Hangman game](https://en.wikipedia.org/wiki/Hangman_(game))
- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI) for setting up the bot
- [ponyorm](https://github.com/ponyorm/pony/) for storing information in a database

## Link to the bot:

- https://t.me/MSAI_Hangman_bot

## List of possible commands:

![image](https://user-images.githubusercontent.com/36015059/151781368-082cbe79-1895-4efc-a5b2-234025c260eb.png)

- `/welcome` or `/help` Gives a brief introduction to the bot and the commands to start interacting with it
- `/start` Starts the game, or if the bot doesn't know you -> `/welcome` command is triggered
- `/stop` Stops the game if one has been started
- `/aboutme` Lets a user change their name
- `/leaderboard` Shows the scores of other players in the descending order of scores
- `/rules` Gives the rules to play the game
- `/language` Allows the user to change the language. Possible options are: English and Russian

## Project structure

- `bot.py` Contains the bot's logic
- `database.py` Contains interaction with the database
- `localization.py` Provides the message templates for English and Russian language
- `player.py` Provides a class to store players data that keeps the game's content. This content is temporary unlike what's written in the database
- `state.py` Allows changing states of the game (attempt 1 to attempt 10)
- `word.py` Helps to manage interactions with the words to be guessed
- `files` Folder contains the words that the bot uses for the game
