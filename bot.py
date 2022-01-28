import telebot

import random

from typing import List

from enum import Enum
from dataclasses import dataclass

from telebot.types import Message

class AnswerType(Enum):
	No = 0,
	Yes = 1,


class GuessType(Enum):
	Letter = 0,
	Word = 1,
	Error = 2,


class Word():
	def __init__(self, word):
		self.q = "\U00002753"

		self.letterAttempts = set()

		self.word = list(word)
		self.mask = self.CreateWordMask(word)

		self.guessed = False

	def AddLetterAttempt(self, letter: str) -> None:
		self.letterAttempts.add(letter)

	def OpenLetters(self, letters: list) -> str:
		for i in letters:
			self.mask[i] = self.word[i]

		self.guessed = self.mask == self.word

		return self.GetMask()

	def CreateWordMask(self, word):
		length = len(word)
		return [self.q for _ in range(length)]

	def GetMask(self):
		return ''.join(self.mask)

	def GetWord(self):
		return ''.join(self.word)
		
	def IsGuessed(self):
		return self.guessed


@dataclass
class Player:
	name: str
	id: int
	word: Word

	def __init__(self, id: int, name: str):
		self.name = name
		self.id = id

	@classmethod
	def FromWord(cls, id: int, name: str, word: Word):
		p = Player(id, name)
		p.ChangeWord(word)

		return p

	def ChangeWord(self, newWord):
		self.word = newWord

	def ChangeName(self, name):
		self.name = name


class Hangman:
	def __init__(self):
		self.bot = telebot.TeleBot("5188887338:AAEkmGdVyFHkIw4gt_-oiksnYBJuvdl3bY0")

		self.YesNoKeyboard = telebot.types.ReplyKeyboardMarkup(True,True)
		self.YesNoKeyboard.row("Yes", "No")

		self.wordsFile = "words.txt"
		self.yesFile = "yes.txt"
		self.noFile = "no.txt"

		self.words = list()
		self.yesVariants = list()
		self.noVariants = list()

		self.LoadFiles()
		self.InitReplies()

		self.players = dict()

		@self.bot.message_handler(commands=['welcome', 'help'])
		def Welcome(message):
			self.bot.send_message(message.chat.id, self.welcomeMessage)

		@self.bot.message_handler(commands=['aboutme'])
		def AboutMe(message):
			reply = self.bot.send_message(message.chat.id, self.aboutMeMessage)

			self.bot.register_next_step_handler(reply, self.RememberPlayersName)

		@self.bot.message_handler(commands=['rules'])
		def Rules(message):
			self.bot.send_message(message.chat.id, self.rulesMessage)

		@self.bot.message_handler(commands=['start'])
		def StartGame(message):
			reply = self.bot.send_message(message.chat.id, self.playMessage, reply_markup=self.YesNoKeyboard)
			
			self.bot.register_next_step_handler(reply, self.StartPlaying)

	def AddOrUpdatePlayer(self, message: Message, word: Word):
		playerId = message.chat.id
		playerName = message.chat.first_name

		if (playerId in self.players):
			self.players[playerId].ChangeWord(word)
		else:
			self.players[playerId] = Player.FromWord(playerId, playerName, word)

	def RememberPlayersName(self, message):
		playerId = message.chat.id
		playerName = message.text

		if (playerId in self.players):
			self.players[playerId].ChangeName(playerName)
		else:
			self.players[playerId] = Player(playerId, playerName)

		self.bot.send_message(message.chat.id, f"I shall now be calling you {playerName}.")

	def InitializeGame(self, message):
		w = random.choice(self.words)
		word = Word(w)

		self.AddOrUpdatePlayer(message, word)

		print(w)

		reply = self.bot.send_message(message.chat.id, f"Here is your word:\n{word.GetMask()}\n Make a guess!")

		self.bot.register_next_step_handler(reply, self.PlayRound)

	def StartPlaying(self, message):
		reply = message.text.lower()

		if (self.ValidateAnswerType(reply, AnswerType.Yes)):
			self.InitializeGame(message)

	def RestartGame(self, message):
		self.bot.send_message(message.chat.id, "I see you want to restart game, sure!")

		self.InitializeGame(message)

	def StopGame(self, message):
		self.bot.send_message(message.chat.id, "Stopping the game per your request.")

	def ShowCurrentGuesses(self, message):
		playerId = message.chat.id
		word = self.players[playerId].word

		if (len(word.letterAttempts) > 0):
			self.bot.send_message(message.chat.id, f"Current attempted letters: {' '.join(word.letterAttempts)}")

	def PlayRound(self, message):
		reply = self.HandleGuess(message)

		if (isinstance(reply, Message)):
			self.ShowCurrentGuesses(message)

			self.bot.register_next_step_handler(reply, self.PlayRound)

	def HandleGuess(self, message):
		guess = message.text.lower()
		playerId = message.chat.id
		word = self.players[playerId].word.GetWord()

		if (guess == "/stop"):
			self.StopGame(message)
			return
		elif (guess == '/start'):
			self.RestartGame(message)
			return

		guessType = self.DetermineGuessType(guess)

		if (guessType == GuessType.Error):
			return self.bot.send_message(message.chat.id, self.invalidGuessReply)

		if (guessType == GuessType.Letter):

			# Already guesses this letter
			if (guess in self.players[playerId].word.letterAttempts):
				return self.bot.send_message(message.chat.id, f"You've already guessed this letter!")

			# Remembering the guess
			self.players[playerId].word.AddLetterAttempt(guess)

			result = self.CheckLetter(guess, word)

			if (result):
				newMask = self.players[playerId].word.OpenLetters(result)

				if (self.players[playerId].word.IsGuessed()):
					self.bot.send_message(message.chat.id, f"Word guessed correctly! Nice job, {self.players[playerId].name}! If you want to play again, press /start")
					return

				reply = self.bot.send_message(message.chat.id, f"Letter guessed correctly! Nice job, {self.players[playerId].name}!\n{newMask}")
				
			else:
				reply = self.bot.send_message(message.chat.id, f"Letter is not found! Wanna try again?")

		elif (guessType == GuessType.Word):
			result = self.CheckWord(guess, word)

			if (result):
				self.bot.send_message(message.chat.id, f"Word guessed correctly! Nice job, {self.players[playerId].name}! If you want to play again, press /start")
				return

			else:
				reply = self.bot.send_message(message.chat.id, f"Incorrect word guess! Wanna try again?")

		return reply

	def DetermineGuessType(self, text: str) -> GuessType:
		if (not text.isalpha()):
			return GuessType.Error
		
		if (len(text) == 1):
			return GuessType.Letter

		return GuessType.Word

	def CheckLetter(self, letter: str, word: str) -> List[int]:
		return [pos for pos, char in enumerate(word) if char == letter]

	def CheckWord(self, guessWord: str, word: str) -> bool:
		if (guessWord == word):
			return True
		return False

	def ValidateAnswerType(self, text: str, answerType: AnswerType) -> bool:
		if (text in self.yesVariants and answerType == AnswerType.Yes):
			return True

		if (text in self.noVariants and answerType == AnswerType.No):
			return True

		return False

	def LoadFiles(self):
		self.ReadFileLower(self.wordsFile, self.words)
		self.ReadFileLower(self.yesFile, self.yesVariants)
		self.ReadFileLower(self.noFile, self.noVariants)

	def ReadFileLower(self, fileName: str, array: list) -> None:
		with open(fileName, 'r') as file:
			for line in file:
				array.append(line[:-1].lower())

	def Run(self):
		self.bot.infinity_polling()

	def InitReplies(self):

		self.welcomeMessage = """
Hello! I am the Hangman bot developed by Georgy.
The rules are here -> /rules
We can go ahead and start playing the game -> /start
Or we can get to know eachother first -> /aboutme		
"""

		self.playMessage = """
Let's play then! Are you ready?
"""

		self.rulesMessage = """
The rules are simple. I give you a word and you have to guess it.
You have 10 attempts, if you miss a word or a letter -> -1 attempt.
When you run out of attempts, the game is over.
"""

		self.aboutMeMessage = """
I see you want to tell me about yourself.
What is your name?
"""

		self.invalidGuessReply = """
We have only English words here.

Please, guess the whole word or just a letter.
If you want to stop playing, press /stop
If you want to restart game, press /start
"""


hangman = Hangman()
hangman.Run()