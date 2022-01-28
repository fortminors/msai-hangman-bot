from pyexpat.errors import messages
import telebot

import random

from typing import List
from typing import Dict

from enum import Enum
from dataclasses import dataclass
from string import Template

from telebot.types import Message
from telebot.types import ReplyKeyboardMarkup

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
	attempts: int
	deleteMessageCandidates: List[Message]
	meaningfulMessages: Dict[str, Message]

	def __init__(self, id: int, name: str):
		self.name = name
		self.id = id
		self.attempts = 10
		self.deleteMessageCandidates = list()
		self.meaningfulMessages = dict()

	@classmethod
	def FromWord(cls, id: int, name: str, word: Word):
		p = Player(id, name)
		p.ChangeWord(word)

		return p

	def ChangeWord(self, newWord):
		self.word = newWord

	def ChangeName(self, name):
		self.name = name

	def AddMessageToDelete(self, message: Message):
		self.deleteMessageCandidates.append(message)

	def GetMessagesToDelete(self):
		return self.deleteMessageCandidates

	def RefreshAttempts(self):
		self.attempts = 10

	# Returns True if there are still attempts left
	def DecreaseAttempts(self) -> bool:
		self.attempts -= 1

		if (self.attempts <= 0):
			return False
		
		return True

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
			self.AddPlayer(message)
			self.AddMessageToDelete(message)

			self.SendMessage(message.chat.id, self.welcomeMessage, True)

		@self.bot.message_handler(commands=['aboutme'])
		def AboutMe(message):
			self.AddPlayer(message)
			self.AddMessageToDelete(message)

			reply = self.SendMessage(message.chat.id, self.aboutMeMessage, True)
			self.bot.register_next_step_handler(reply, self.UpdatePlayersName)

		@self.bot.message_handler(commands=['rules'])
		def Rules(message):
			self.AddPlayer(message)
			self.AddMessageToDelete(message)

			self.SendMessage(message.chat.id, self.rulesMessage, True)

		@self.bot.message_handler(commands=['start'])
		def StartGame(message):
			# Ignoring start game if this is the first start for this player
			if (message.chat.id not in self.players):
				Welcome(message)
				return

			self.AddPlayer(message)
			self.AddMessageToDelete(message)

			self.DeleteAllPreviousMessages(message)

			reply = self.SendMessage(message.chat.id, self.playMessage, True, self.YesNoKeyboard)
			self.bot.register_next_step_handler(reply, self.StartPlaying)

	def SendMessage(self, id: int, text: str, toDelete: bool = None, keyboard: ReplyKeyboardMarkup = None) -> Message:
		message = self.bot.send_message(id, text, reply_markup=keyboard)

		if (toDelete):
			self.players[id].AddMessageToDelete(message)

		return message

	def AddPlayer(self, message: Message):
		playerId = message.chat.id
		playerName = message.chat.first_name

		if (playerId not in self.players):
			self.players[playerId] = Player(playerId, playerName)

	def UpdatePlayersName(self, message):
		playerId = message.chat.id
		playerName = message.text

		self.AddMessageToDelete(message)

		self.players[playerId].ChangeName(playerName)

		self.SendMessage(message.chat.id, self.changedName.substitute(name=playerName), True)

	def UpdateWord(self, message: Message, word: Word):
		playerId = message.chat.id
		playerName = message.chat.first_name

		if (playerId in self.players):
			self.players[playerId].ChangeWord(word)
		else:
			self.players[playerId] = Player.FromWord(playerId, playerName, word)

	def InitializeGame(self, message):
		playerId = message.chat.id
		w = random.choice(self.words)
		word = Word(w)

		self.UpdateWord(message, word)

		print(w)
		reply = self.SendMessage(message.chat.id, self.makeAGuess.substitute(word=word.GetMask()), True)
		self.players[playerId].meaningfulMessages['showWord'] = reply

		self.players[playerId].RefreshAttempts()
		attempts = self.players[playerId].attempts
		reply = self.SendMessage(message.chat.id, self.attemptsLeft.substitute(attempts=attempts), True)
		self.players[playerId].meaningfulMessages['attempts'] = reply

		self.ShowCurrentLetterAttempts(message)

		self.bot.register_next_step_handler(reply, self.PlayRound)

	def StartPlaying(self, message):
		reply = message.text.lower()

		self.AddMessageToDelete(message)

		if (self.ValidateAnswerType(reply, AnswerType.Yes)):
			self.InitializeGame(message)
		else:
			self.SendMessage(message.chat.id, self.playReject, True)

	def RestartGame(self, message):
		self.DeleteAllPreviousMessages(message)

		self.SendMessage(message.chat.id, self.restartGame, True)

		self.InitializeGame(message)

	def StopGame(self, message):
		self.SendMessage(message.chat.id, self.stopGame, True)

	def ShowCurrentLetterAttempts(self, message):
		playerId = message.chat.id
		word = self.players[playerId].word
 
		m = self.SendMessage(message.chat.id, self.currentLetters.substitute(letters=' '.join(word.letterAttempts)), True)
		self.players[playerId].meaningfulMessages['letterAttempts'] = m

	def DeleteUserMessage(self, message):
		self.bot.delete_message(message.chat.id, message.id)

	def UpdateMessage(self, message, text) -> Message:
		self.bot.edit_message_text(text, message.chat.id, message.id)
		return message

	def PlayRound(self, message):
		reply = self.HandleGuess(message)

		self.DeleteUserMessage(message)

		# Ignore ended dialogues. They return None
		if (isinstance(reply, Message)):
			self.bot.register_next_step_handler(reply, self.PlayRound)

	def HandleGuess(self, message):
		guess = message.text.lower()
		playerId = message.chat.id
		word = self.players[playerId].word.GetWord()

		reply = self.players[playerId].meaningfulMessages['showWord']	

		if (guess == "/stop"):
			self.StopGame(message)
			return
		elif (guess == '/start'):
			self.RestartGame(message)
			return

		guessType = self.DetermineGuessType(guess)

		if (guessType == GuessType.Error):
			return self.SendMessage(message.chat.id, self.invalidGuessReply, True)

		if (guessType == GuessType.Letter):

			# Already guessed this letter
			if (guess in self.players[playerId].word.letterAttempts):
				#return self.SendMessage(message.chat.id, self.letterDuplicate, True)
				return reply

			# Remembering the guess
			self.players[playerId].word.AddLetterAttempt(guess)

			# Updating the letters that the user guessed
			m = self.players[playerId].meaningfulMessages['letterAttempts']
			w = self.players[playerId].word
			self.UpdateMessage(m, self.currentLetters.substitute(letters=' '.join(w.letterAttempts)))

			result = self.CheckLetter(guess, word)

			# Guess succeeded
			if (result):
				newMask = self.players[playerId].word.OpenLetters(result)

				if (self.players[playerId].word.IsGuessed()):
					self.SendMessage(message.chat.id, self.correctWordGuess.substitute(name=self.players[playerId].name), True)
					return

				showWordMessage = self.players[playerId].meaningfulMessages['showWord']
				reply = self.UpdateMessage(showWordMessage, self.makeAGuess.substitute(word=newMask))

				# reply = self.SendMessage(message.chat.id, self.correctLetterGuess.substitute(name=self.players[playerId].name, newMask=newMask), True)

			# Guess failed
			else:
				stillPlaying = self.players[playerId].DecreaseAttempts()

				if (not stillPlaying):
					self.SendMessage(message.chat.id, self.noAttempts, True)
					return

				attempts = self.players[playerId].attempts
				attemptsMessage = self.players[playerId].meaningfulMessages['attempts']

				reply = self.UpdateMessage(attemptsMessage, self.attemptsLeft.substitute(attempts=attempts))
				# reply = self.SendMessage(message.chat.id, self.letterNotFound, True)

		elif (guessType == GuessType.Word):
			result = self.CheckWord(guess, word)

			# Guess succeeded
			if (result):
				self.SendMessage(message.chat.id, self.correctWordGuess.substitute(name=self.players[playerId].name), True)
				return

			# Guess failed
			else:
				stillPlaying = self.players[playerId].DecreaseAttempts()

				if (not stillPlaying):
					self.SendMessage(message.chat.id, self.noAttempts, True)
					return

				attempts = self.players[playerId].attempts
				attemptsMessage = self.players[playerId].meaningfulMessages['attempts']

				reply = self.UpdateMessage(attemptsMessage, self.attemptsLeft.substitute(attempts=attempts))
				# reply = self.SendMessage(message.chat.id, self.incorrectWordGuess, True)

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

			# :-1 trims the last character of last line
			array[-1] = line.lower()

	def AddMessageToDelete(self, message):
		playerId = message.chat.id

		if (playerId in self.players):
			self.players[playerId].AddMessageToDelete(message)

	def DeleteAllPreviousMessages(self, message):
		playerId = message.chat.id

		if (playerId in self.players):
			messages = self.players[playerId].GetMessagesToDelete()
			
			for _ in range(len(messages)):
				m = messages.pop()
				self.DeleteUserMessage(m)

			self.players[playerId].meaningfulMessages.clear()

	def Run(self):
		self.bot.infinity_polling()

	def InitReplies(self):

		self.welcomeMessage = """
Hello! I am the Hangman bot developed by Georgy.
The rules are here -> /rules
We can go ahead and start playing the game -> /start
Or we can get to know eachother first -> /aboutme		
"""

		self.playMessage = "Let's play then! Are you ready?"

		self.playReject = "Okay! I guess we are not playing then. If you change your mind, let me know -> /start"

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

		self.correctWordGuess = Template("""
Word guessed correctly! Nice job, $name! If you want to play again, press /start
""")

		self.correctLetterGuess = Template("""
Letter guessed correctly! Nice job, $name!
$newMask
""")

		self.letterNotFound = "Letter is not found! Wanna try again?"

		self.incorrectWordGuess = "Incorrect word guess! Wanna try again?"

		self.letterDuplicate = "You've already guessed this letter!"

		self.changedName  = Template("I shall now be calling you $name.")

		self.makeAGuess = Template("Word to guess: $word")

		self.attemptsLeft = Template("Attempts left: $attempts")

		self.restartGame = "I see you want to restart game, sure!"

		self.stopGame = "Stopping the game per your request."

		self.currentLetters = Template("Current attempted letters: $letters")

		self.noAttempts = "No attempts left, you've lost! If you want to play again, press /start"

hangman = Hangman()
hangman.Run()