from string import Template
from dataclasses import dataclass

@dataclass
class RussianLocalization:
    welcomeMessage: str = """
Привет! Я Hangman bot, разработанный @georgygunkin.
Правила тут -> /rules
Мы можем прямиком начать играть -> /start
Либо мы можем, для начала, познакомиться -> /aboutme
Ты можешь поменять язык на Английский -> /language
Ты можешь посмотреть рекорд других игроков -> /leaderboard	
"""

    playMessage: str = "Ну, давай играть! Готов?"

    playReject: str = "Ок! Стало быть, мы не играем. Если передумаешь, дай мне знать -> /start"

    rulesMessage: str = """
Правила достаточно просты. Я даю тебе слово, а ты его угадываешь.
У тебя есть ровно 10 попыток
Не угадал букву или слово целиком -> -1 попытка.
Если попытки закончились, игра окончена.
"""

    changeLanguage: str = "Без проблем, я многоязычный. Выбери язык, на который хочешь переключить"

    successfullyChangedLanguage: str = "Успешно сменил язык"

    availableLanguages: str = "Единственные доступные языки - Русский и English"

    leaderboardMessage: str = Template("$name | Соотношение побед: $wins/$played")

    launchingGame: str = "Запускаю игру..."

    aboutMeMessage: str = """
Ну, давай познакомимся.
Как мне к тебе обращаться?
"""

    invalidGuessReply: str = """
У нас тут только Русские слова.

Попробуй угадать всё слово или одну букву.
Если хочешь закончить игру, нажми /stop
Если хочешь перезапустить игру, нажми /start
"""

    correctWordGuess: str = Template("""
Слово угадано! Молодец, $name! Если хочешь ещё раз сыграть, нажми /start
""")

    correctLetterGuess: str = Template("""
Угадал букву! Молодец, $name!
$newMask
""")

    letterNotFound: str = "Этой буквы нет, хочешь попробовать еще?"

    incorrectWordGuess: str = "Нет, не угадал слово. Хочешь попробовать еще?"

    letterDuplicate: str = "Ты уже предлагал эту букву!"

    changedName: str = Template("Хорошо, теперь буду обращаться к тебе так: $name.")

    makeAGuess: str = Template("Загаданное слово:\n$word")

    attemptsLeft: str = Template("Попыток осталось: $attempts")

    restartGame: str = "Вижу ты хочешь перезапустить игру, почему бы и нет!"

    stopGame: str = "Останавливаю игру."

    currentLetters: str = Template("Текущие попытки букв: $letters")

    noAttempts: str = "Попыток не осталось, ты проиграл! Если хочешь сыгать ещё раз, нажми /start"


@dataclass
class EnglishLocalization:
    welcomeMessage: str = """
Hello! I am the Hangman bot developed by @georgygunkin.
The rules are here -> /rules
We can go ahead and start playing the game -> /start
Or we can get to know eachother first -> /aboutme
You can change the language to Russian -> /language
You can view the scores of other players -> /leaderboard
"""

    playMessage: str = "Let's play then! Are you ready?"

    playReject: str = "Okay! I guess we are not playing then. If you change your mind, let me know -> /start"

    rulesMessage: str = """
The rules are simple. I give you a word and you have to guess it.
You have 10 attempts
If you miss a word or a letter -> -1 attempt.
When you run out of attempts, the game is over.
"""

    successfullyChangedLanguage: str = "Successfully changed the language"

    availableLanguages: str = "The only available languages are Русский and English"

    changeLanguage: str = "Sure, I am multilingual, please pick a language you wish to switch to"

    leaderboardMessage: str = Template("$name | Win Ratio: $wins/$played")

    launchingGame: str = "Launching the game..."

    aboutMeMessage: str = """
I see you want to tell me about yourself.
What is your name?
"""

    invalidGuessReply: str = """
We have only English words here.

Please, guess the whole word or just a letter.
If you want to stop playing, press /stop
If you want to restart game, press /start
"""

    correctWordGuess: str = Template("""
Word guessed correctly! Nice job, $name! If you want to play again, press /start
""")

    correctLetterGuess: str = Template("""
Letter guessed correctly! Nice job, $name!
$newMask
""")

    letterNotFound: str = "Letter is not found! Wanna try again?"

    incorrectWordGuess: str = "Incorrect word guess! Wanna try again?"

    letterDuplicate: str = "You've already guessed this letter!"

    changedName: str = Template("I shall now be calling you $name.")

    makeAGuess: str = Template("Word to guess:\n$word")

    attemptsLeft: str = Template("Attempts left: $attempts")

    restartGame: str = "I see you want to restart game, sure!"

    stopGame: str = "Stopping the game per your request."

    currentLetters: str = Template("Currently attempted letters: $letters")

    noAttempts: str = "No attempts left, you've lost! If you want to play again, press /start"
