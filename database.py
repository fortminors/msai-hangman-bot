from pony.orm import Database, Required, PrimaryKey, db_session

class DatabaseManager:

    db = Database()

    class Player(db.Entity):
        id = PrimaryKey(int)
        name = Required(str)
        gamesPlayed = Required(int)
        gamesWon = Required(int)

    def __init__(self):
        self.db.bind(provider='sqlite', filename='players.sqlite', create_db=True)
        self.db.generate_mapping(create_tables=True)

    @db_session
    def PlayerExists(self, id):
        return self.Player.exists(id=id)

    @db_session
    def GetPlayerIfExists(self, id) -> Player | None:
        return self.Player.get(id=id)

    @db_session
    def AddPlayer(self, id, name):
        if (not self.Player.exists(id=id)):
            self.Player(id=id, name=name, gamesPlayed=0, gamesWon=0)

    @db_session
    def ChangePlayerName(self, id, name):
        self.Player[id].name = name

    @db_session
    def IncrementGamesPlayed(self, id):
        self.Player[id].gamesPlayed += 1

    @db_session
    def IncrementGamesWon(self, id):
        self.Player[id].gamesWon += 1

    @db_session
    def GetWinPercentage(self, id):
        played = self.Player[id].gamesPlayed
        won = self.Player[id].gamesWon

        return round((won / played) * 100)