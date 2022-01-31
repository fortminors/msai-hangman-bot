from typing import Set, Dict
from dataclasses import dataclass

from telebot.types import Message

from localization import EnglishLocalization, RussianLocalization
from state import StateManager
from word import Word

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