from enum import Enum
from dataclasses import dataclass

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

	def Next(self) -> None:
		if (self.state.value == self.maxState):
			self.state = State.state_0
		else:
			self.state = State(self.state.value + 1)

	def Reset(self) -> None:
		self.state = State.state_0
