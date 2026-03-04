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

# GPIO setup voor kleine knop
button = digitalio.DigitalInOut(board.GP28)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

# GPIO setup voor grote knop
big_button = digitalio.DigitalInOut(board.GP1)
big_button.direction = digitalio.Direction.INPUT
big_button.pull = digitalio.Pull.UP

# LED/buzzer op één pin
led_buzzer = digitalio.DigitalInOut(board.GP3)
led_buzzer.direction = digitalio.Direction.OUTPUT

# # # # # # # # # # # # # # # #
# Letter/Morse instellingen   #
# # # # # # # # # # # # # # # #

UNIT = 0.2
INTRAGAP = 1 * UNIT      # korte pauze tussen symbolen
CHARGAP = 3 * UNIT       # pauze tussen letters
WORDGAP = 7 * UNIT       # pauze tussen woorden

KORT = 1 * UNIT          # punt
LANG = 3 * UNIT          # streep

# Morse code alfabet
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

# Omzetten van morse naar letter
MORSE_REVERSED = {v: k for k, v in MORSE.items()}

# # # # # # # # # # # # # # # # # # 
# Basis functies voor LED/buzzer  #
# # # # # # # # # # # # # # # # # #

def ON(duration):
    led_buzzer.value = True
    time.sleep(duration)
    led_buzzer.value = False

def GAP(duration):
    time.sleep(duration)

def FKORT():
    ON(KORT)
    GAP(INTRAGAP)

def FLANG():
    ON(LANG)
    GAP(INTRAGAP)

def CHAR_GAP():
    GAP(CHARGAP)

def WORD_GAP():
    GAP(WORDGAP)

def play_morse(letter):
    code = MORSE[letter]
    for symbol in code:
        check_menu_hold()  # altijd checken of menu moet, ook tijdens het voorbeeld
        if symbol == ".":
            FKORT()
        elif symbol == "-":
            FLANG()
    CHAR_GAP()

# # # # # # # # # # # # # # # # #
# Functies voor letters oefenen # 
# # # # # # # # # # # # # # # # #

def random_letter():
    return random.choice(list(MORSE.keys()))

def LCD_print(letter):
    lcd.clear()
    lcd.message = f"{letter} :  {MORSE[letter]}"
    play_morse(letter)

def knop_checken(letter):
    knop_morse = []
    code = MORSE[letter]
    lengte = len(code)

    while len(knop_morse) < lengte:
        check_menu_hold()
        if not big_button.value:
            press_time = time.time()
            led_buzzer.value = True
            while not big_button.value:
                time.sleep(0.01)
            led_buzzer.value = False
            duration = time.time() - press_time
            if duration < KORT:
                knop_morse.append(".")
            else:
                knop_morse.append("-")
            lcd.cursor_position(0, 1)
            lcd.message = "".join(knop_morse)
            time.sleep(0.2)

    if "".join(knop_morse) == code:
        lcd.clear()
        lcd.message = "goed gedaan!\nvolgende letter"
    else:
        lcd.clear()
        lcd.message = f"fout, goed was:\n{code}"
    time.sleep(1)

def letters_oefenen():
    while True:
        check_menu_hold()
        letter = random_letter()
        LCD_print(letter)
        knop_checken(letter)

def morsecode_oefenen():
    while True:
        check_menu_hold()
        letter = random_letter()
        lcd.clear()
        lcd.message = letter
        knop_checken(letter)

# # # # # # # # # # # # # # # #
# Functies voor zelf typen    #
# # # # # # # # # # # # # # # #

def lees_morse_letter():
    knop_morse = []
    last_input_time = time.time()
    
    # vertraging extra om snelle klikken niet te interpreteren als losse letters
    LETTER_TIMEOUT = CHARGAP + 0.15  # iets langer dan CHARGAP, is makkelijker

    while True:
        check_menu_hold()
        if not big_button.value:
            press_time = time.time()
            led_buzzer.value = True
            while not big_button.value:
                time.sleep(0.01)
            led_buzzer.value = False
            duration = time.time() - press_time
            if duration < KORT:
                knop_morse.append(".")
            else:
                knop_morse.append("-")
            lcd.clear()
            lcd.message = "".join(knop_morse)
            last_input_time = time.time()
            time.sleep(0.15)  # kleine pauze 

        # einde letter wacht iets langer dan CHARGAP
        if knop_morse and (time.time() - last_input_time > LETTER_TIMEOUT):
            return "".join(knop_morse)

        # spatie / wordgap
        if not knop_morse and (time.time() - last_input_time > WORDGAP):
            return "SPACE"

def zelf_typen():
    lcd.clear()
    lcd.message = "Typ morse..."
    woord = ""

    while True:
        # eerst morse input lezen
        code = lees_morse_letter()

        # Verwerking van de morse input naar letter/spatie
        if code == "SPACE":
            if not woord.endswith(" "):
                woord += " "
        else:
            try:
                letter = MORSE_REVERSED.get(code, "?")  # fallback voor onbekende code
                woord += letter
            except Exception as e:
                woord += "?"
        lcd.clear()
        lcd.message = woord[-16:]  # laatste 16 tekens tonen

        # Kleine knop = clear, lange knop = menu
        if not button.value:
            press_start = time.time()
            while not button.value:
                time.sleep(0.01)
            press_duration = time.time() - press_start

            if press_duration < 1:  # korte druk = clear
                woord = ""
                lcd.clear()
                lcd.message = "clear"
                time.sleep(0.5)
                lcd.clear()
                lcd.message = "Typ morse..."
            else:  # lange druk = menu
                return  # terug naar menu

# # # # # # # # # # # # # # # # # # # # # # # #
# Functie om altijd terug naar menu te kunnen #
# # # # # # # # # # # # # # # # # # # # # # # #

def check_menu_hold():
    if not button.value:
        start = time.time()
        while not button.value:
            time.sleep(0.01)
            if time.time() - start > 1.2:
                lcd.clear()
                lcd.message = "Menu..."
                time.sleep(0.3)
                raise SystemExit
    return False

# # # # # # # # # # # # # # # #
# Menu om modus te kiezen     #
# # # # # # # # # # # # # # # #

def menu():
    opties = [
        ("Letters oefenen", letters_oefenen),
        ("Morse oefenen", morsecode_oefenen),
        ("Zelf typen", zelf_typen)
    ]

    index = 0

    while True:
        lcd.clear()
        lcd.message = "Modus kiezen:\n" + opties[index][0]

        while True:
            # scrollen
            if not button.value:
                time.sleep(0.15)
                if not button.value:
                    index = (index + 1) % len(opties)
                    while not button.value:
                        time.sleep(0.01)
                    break
            # selecteren
            if not big_button.value:
                time.sleep(0.15)
                if not big_button.value:
                    while not big_button.value:
                        time.sleep(0.01)
                    try:
                        opties[index][1]()
                    except SystemExit:
                        pass
                    break
            time.sleep(0.05)

menu()
