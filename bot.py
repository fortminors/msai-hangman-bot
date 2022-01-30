from pyexpat.errors import messages
import telebot

import random

from typing import List, Set, Dict

from enum import Enum
from dataclasses import dataclass
from string import Template

from telebot.types import Message
from telebot.types import ReplyKeyboardMarkup
from telebot.types import InputMediaPhoto

from database import DatabaseManager

from localization import EnglishLocalization, RussianLocalization

class GuessType(Enum):
	Letter = 0,
	Word = 1,
	Error = 2,

class State(Enum):
	state_0 = 0
	state_1 = 1
	state_2 = 2
	state_3 = 3
	state_4 = 4
	state_5 = 5
	state_6 = 6
	state_7 = 7
	state_8 = 8
	state_9 = 9
	state_10 = 10

@dataclass
class StateManager:
	state: State = State.state_0
	maxState: int = 10

	def Next(self):
		if (self.state.value == self.maxState):
			self.state = State.state_0
		else:
			self.state = State(self.state.value + 1)

	def Reset(self):
		self.state = State.state_0

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
	stateManager: StateManager
	deleteMessageCandidates: Set[Message]
	meaningfulMessages: Dict[str, Message]
	localization: EnglishLocalization | RussianLocalization

	def __init__(self, id: int, name: str):
		self.name = name
		self.id = id
		self.attempts = 10
		self.stateManager = StateManager()
		self.deleteMessageCandidates = set()
		self.meaningfulMessages = dict()
		self.localization = EnglishLocalization()

	@classmethod
	def FromWord(cls, id: int, name: str, word: Word):
		p = Player(id, name)
		p.ChangeWord(word)

		return p

	def ChangeWord(self, newWord):
		self.word = newWord

	def ChangeName(self, name):
		self.name = name

	def ResetState(self):
		self.stateManager.Reset()

	def NextState(self):
		self.stateManager.Next()

	def CurrentState(self) -> str:
		return self.stateManager.state.name

	def AddMessageToDelete(self, message: Message):
		self.deleteMessageCandidates.add(message)

	def RemoveMessageFromDelete(self, message: Message):
		if (message in self.deleteMessageCandidates):
			self.deleteMessageCandidates.remove(message)

	def GetMessagesToDelete(self):
		return self.deleteMessageCandidates

	def RefreshAttempts(self):
		self.attempts = 10

	def ChangeLocalization(self, localization: EnglishLocalization | RussianLocalization):
		self.localization = localization

	# Returns True if there are still attempts left
	def DecreaseAttempts(self) -> bool:
		self.attempts -= 1

		if (self.attempts <= 0):
			return False
		
		return True

class Hangman:
	def __init__(self):
		self.bot = telebot.TeleBot("5188887338:AAEkmGdVyFHkIw4gt_-oiksnYBJuvdl3bY0")

		self.yesNoKeyboardEnglish = ReplyKeyboardMarkup(True, True)
		self.yesNoKeyboardEnglish.row("Yes", "No")

		self.yesNoKeyboardRussian = ReplyKeyboardMarkup(True, True)
		self.yesNoKeyboardRussian.row("Да", "Нет")

		self.defaultKeyboard = ReplyKeyboardMarkup(True, False)
		self.defaultKeyboard.row("/start", "/stop")
		self.defaultKeyboard.row("/welcome", "/help")
		self.defaultKeyboard.row("/aboutme", "/rules")
		self.defaultKeyboard.row("/leaderboard", "/language")

		self.languageKeyboard = ReplyKeyboardMarkup(True, True)
		self.languageKeyboard.row("Русский", "English")

		self.wordsRussianFile = "files/words_russian.txt"
		self.wordsEnglishFile = "files/words_english.txt"

		self.statePath = "states/easy/"

		self.wordsRussian = list()
		self.wordsEnglish = list()

		self.LoadFiles()

		self.players = dict()

		self.databaseManager = DatabaseManager()

		@self.bot.message_handler(commands=['welcome', 'help'])
		def Welcome(message):
			self.AddPlayer(message)
			self.AddMessageToDelete(message)

			self.SendMessage(message.chat.id, self.players[message.chat.id].localization.welcomeMessage, True, self.defaultKeyboard)

			self.databaseManager.GetLeaderboard(10)

		@self.bot.message_handler(commands=['aboutme'])
		def AboutMe(message):
			self.AddPlayer(message)
			self.AddMessageToDelete(message)

			reply = self.SendMessage(message.chat.id, self.players[message.chat.id].localization.aboutMeMessage, True)
			self.bot.register_next_step_handler(reply, self.UpdatePlayersName)

		@self.bot.message_handler(commands=['rules'])
		def Rules(message):
			self.AddPlayer(message)
			self.AddMessageToDelete(message)

			self.SendMessage(message.chat.id, self.players[message.chat.id].localization.rulesMessage, True)

		@self.bot.message_handler(commands=['leaderboard'])
		def ShowLeaderboard(message):
			self.AddPlayer(message)
			self.AddMessageToDelete(message)

			leaderboard = self.databaseManager.GetLeaderboard(10)

			self.SendMessage(message.chat.id, '\n'.join(self.SubstituteLeaderboardStats(message, stats) for stats in leaderboard), True)

		@self.bot.message_handler(commands=['language'])
		def ChangeLanguage(message):
			self.AddPlayer(message)
			self.AddMessageToDelete(message)

			reply = self.SendMessage(message.chat.id, self.players[message.chat.id].localization.changeLanguage, True, self.languageKeyboard)

			self.bot.register_next_step_handler(reply, self.HandleChangeLanguage)

		@self.bot.message_handler(commands=['start'])
		def StartGame(message):
			# Ignoring start game if this is the first start for this player
			if (not self.databaseManager.PlayerExists(message.chat.id)):
				Welcome(message)
				return

			self.AddPlayer(message)
			self.AddMessageToDelete(message)

			self.DeleteAllPreviousMessages(message)

			keyboard = self.yesNoKeyboardEnglish
			playerId = message.chat.id

			if (isinstance(self.players[playerId].localization, RussianLocalization)):
				keyboard = self.yesNoKeyboardRussian

			reply = self.SendMessage(message.chat.id, self.players[message.chat.id].localization.playMessage, True, keyboard)
			self.bot.register_next_step_handler(reply, self.StartPlaying)

	def SendState(self, state, message):
		with open(f'{self.statePath}{state}.png', 'rb') as image:
			m = self.bot.send_photo(message.chat.id, image)

		# Always cleanup photos
		self.players[message.chat.id].AddMessageToDelete(m)
		return m

	def UpdateState(self, message):
		playerId = message.chat.id

		if ('state' in self.players[playerId].meaningfulMessages):
			self.players[playerId].NextState()

			stateMessage = self.players[playerId].meaningfulMessages['state']
			self.DeleteUserMessage(stateMessage)

		stateName = self.players[playerId].CurrentState()
		stateMessage = self.SendState(stateName, message)
		self.players[playerId].meaningfulMessages['state'] = stateMessage

	def SendMessage(self, id: int, text: str, toDelete: bool = None, keyboard: ReplyKeyboardMarkup = None) -> Message:
		message = self.bot.send_message(id, text, reply_markup=keyboard)

		if (toDelete):
			self.players[id].AddMessageToDelete(message)

		return message

	def UpdateMessage(self, message, text) -> Message:
		self.bot.edit_message_text(text, message.chat.id, message.id)
		return message

	def DeleteUserMessage(self, message):
		playerId = message.chat.id
		self.players[playerId].RemoveMessageFromDelete(message)
		self.bot.delete_message(message.chat.id, message.id)

	def AddPlayer(self, message: Message):
		playerId = message.chat.id
		playerName = message.chat.first_name

		if (playerId not in self.players):
			player = self.databaseManager.GetPlayerIfExists(playerId)

			# Saving the new player
			if (player is None):
				self.databaseManager.AddPlayer(playerId, playerName)
			# Taking what's stored
			else:
				playerName = player.name

			self.players[playerId] = Player(playerId, playerName)

	def UpdatePlayersName(self, message):
		playerId = message.chat.id
		playerName = message.text

		self.AddMessageToDelete(message)

		self.players[playerId].ChangeName(playerName)

		self.SendMessage(message.chat.id, self.players[message.chat.id].localization.changedName.substitute(name=playerName), True)

		self.databaseManager.ChangePlayerName(playerId, playerName)

	def UpdateWord(self, message: Message, word: Word):
		playerId = message.chat.id
		playerName = message.chat.first_name

		if (playerId in self.players):
			self.players[playerId].ChangeWord(word)
		else:
			self.players[playerId] = Player.FromWord(playerId, playerName, word)

	def InitializeGame(self, message):
		playerId = message.chat.id

		if (isinstance(self.players[playerId].localization, EnglishLocalization)):
			w = random.choice(self.wordsEnglish)
		else:
			w = random.choice(self.wordsRussian)

		word = Word(w)

		self.players[playerId].ResetState()

		self.UpdateWord(message, word)

		print(w)

		self.SendMessage(message.chat.id, self.players[message.chat.id].localization.launchingGame, True,  self.defaultKeyboard)

		reply = self.SendMessage(message.chat.id, self.players[message.chat.id].localization.makeAGuess.substitute(word=word.GetMask()), True)
		self.players[playerId].meaningfulMessages['showWord'] = reply

		self.players[playerId].RefreshAttempts()
		attempts = self.players[playerId].attempts
		reply = self.SendMessage(message.chat.id, self.players[message.chat.id].localization.attemptsLeft.substitute(attempts=attempts), True)
		self.players[playerId].meaningfulMessages['attempts'] = reply

		self.ShowCurrentLetterAttempts(message)

		self.UpdateState(message)

		self.bot.register_next_step_handler(reply, self.PlayRound)

	def StartPlaying(self, message):
		reply = message.text.lower()

		self.AddMessageToDelete(message)

		if (self.ValidateAffirmativeAnswer(reply)):
			self.InitializeGame(message)
		else:
			self.SendMessage(message.chat.id, self.players[message.chat.id].localization.playReject, True, self.defaultKeyboard)

	def RestartGame(self, message):
		self.DeleteAllPreviousMessages(message)

		self.SendMessage(message.chat.id, self.players[message.chat.id].localization.restartGame, True)

		self.InitializeGame(message)

	def StopGame(self, message):
		self.SendMessage(message.chat.id, self.players[message.chat.id].localization.stopGame, True)

	def PlayRound(self, message):
		reply = self.HandleGuess(message)

		self.DeleteUserMessage(message)

		# Ignore ended dialogues. They return None
		if (isinstance(reply, Message)):
			self.bot.register_next_step_handler(reply, self.PlayRound)
		# None means the game is over and has to be marked as played
		elif (reply is None):
			playerId = message.chat.id
			self.databaseManager.IncrementGamesPlayed(playerId)

	def HandleGuess(self, message):
		guess = message.text.lower()
		playerId = message.chat.id

		reply = self.players[playerId].meaningfulMessages['showWord']	

		if (guess == "/stop"):
			self.StopGame(message)
			return
		elif (guess == '/start'):
			self.RestartGame(message)
			return

		guessType = self.DetermineGuessType(guess)

		if (guessType == GuessType.Error):
			return self.SendMessage(message.chat.id, self.players[message.chat.id].localization.invalidGuessReply, True)

		if (guessType == GuessType.Letter):
			reply = self.HandleLetterGuess(guess, message)
		elif (guessType == GuessType.Word):
			reply = self.HandleWordGuess(guess, message)

		return reply

	def HandleLetterGuess(self, guess, message):
		playerId = message.chat.id
		word = self.players[playerId].word.GetWord()

		reply = self.players[playerId].meaningfulMessages['showWord']

		# Already guessed this letter
		if (guess in self.players[playerId].word.letterAttempts):
			#return self.SendMessage(message.chat.id, self.letterDuplicate, True)
			return reply

		# Remembering the guess
		self.players[playerId].word.AddLetterAttempt(guess)

		# Updating the letters that the user guessed
		m = self.players[playerId].meaningfulMessages['letterAttempts']
		w = self.players[playerId].word
		self.UpdateMessage(m, self.players[message.chat.id].localization.currentLetters.substitute(letters=' '.join(w.letterAttempts)))

		result = self.CheckLetter(guess, word)

		# Guess succeeded
		if (result):
			newMask = self.players[playerId].word.OpenLetters(result)

			showWordMessage = self.players[playerId].meaningfulMessages['showWord']
			reply = self.UpdateMessage(showWordMessage, self.players[message.chat.id].localization.makeAGuess.substitute(word=newMask))

			if (self.players[playerId].word.IsGuessed()):
				self.databaseManager.IncrementGamesWon(playerId)
				self.SendMessage(message.chat.id, self.players[message.chat.id].localization.correctWordGuess.substitute(name=self.players[playerId].name), True)
				return

			# reply = self.SendMessage(message.chat.id, self.correctLetterGuess.substitute(name=self.players[playerId].name, newMask=newMask), True)

		# Guess failed
		else:
			reply = self.HandleGuessFailed(playerId, message)

		return reply

	def HandleWordGuess(self, guess, message):
		playerId = message.chat.id
		word = self.players[playerId].word.GetWord()

		result = self.CheckWord(guess, word)

		# Guess succeeded
		if (result):
			self.databaseManager.IncrementGamesWon(playerId)
			self.RevealWord(message)
			self.SendMessage(message.chat.id, self.players[message.chat.id].localization.correctWordGuess.substitute(name=self.players[playerId].name), True)
			return

		# Guess failed
		else:
			reply = self.HandleGuessFailed(playerId, message)

		return reply

	def HandleGuessFailed(self, playerId, message):
		stillPlaying = self.players[playerId].DecreaseAttempts()

		self.UpdateState(message)

		attempts = self.players[playerId].attempts
		attemptsMessage = self.players[playerId].meaningfulMessages['attempts']

		reply = self.UpdateMessage(attemptsMessage, self.players[message.chat.id].localization.attemptsLeft.substitute(attempts=attempts))

		if (not stillPlaying):
			self.SendMessage(message.chat.id, self.players[message.chat.id].localization.noAttempts, True)

			self.RevealWord(message)
			return

		return reply

	def RevealWord(self, message):
		playerId = message.chat.id
		word = self.players[playerId].word.GetWord()

		showWordMessage = self.players[playerId].meaningfulMessages['showWord']
		self.UpdateMessage(showWordMessage, self.players[message.chat.id].localization.makeAGuess.substitute(word=word))

	def ShowCurrentLetterAttempts(self, message):
		playerId = message.chat.id
		word = self.players[playerId].word
 
		m = self.SendMessage(message.chat.id, self.players[message.chat.id].localization.currentLetters.substitute(letters=' '.join(word.letterAttempts)), True)
		self.players[playerId].meaningfulMessages['letterAttempts'] = m

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

	def HandleChangeLanguage(self, message):
		playerId = message.chat.id

		if (message.text == "English"):
			self.players[playerId].localization = EnglishLocalization()
		elif (message.text == "Русский"):
			self.players[playerId].localization = RussianLocalization()
		else:
			self.SendMessage(playerId, self.players[message.chat.id].localization.availableLanguages, True, self.defaultKeyboard)
			return

		self.SendMessage(playerId, self.players[message.chat.id].localization.successfullyChangedLanguage, True, self.defaultKeyboard)

	def ValidateAffirmativeAnswer(self, text: str) -> bool:
		if (text == "yes" or text == "да"):
			return True

		return False

	def LoadFiles(self):
		self.ReadFileLower(self.wordsRussianFile, self.wordsRussian)
		self.ReadFileLower(self.wordsEnglishFile, self.wordsEnglish)

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

	def SubstituteLeaderboardStats(self, message, stats):
		return self.players[message.chat.id].localization.leaderboardMessage.substitute(name=stats[0], wins=stats[1], played=stats[2])

	def Run(self):
		self.bot.infinity_polling()

	
hangman = Hangman()
hangman.Run()