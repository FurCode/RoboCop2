# RoboCop 2's derpify.py - I don't even know why this exists, but it's entertaining in a way.
from cloudbot import hook

import random

def translate(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text

@hook.command
def derpify(text):
    """derpify <text> - returns some amusing 12-yearoldish reponses from your input."""
    string = text.upper()
    pick_the = random.choice(["TEH", "DA"])
    pick_e = random.choice(["E", "3", "A"])
    pick_qt = random.choice(["?!?!??", "???!!!!??", "?!??!?", "?!?!?!???"])
    pick_ex = random.choice(["1111!11", "1!11", "!!1!", "1!!!!111", "!1!111!1", "!11!111"])
    pick_end = random.choice(["", "OMG", "LOL", "WTF", "WTF LOL", "OMG LOL"])
    rules = {"YOU'RE":"UR", "YOUR":"UR", "YOU":"U", "WHAT THE HECK":"WTH", "WHAT THE HELL":"WTH", "WHAT THE FUCK":"WTF",
             "WHAT THE":"WT", "WHAT":"WUT", "ARE":"R", "WHY":"Y", "BE RIGHT BACK":"BRB", "BECAUSE":"B/C",
             "OH MY GOD":"OMG", "O":"OH", "THE":pick_the, "TOO":"2", "TO":"2", "BE":"B", "CK":"K", "ING":"NG",
             "PLEASE":"PLS", "SEE YOU":"CYA", "SEE YA":"CYA", "SCHOOL":"SKOOL", "AM":"M", "AM GOING TO":"IAM GOING TO",
             "LIKE":"LIEK", "HELP":"HALP", "KE":"EK","E": pick_e, "!": pick_ex, "?": pick_qt}
    output = translate(string, rules) + " " + pick_end

    return output;