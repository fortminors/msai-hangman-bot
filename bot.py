import telebot
import random

from enum import Enum


class AnswerType(Enum):
	No = 0,
	Yes = 1,


class GuessType(Enum):
	Letter = 0,
	Word = 1,
	Error = 2,

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

		self.q = "\U00002753"

		self.LoadFiles()

		self.runGame = True

		@self.bot.message_handler(commands=['start', 'help'])
		def Welcome(message):
			reply = self.bot.send_message(message.chat.id, "Hey! This is a Hangman bot. Wanna play?", reply_markup=self.YesNoKeyboard)

			# bot.send_message(message.chat.id, "".join("\U00002753" for i in range(5)).join("A").join("\U00002753" for i in range(5)))

			self.bot.register_next_step_handler(reply, self.StartPlaying)

	def StartPlaying(self, message):
		self.runGame = True

		reply = message.text.lower()

		if (self.ValidateAnswerType(reply, AnswerType.Yes)):
			self.currentWord = random.choice(self.words)
			reply = self.bot.reply_to(message, f"Here is your word: {self.currentWord}. Make a guess!")

			self.bot.register_next_step_handler(reply, self.PlayRound)

	def StopGame(self, message):
			self.runGame = False

			self.bot.send_message(message.chat.id, "Stopping the game per your request.")

	def PlayRound(self, message):
		reply = self.HandleGuess(message)

		if (self.runGame):
			self.bot.register_next_step_handler(reply, self.PlayRound)

	def HandleGuess(self, message):
		guess = message.text.lower()

		if (guess == "/stop"):
			self.StopGame(message)
			return

		guessType = self.DetermineGuessType(guess)

		if (guessType == GuessType.Error):
			return self.bot.send_message(message.chat.id, "We have only English words here. Please, guess the whole word or just a letter.")

		answerContent = "Letter" if guessType == GuessType.Letter else "Word"

		if (guessType == GuessType.Letter):
			result = self.CheckLetter(guess, self.currentWord)
		else:
			result = self.CheckWord(guess, self.currentWord)

		if (result):
			reply = self.bot.send_message(message.chat.id, f"{answerContent} guessed correctly!")
		else:
			reply = self.bot.send_message(message.chat.id, f"{answerContent} is not correct! Wanna try again?")

		return reply

	def DetermineGuessType(self, text: str) -> GuessType:
		if (not text.isalpha()):
			return GuessType.Error
		
		if (len(text) == 1):
			return GuessType.Letter

		return GuessType.Word

	def CheckLetter(self, letter: str, word: str) -> bool:
		if (letter in word):
			return True
		return False

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