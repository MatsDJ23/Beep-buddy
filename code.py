import time
import random
import digitalio
import board
import adafruit_character_lcd.character_lcd as characterlcd

# # # # # # # # # # # # # # # #
# Preperation/voorbereiding   #
# # # # # # # # # # # # # # # #

# LCD pins
lcd_rs = digitalio.DigitalInOut(board.GP16)
lcd_en = digitalio.DigitalInOut(board.GP17)
lcd_d4 = digitalio.DigitalInOut(board.GP18)
lcd_d5 = digitalio.DigitalInOut(board.GP19)
lcd_d6 = digitalio.DigitalInOut(board.GP20)
lcd_d7 = digitalio.DigitalInOut(board.GP21)

# LCD setup
lcd_columns = 16
lcd_rows = 2
lcd = characterlcd.Character_LCD_Mono(
    lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows
)

# GPIO setup voor button
button = digitalio.DigitalInOut(board.GP28)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

# GPIO setup voor grote knop
big_button = digitalio.DigitalInOut(board.GP1)
big_button.direction = digitalio.Direction.INPUT
big_button.pull = digitalio.Pull.UP

# led en buzzer zitten op dezelfde gpio pin
led_buzzer = digitalio.DigitalInOut(board.GP3)
led_buzzer.direction = digitalio.Direction.OUTPUT

# Letter instellingen
UNIT = 0.2
INTRAGAP = 1 * UNIT      
CHARGAP =  3 * UNIT
WORDGAP =  7 * UNIT

KORT = 1 * UNIT        # .
LANG = 3 * UNIT        # -

# Morse code library/alfabet
MORSE = {
    "A": ".-",    "B": "-...",  "C": "-.-.",  "D": "-..",
    "E": ".",     "F": "..-.",  "G": "--.",   "H": "....",
    "I": "..",    "J": ".---",  "K": "-.-",   "L": ".-..",
    "M": "--",    "N": "-.",    "O": "---",   "P": ".--.",
    "Q": "--.-",  "R": ".-.",   "S": "...",   "T": "-",
    "U": "..-",   "V": "...-",  "W": ".--",   "X": "-..-",
    "Y": "-.--",  "Z": "--..",

    "1": ".----", "2": "..---", "3": "...--", "4": "....-",
    "5": ".....", "6": "-....", "7": "--...", "8": "---..",
    "9": "----.", "0": "-----",

    ".": ".-.-.-", ",": "--..--", "?": "..--..", "'": ".----.",
    "!": "-.-.--", "/": "-..-.",  "(": "-.--.",  ")": "-.--.-",
    "&": ".-...",  ":": "---...", ";": "-.-.-.", "=": "-...-",
    "+": ".-.-.",  "-": "-....-", "_": "..--.-", "\"": ".-..-.",
    "$": "...-..-","@": ".--.-."
}
# Het morse code alfabet is gemaakt met chatgpt omdat het anders heel veel hetzelfde zou zijn

# # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Begin van de echte code                           #
# # # # # # # # # # # # # # # # # # # # # # # # # # #

# Function voor random letter
def random_letter():
    return random.choice([
        "A","B","C","D","E","F","G","H","I","J","K","L","M",
        "N","O","P","Q","R","S","T","U","V","W","X","Y","Z",
        "!","?","0","1","2","3","4","5","6","7","8","9","_"
    ])

# functions voor het voorbeeld, dit bliept de letter en zet het op de lcd
def LCD_print(letter):
    lcd.clear()
    lcd.message = f"{letter}\n{MORSE[letter]}"
    play_morse(letter)

def ON(duration):
    led_buzzer.value = True
    time.sleep(duration)
    led_buzzer.value = False

def GAP(duration):
    time.sleep(duration)

def FKORT():      # kort signaal
    ON(KORT)
    GAP(INTRAGAP)

def FLANG():      # lang signaal
    ON(LANG)
    GAP(INTRAGAP)

def CHAR_GAP():
    GAP(CHARGAP)

def WORD_GAP():
    GAP(WORDGAP)

def play_morse(letter):
    code = MORSE[letter]

    for symbol in code:
        if symbol == ".":
            FKORT()
        elif symbol == "-":
            FLANG()

    CHAR_GAP()

# functions voor voorbeeld tot hier # # # # # # # # # # # # # # # # # # #

# function voor wat jij invoert
def knop_checken(letter):
    knop_morse = []                       # lijst om de ingevoerde symbolen op te slaan
    code = MORSE[letter]                  # de morse-code van de letter
    lengte = len(code)                    # hoeveel symbolen er ingevoerd moeten worden

    # zolang we nog niet alle symbolen hebben gekregen
    while len(knop_morse) < lengte:
        if not big_button.value:          # knop wordt ingedrukt
            press_time = time.time()      # start tijd meten

            # LED/buzzer aan zolang ingedrukt
            led_buzzer.value = True

            # wacht tot de knop losgelaten wordt
            while not big_button.value:
                time.sleep(0.01)

            # los = LED uit
            led_buzzer.value = False

            # bereken duur van de druk
            duration = time.time() - press_time

            # bepaal kort of lang signaal
            if duration < (KORT + LANG) / 2:   # korter dan grens "."
                knop_morse.append(".")
            else:                             # langer dan grens "-"
                knop_morse.append("-")

            # bovenste rij tonen wat er tot nu toe is ingedrukt
            lcd.cursor_position(0, 0)
            lcd.message = "".join(knop_morse)

            time.sleep(0.2)  # kleine pauze tussen drukken

    # Als alle symbolen zijn ingevoerd vergelijken
    if "".join(knop_morse) == code:
        lcd.clear()
        lcd.message = "goed gedaan!\nvolgende letter"
    else:
        lcd.clear()
        lcd.message = "helaas, dat \n klopt niet"
        knop_checken()

    # korte pauze zodat gebruiker het resultaat kan zien
    time.sleep(1)

# de main loop voor alles
while True:
    if not button.value:
        letter = random_letter()
        LCD_print(letter)
        time.sleep(0.1)
        knop_checken(letter)

        # klik op de knop ob het breadbord om script te starten
        while not button.value:
            time.sleep(0.1)

