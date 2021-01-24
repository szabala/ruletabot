import random
import os

f = open('assets/quotes.txt.txt', 'r')
txt = f.read()
lines = txt.split('\n.\n')
random.choice(lines)
