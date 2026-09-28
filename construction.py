from dataclasses import fields
import os, random

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def draw():
    print("Xx--------------------Xx")

run = True
menu = True
play = False
rules = False
key = False
fight = False
standing = True
buy = False
speak = False
boss = False

name = ""
HP = 100
MAXHP = HP
ATK = 10
pot = 1
elix = 0
gold = 0
x = 0
y = 0

biom =  {
    "plains": {
        "t":"PLAINS",
        "e": True
    },   
    "fields": {
        "t":"FIELDS",
        "e": False
    },
    "forest": {
        "t":"FOREST",
        "e": True
    },
    "shop": {
        "t":"SHOP",
        "e": False
    },
    "cave": {
        "t":"CAVE",
        "e": True
    },
    "mayor": {
        "t":"MAYOR",
        "e": False
    }
}

e_list = ["Orc", "Werewolf", "Giant Worm"]

mobs = {
    "Orc": {
        "HP": 20,
        "ATK": 5,
        "GOLD": 10
    },
    "Werewolf": {
        "HP": 30,
        "ATK": 10,
        "GOLD": 20
    },
    "Giant Worm": {
        "HP": 50,
        "ATK": 15,
        "GOLD": 30
    },
    "Dragon": {
        "HP": 100,
        "ATK": 20,
        "GOLD": 50
    }
}



map  =  [
            ["plains", "plains", "plains", "plains", "plains", "plains", "plains", "plains", "plains", "plains"],
            ["plains", "forest", "forest", "forest", "forest", "forest", "forest", "forest", "forest", "plains"],
            ["plains", "forest", "plains", "plains", "plains", "shop", "plains", "plains", "forest", "plains"],
            ["plains", "forest", "plains", "forest", "forest", "forest", "plains", "plains", "forest", "cave"],
            ["plains", "forest", "shop", "forest", "plains", "forest", "plains", "plains", "forest", "plains"],
            ["plains", "forest", "plains", "forest", "plains", "forest", "plains", "plains", "forest", "plains"],
            ["plains", "forest", "plains", "shop", "plains", "forest", "plains", "plains", "forest", "plains"],
            ["plains", "forest", "plains", "forest", "plains", "shop", "plains", "plains", "forest", "plains"],
            ["plains", "forest", "fields", "forest", "fields", "forest", "fields", "fields", "fields", "plains"],
            ["plains", "plains", "plains", "plains", "plains", "mayor", "plains", "plains", "plains", "plains"]
        ]

y_len = len(map)-1
x_len = len(map[0])-1

current_tile = map[y][x]
print(f"Current tile: {current_tile}")
name_of_tile = biom[current_tile]["t"]
print(f"Name of tile: {name_of_tile}")
enemy_tile = biom[current_tile]["e"]
print(f"Enemy present: {enemy_tile}")


def save():
    data = [
        name,
        str(HP),
        str(ATK),
        str(pot),
        str(elix),
        str(gold),
        str(x),
        str(y)
    ]

    f = open("load.txt" , "w")
    for item in data:
        f.write(item + "\n")
    f.close()

def heal(amount):
    global HP, MAXHP
    HP += amount
    if HP > MAXHP:
        HP = MAXHP
        print("You healed for " + str(amount) + " HP!")
    else:
        print("You healed for " + str(amount) + " HP!")
        input("> ")
def shop():
    global gold, pot, elix, ATK, buy
    while buy:
        clear()
        print("Welcome to the shop!")
        print("You have " + str(gold) + " gold.")
        print("1 - Buy Potion (10 gold)")
        print("2 - Buy Elixir (25 gold)")
        print("3 - Upgrade ATK by 1 (50 gold)")
        print("4 - Exit Shop")
        choice = input("# ")
        if choice == "1":
            if gold >= 10:
                pot += 1
                gold -= 10
                print("You bought a potion!")
                input("> ")
            else:
                print("You don't have enough gold!")
                input("> ")
        elif choice == "2":
            if gold >= 25:
                elix += 1
                gold -= 25
                print("You bought an elixir!")
                input("> ")
            else:
                print("You don't have enough gold!")
                input("> ")
        elif choice == "3":
            if gold >= 50:
                ATK += 1
                gold -= 50
                print("You upgraded your attack!")
                input("> ")
            else:
                print("You don't have enough gold!")
                input("> ")
        elif choice == "4":
            buy = False
def mayor():
    global speak, key
    speak = True
    while speak:
        clear()
        print("Mayor: Hello, hero! I have a quest for you.")
        print("Mayor: Please defeat the Dragon in the cave to save our village.")
        print("1 - Accept Quest")
        print("2 - Decline Quest")
        choice = input("# ")
        if choice == "1":
            print("Mayor: Thank you, hero! Here is a key to the cave.")
            key = True
            input("> ")
            speak = False
        elif choice == "2":
            print("Mayor: I see, hero. Please come back if you change your mind.")
            input("> ")
            speak = False
def cave():
    global boss, key, fight
    while boss:
        clear()
        print("You enter the cave and face the Dragon!")
        if key:
            print("1 - Fight the Dragon")
        print("2 - Leave the cave")
        choice = input("# ")
        if choice == "1":
            if not key:
                print("You need a key to fight the Dragon!")
                input("> ")
                boss = False
                return
            else:
                fight = True
                battle()
                if HP > 0:
                    print("Congratulations! You have defeated the Dragon and saved the village!")
                    input("> ")
                    boss = False
                    key = False
                else:
                    print("You have been defeated by the Dragon. Game over!")
                    input("> ")
                    boss = False
        elif choice == "2":
            print("You leave the cave.")
            input("> ")
            boss = False
def battle():
    global fight, play, run, HP, pot, elix, gold, menu, boss
    if not boss:
        enemy = random.choice(e_list)
    else:
        enemy = "Dragon"
    hp = mobs[enemy]["HP"]
    hp_max = hp
    atk = mobs[enemy]["ATK"]
    g = mobs[enemy]["GOLD"]
    print("You are in a battle with a " + enemy + "!")
    
    while fight:
        clear()
        draw()
        if hp > 0:
            print(enemy + "s HP: " + str(hp) + "/" + str(hp_max))
        if HP > 0:
            print(name + "'s HP: " + str(HP) + "/" + str(MAXHP))
        print("POTIONS: " + str(pot))
        print("ELIXIRS: " + str(elix))
        draw()
        print("1 - ATTACK")
        if pot > 0:
            print("2 - USE POTION")
        if elix > 0:
            print("3 - USE ELIXIR")
        draw()

        choice = input("# ")
        if choice == "1":
            hp -= ATK
            print("You attacked the " + enemy + " for " + str(ATK) + " damage!")
            input("> ")
            if hp <= 0:
                hp = 0
                print("You defeated the " + enemy + "!")
                gold += g
                print("You gained " + str(g) + " gold!")
                if random.randint(1, 100) <= 20:
                    pot += 1
                    print("You found a potion!")
                if enemy == "Dragon":
                    print("Congratulations! You defeated the dragon!")
                    elix += 1
                    print("You found 1 elixir!")
                    boss = False
                input("> ")
                clear()
                fight = False
            if hp > 0:
                HP -= atk
                print("The " + enemy + " attacked you for " + str(atk) + " damage!")
                input("> ")
                if HP <= 0:
                    HP = 0
                    print("You have been defeated by the " + enemy + "!")
                    input("> ")
                    fight = False
                    play = False
                    menu = True
                    print("Game over!")
        elif choice == "2":
            if pot > 0:
                heal(20)
                pot -= 1
                print("You used a potion and restored 20 HP!")
                input("> ")
            else:
                print("You don't have any potions!")
                input("> ")
        elif choice == "3":
            if elix > 0:
                heal(50)
                elix -= 1
                print("You used an elixir and restored 50 HP!")
                input("> ")
            else:
                print("You don't have any elixirs!")
                input("> ")

while run:
    while menu:
        clear()
        print("1, NEW GAME")
        print("2, LOAD GAME")
        print("3, RULES")
        print("4, EXIT")

        choice = input("# ")

        if choice == "1":
            name = input("What's your name, hero? ")
            clear()

            while name == "":
                name = input("Please enter a valid name: ")
                clear()

            print(f"Welcome, {name}!")
            menu = False
            play = True
            HP = 100
            ATK = 10
            pot = 1
            elix = 0
            gold = 0
            x = 0
            y = 0

        elif choice == "2":
            try:
                f = open("load.txt", "r")
                data = f.readlines()
                name = data[0].strip()
                HP = int(data[1].strip())
                ATK = int(data[2].strip())
                pot = int(data[3].strip()) if len(data) > 3 else 1
                elix = int(data[4].strip()) if len(data) > 4 else 0
                gold = int(data[5].strip()) if len(data) > 5 else 0
                x = int(data[6].strip()) if len(data) > 6 else 0
                y = int(data[7].strip()) if len(data) > 7 else 0
                f.close()
                clear()

                if HP > 0:
                    print(f"Welcome back, {name}!")
                    input("> ")
                    menu = False
                    play = True
                else:
                    print("You have no HP left, you cannot load the game.")
                    input("> ")
            except FileNotFoundError:
                clear()
                print("No saved game found")
                input("> ")
                menu = True
        elif choice == "3":
            print("Rules: \n- You have HP and ATK stats.\n- Make choices to progress in the game.")
            input("> ")
        elif choice == "4":
            run = False
            menu = False
            play = False
    
    while play:
        save()
        clear()

        if not standing:
            if biom[map[y][x]]["e"] == True:
                if random.randint(1, 100) <= 30:
                    fight = True
                    battle()
        draw()

        if play:
            print("LOCATION: " + biom[map[y][x]]["t"])
            print("NAME: " + name)
            print("HP: " + str(HP) + "/" + str(MAXHP))
            print("ATK: " + str(ATK))
            print("POTIONS: " + str(pot))
            print("ELIXIRS: " + str(elix))
            print("GOLD: " + str(gold))
            print("COORDINATES: " + str(x) + ", " + str(y))
            draw()
            print("0 - SAVE AND QUIT")
            if y > 0:
                print("w - MOVE UP")
            if y < y_len:
                print("s - MOVE DOWN")
            if x > 0:
                print("a - MOVE LEFT")
            if x < x_len:
                print("d - MOVE RIGHT")
            if pot > 0:
                print("p - USE POTION")
            if elix > 0:
                print("e - USE ELIXIR")
            if biom[map[y][x]]["t"] == "SHOP":
                print("b - BUY ITEMS")
            if biom[map[y][x]]["t"] == "MAYOR":
                print("m - TALK TO MAYOR")
            if biom[map[y][x]]["t"] == "CAVE" and key:
                print("c - ENTER CAVE")

            draw()

            dest = input("# ")

            if dest == "0":
                play = False
                menu = True
                save()

            if dest == "w":
                if y > 0:
                    y -= 1
                    standing = False
            elif dest == "s":
                if y < y_len:
                    y += 1
                    standing = False
            elif dest == "a":
                if x > 0:
                    x -= 1
                    standing = False
            elif dest == "d":
                if x < x_len:
                    x += 1
                    standing = False
            elif dest == "p":
                if pot > 0:
                    heal(20)
                    pot -= 1
                else:
                    print("You don't have any potions!")
                    input("> ")
                    standing = True
            elif dest == "e":
                if elix > 0:
                    heal(50)
                    elix -= 1
                else:
                    print("You don't have any elixirs!")
                    input("> ")
                    standing = True
            elif dest == "b":
                if biom[map[y][x]]["t"] == "SHOP":
                    buy = True
                else:
                    print("You can't buy items here!")
                    input("> ")
                    standing = True
            elif dest == "m":
                if biom[map[y][x]]["t"] == "MAYOR":
                    mayor()
                else:
                    print("You can't talk to the mayor here!")
                    input("> ")
                    standing = True
            elif dest == "c":
                if biom[map[y][x]]["t"] == "CAVE" and key:
                    print("You enter the cave to face the Dragon!")
                    input("> ")
                    fight = True
                    battle()
                elif biom[map[y][x]]["t"] == "CAVE" and not key:
                    print("You need a key to enter the cave!")
                    input("> ")
                    standing = True
                else:
                    print("There is no cave here!")
                    input("> ")
                    standing = True
            else:
                standing = True
        