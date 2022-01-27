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

		self.word = list(word)
		self.mask = self.CreateWordMask(word)

	def OpenLetters(self, letters: list) -> str:
		for i in letters:
			self.mask[i] = self.word[i]

		return self.GetMask()

	def CreateWordMask(self, word):
		length = len(word)
		return [self.q for _ in range(length)]

	def GetMask(self):
		return ''.join(self.mask)

	def GetWord(self):
		return ''.join(self.word)
		

@dataclass
class Player:
	name: str
	id: int
	word: Word

	def __init__(self, id: int, name: str, word: Word):
		self.name = name
		self.id = id
		self.word = word

	def ChangeWord(self, newWord):
		self.word = newWord


class Hangman:
	def __init__(self):
		self.bot = telebot.TeleBot("5188887338:AAEkmGdVyFHkIw4gt_-oiksnYBJuvdl3bY0")

		self.YesNoKeyboard = telebot.types.ReplyKeyboardMarkup(True,True)
		self.YesNoKeyboard.row("Yes", "No")

		self.wordsFile = "words.txt"
		self.yesFile = "yes.txt"
		self.noFile = "no.txt"

		self.invalidGuessReply = """
We have only English words here.

Please, guess the whole word or just a letter.
If you want to stop playing, press /stop
If you want to restart game, press /start
"""

		self.words = list()
		self.yesVariants = list()
		self.noVariants = list()

		self.LoadFiles()

		self.players = dict()

		@self.bot.message_handler(commands=['start', 'help'])
		def Welcome(message):
			reply = self.bot.send_message(message.chat.id, "Hey! This is a Hangman bot. Wanna play?", reply_markup=self.YesNoKeyboard)

			# bot.send_message(message.chat.id, "".join("\U00002753" for i in range(5)).join("A").join("\U00002753" for i in range(5)))

			self.bot.register_next_step_handler(reply, self.StartPlaying)

	def AddOrUpdatePlayer(self, message: Message, word: Word):
		playerId = message.chat.id
		playerName = message.chat
		if (playerId in self.players):
			self.players[playerId].ChangeWord(word)
		else:
			self.players[playerId] = Player(playerId, playerName, word)

	def InitializeGame(self, message):
		w = random.choice(self.words)

		self.AddOrUpdatePlayer(message, Word(w))

		reply = self.bot.send_message(message.chat.id, f"Here is your word: {w}. Make a guess!")

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

	def PlayRound(self, message):
		reply = self.HandleGuess(message)

		if (isinstance(reply, Message)):
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
			result = self.CheckLetter(guess, word)

			if (result):
				reply = self.bot.send_message(message.chat.id, f"Letter guessed correctly at positions {result}!")
			else:
				reply = self.bot.send_message(message.chat.id, f"Letter is not found! Wanna try again?")

		elif (guessType == GuessType.Word):
			result = self.CheckWord(guess, word)

			if (result):
				reply = self.bot.send_message(message.chat.id, f"Word guessed correctly!")
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


hangman = Hangman()
hangman.Run()