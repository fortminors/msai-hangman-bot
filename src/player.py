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

	def ChangeWord(self, newWord: str) -> None:
		self.word = newWord

	def ChangeName(self, name: str) -> None:
		self.name = name

	def ResetState(self) -> None:
		self.stateManager.Reset()

	def NextState(self) -> None:
		self.stateManager.Next()

	def CurrentState(self) -> str:
		return self.stateManager.state.name

	def AddMessageToDelete(self, message: Message) -> None:
		self.deleteMessageCandidates.add(message)

	def RemoveMessageFromDelete(self, message: Message) -> None:
		if (message in self.deleteMessageCandidates):
			self.deleteMessageCandidates.remove(message)

	def GetMessagesToDelete(self) -> Set[Message]:
		return self.deleteMessageCandidates

	def RefreshAttempts(self) -> None:
		self.attempts = 10

	def ChangeLocalization(self, localization: EnglishLocalization | RussianLocalization) -> None:
		self.localization = localization

	# Returns True if there are still attempts left
	def DecreaseAttempts(self) -> bool:
		self.attempts -= 1

		if (self.attempts <= 0):
			return False
		
		return True