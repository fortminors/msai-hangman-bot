from typing import List

class Word():
	def __init__(self, word: str):
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

	def CreateWordMask(self, word: str) -> List[str]:
		length = len(word)
		return [self.q for _ in range(length)]

	def GetMask(self) -> str:
		return ''.join(self.mask)

	def GetWord(self) -> str:
		return ''.join(self.word)
		
	def IsGuessed(self) -> bool:
		return self.guessed