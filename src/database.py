from pony.orm import Database, Required, PrimaryKey, db_session, select, desc

from typing import List, Tuple

class DatabaseManager:

    db = Database()

    class Player(db.Entity):
        id = PrimaryKey(int)
        name = Required(str)
        gamesPlayed = Required(int)
        gamesWon = Required(int)
        winPercentage = Required(int)

    def __init__(self):
        self.db.bind(provider='sqlite', filename='players.sqlite', create_db=True)
        self.db.generate_mapping(create_tables=True)

    @db_session
    def PlayerExists(self, id: int) -> bool:
        return self.Player.exists(id=id)

    @db_session
    def GetPlayerIfExists(self, id: int) -> Player | None:
        return self.Player.get(id=id)

    @db_session
    def AddPlayer(self, id: int, name: str) -> None:
        if (not self.Player.exists(id=id)):
            self.Player(id=id, name=name, gamesPlayed=0, gamesWon=0, winPercentage=0)

    @db_session
    def ChangePlayerName(self, id: int, name: str) -> None:
        self.Player[id].name = name

    @db_session
    def IncrementGamesPlayed(self, id: int) -> None:
        self.Player[id].gamesPlayed += 1
        self.UpdateWinPercentage(id)

    @db_session
    def IncrementGamesWon(self, id: int) -> None:
        self.Player[id].gamesWon += 1
        self.UpdateWinPercentage(id)

    @db_session
    def UpdateWinPercentage(self, id: int) -> None:
        winPercentage = self.GetWinPercentage(id)
        self.Player[id].winPercentage = winPercentage

    @db_session
    def GetWinPercentage(self, id: int) -> int:
        won = self.Player[id].gamesWon
        played = self.Player[id].gamesPlayed

        winPercentage = 100

        if (played > 0):
            winPercentage = round((won / played) * 100)

        return winPercentage

    @db_session
    def GetLeaderboard(self, amount: int) -> List[Tuple]:
        return select((p.name, p.gamesWon, p.gamesPlayed) for p in self.Player).order_by(lambda: desc(p.winPercentage))[:amount]
