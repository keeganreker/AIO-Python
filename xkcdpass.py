#!/usr/bin/env python3
import random
import os
import argparse
import math
import sys

DEBUG = False
VERBOSE = False
SHOW_STRENGTH = False
ENTROPY = []

def set_template_vals(template):
  global num_words, word_len_min, word_len_max, case_trans
  global separators, pad_digits_pre, pad_digits_post
  global padding_type, pad_to_length, padding_chars
  global padding_chars_pre, padding_chars_post
  match template:
    case 'STD':
      num_words          = 3
      word_len_min       = 4
      word_len_max       = 6
      case_trans         = "capitalize"
      separators         = "@%^&*_+~?'/"
      pad_digits_pre     = 0
      pad_digits_post    = 2
      padding_type       = "fixed"
      pad_to_length      = 0
      padding_chars      = "!@$%^&=~?"
      padding_chars_pre  = 1
      padding_chars_post = 1
    case 'WSE':
      num_words          = 2
      word_len_min       = 5
      word_len_max       = 6
      case_trans         = "capitalize"
      separators         = "!#$^*-_=+"
      pad_digits_pre     = 0
      pad_digits_post    = 2
      padding_type       = "adapt"
      pad_to_length      = 16
      padding_chars      = "!#$^*=+"
      padding_chars_pre  = 0
      padding_chars_post = 0
    case 'ALT':
      num_words          = 3
      word_len_min       = 4
      word_len_max       = 6
      case_trans         = "capitalize"
      separators         = ""
      pad_digits_pre     = 2
      pad_digits_post    = 0
      padding_type       = "fixed"
      pad_to_length      = 0
      padding_chars      = "!@$%^&*+=~?"
      padding_chars_pre  = 0
      padding_chars_post = 2
    case 'STR':
      num_words          = 3
      word_len_min       = 5
      word_len_max       = 9
      case_trans         = "capitalize"
      separators         = "!@$%^&*-_+=|~?"
      pad_digits_pre     = 3
      pad_digits_post    = 3
      padding_type       = "fixed"
      pad_to_length      = 0
      padding_chars      = "!@$%^&*_+=~?"
      padding_chars_pre  = 2
      padding_chars_post = 2
    case _:
      print("The preset '" + preset + "' is not valid. Proceeding with the 'STD' preset...")
      set_params(STD)

def set_case_trans(case_trans, wordlist):
  new_wordlist = []
  match case_trans:
    case 'alternating':
      t = 0
      for word in wordlist:
        if t == 1:
          new_word = word.upper()
          t = 0
        else:
          new_word = word.lower()
          t = 1
        new_wordlist.append(new_word)
    case 'upper':
      for word in wordlist:
        new_word = word.upper()
        new_wordlist.append(new_word)
    case 'lower':
      for word in wordlist:
        new_word = word.lower()
        new_wordlist.append(new_word)
    case 'random':
      for word in wordlist:
        new_word = ""
        for letter in word:
          docap = random.choice('01')
          if docap == '0':
            new_word = new_word + letter.lower()
          else:
            new_word = new_word + letter.upper()
        new_wordlist.append(new_word)
    case 'capitalize':
      for word in wordlist:
        new_word = word.capitalize()
        new_wordlist.append(new_word)
    case 'as-is':
      new_wordlist = wordlist
  return new_wordlist

def get_separator(separators):
  separator = random.choice(separators)
  return separator

def get_pad_char(padding_chars):
  padding_char = random.choice(padding_chars)
  return padding_char

def get_pad_digits(num):
  count = 1
  new_string = ""
  while count <= num:
    new_num = random.choice('0123456789')
    new_string = new_string + new_num
    count += 1
  return new_string

def find_dict():
  common_word_files = ["/usr/share/dict/xkcdpass.txt",
                       "/usr/share/cracklib/cracklib-dict",
                       "/usr/share/dict/words"]
  for file in common_word_files:
    if os.path.isfile(file):
      return file

def get_wordlist(dictionary, word_len_min, word_len_max, num_words):
  if word_len_min < 1:
    sys.stderr.write("ERROR:The minimum length cannot be 0\n")
    sys.exit(1)
  words = []
  with open(dictionary) as wordlist:
    for line in wordlist:
      new_word = line.strip()
      if not "'" in new_word:
        if len(new_word) <= word_len_max:
          if len(new_word) >= word_len_min:
            words.append(new_word)
  wordlist = random.choices(words, k = num_words)
  return wordlist

def get_cryto_vlaue(passwd):
  possible_symbols = 26
  if case_trans != 'upper' or case_trans != 'lower':
    possible_symbols = int(possible_symbols) + 26
  if pad_digits_pre != 0 or pad_digits_post != 0:
    possible_symbols = int(possible_symbols) + 10
  if padding_chars != "" or separators != "":
    comblist = padding_chars + separators
    uniq = []
    for symbol in comblist:
      if not symbol in uniq:
        uniq.append(symbol)
    possible_symbols = int(possible_symbols) + int(len(uniq))
  length = len(passwd)
  strength = round(math.log2( possible_symbols ** length ))
  return strength

def get_min_crypto_values():
  if case_trans == 'upper' or case_trans == 'lower':
    letter_syms = 26 ** ( num_words * word_len_min )
  if case_trans == 'capitalize':
    lower_syms = 26 ** (( num_words * word_len_min ) - num_words )
    upper_syms = 26 ** num_words
    letter_syms = lower_syms + upper_syms
  if case_trans == 'alternating':
    num_words_upper = int( num_words / 2 )
    if ( num_words % 2 ) == 0:
      num_words_lower = num_words_upper
    else:
      num_words_lower = num_words_upper + 1
    lower_syms = 26 ** ( num_words_lower * word_len_min )
    upper_syms = 26 ** ( num_words_upper * word_len_min )
    letter_syms = lower_syms + upper_syms
  # We don't know what's in the dictionary, lump as-is with random
  if case_trans == 'random' or case_trans == 'as-is':
    letter_syms = 52 ** ( num_words * word_len_min )
  if pad_digits_pre != 0 or pad_digits_post != 0:
    digit_syms = 10 ** ( pad_digits_pre + pad_digits_post )
  num_syms = len(separators)
  if num_syms == 1:
    sepr_syms = 1
  else:
    count_syms = num_words
    if pad_digits_pre != 0:
      count_syms = count_syms + 1
    if pad_digits_post != 0:
      count_syms = count_syms + 1
    sepr_syms = num_syms ** count_syms
  num_pads = len(padding_chars)
  if padding_type == 'fixed':
    if padding_chars_pre != 0 or padding_chars_post != 0:
      pad_syms = num_pads ** ( padding_chars_pre + padding_chars_post )
    else:
      pad_syms = 0
  else:
    # fixed
    min_pw_len = ( num_words * word_len_min ) + pad_digits_pre + pad_digits_post
    pad_syms = num_pads ** ( pad_to_length - min_pw_len )
  total_syms = letter_syms + digit_syms + sepr_syms + pad_syms
  strength = round(math.log2( total_syms ))
  return strength

parser = argparse.ArgumentParser( prog = 'xkcdpass.py',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description = '''xkcdpass.py uses a dictionary to generate stong but memorable passwords.''',
        epilog = '''Examples:
          xkcdpass.py --passcount 3 --numwords 3  \\
                      --minlength 4 --maxlength 6 \\
                      --casetransform capitalize  \\
                      --separators '@%^&*_+~?'    \\
                      --paddigitspre 0            \\
                      --paddigitspost 0           \\
                      --paddingtype fixed         \\
                      --paddingchars '!@$%^&=~?'  \\
                      --padtolength 0             \\
                      --padcharspre 1             \\
                      --padcharspost 1

          xkcdpass.py -t STD

          xkcdpass.py

The above three commands all produce identicaly formatted output. The defualt
template is the 'STD' template, which the first example provides in detail.
If using a template, the template parameters are loaded fist, and any
additional commandline arguments will override those in the template.''')
parser.add_argument("-d", "--dictionary",
                    type=str,
                    help="optional wordlist (one word per line)",
                    metavar="PATH")
parser.add_argument("-t", "--template",
                    type=str,
                    choices=['STD', 'WSE', 'ALT', 'STR'],
                    help="Use a predefined template [STD|WSE|ALT|STR]",
                    metavar="VAL")
parser.add_argument("-N", "--passcount",
                    default = 3,
                    type=int,
                    help="Number of password options to return",
                    metavar="NUM")
parser.add_argument("-n", "--numwords",
                    type=int,
                    help="Number of words in password",
                    metavar="NUM")
parser.add_argument("-m", "--minlength",
                    type=int,
                    help="Minumum length of words",
                    metavar="NUM")
parser.add_argument("-M", "--maxlength",
                    type=int,
                    help="Maximum length of words",
                    metavar="NUM")
parser.add_argument("-c", "--casetransform",
                    type=str,
                    choices=['alternating', 'upper', 'lower', 'random', 'capitalize', 'as-is'],
                    help="Method: [upper|lower|random|capitalize|as-is]",
                    metavar="VAL")
parser.add_argument("-s", "--separators",
                    type=str,
                    help="One or more characters used as a separator",
                    metavar="STRING")
parser.add_argument("-p", "--paddigitspre",
                    type=int,
                    help="Number of padding digits at the start of the password",
                    metavar="NUM")
parser.add_argument("-P", "--paddigitspost", 
                    type=int,
                    help="Number of padding digits at the end of the password",
                    metavar="NUM")
parser.add_argument("-T", "--paddingtype",
                    type=str,
                    choices=['adapt', 'fixed'],
                    help="Select the padding characters type: [adapt|fixed]",
                    metavar="VAL")
parser.add_argument("-C", "--paddingchars", 
                    type=str,
                    help="One or more characters used for pre or post padding",
                    metavar="STRING")
parser.add_argument("-l", "--padtolength",
                    type=int,
                    help="Length of final password if using adapt pad type",
                    metavar="NUM")
parser.add_argument("-x", "--padcharspre",
                    type=int,
                    help="Number of padding chars at the start of the password",
                    metavar="NUM")
parser.add_argument("-X", "--padcharspost",
                    type=int,
                    help="Number of padding chars at the end of the password",
                    metavar="NUM")
parser.add_argument("-v", "--verbose",
                    help="Print computed min/max/avg entropy to stdout",
                    action="store_true")
parser.add_argument("-D", "--debug",
                    help="Print debug messages to stderr.",
                    action="store_true")
parser.add_argument("-S", "--strength",
                    help="Show minimum entropy if attacker knows scheme.",
                    action="store_true")
args = parser.parse_args()

if args.dictionary:
  dictionary = args.dictionary
else:
  dictionary = find_dict()

# Arguments should override templates, so just
# get set the template values right off the bat
if args.template:
  template = args.template
else:
  template = 'STD'
set_template_vals(template)

if args.passcount:
  passcount = args.passcount

if args.numwords:
  num_words = args.numwords

if args.minlength:
  word_len_min = args.minlength

if args.maxlength:
  word_lin_max = args.maxlength

if args.casetransform:
  case_trans = args.casetransform

if args.separators:
  separators = args.separators

if args.paddigitspre:
  pad_digits_pre = args.paddigtspre

if args.paddigitspost:
  pad_digits_post = args.paddigitspost

if args.paddingtype:
  padding_type = args.paddingtype

if args.padtolength:
  pad_to_length = args.padtolength

if args.paddingchars:
  padding_chars = args.paddingchars

if args.padcharspre:
  padding_chars_pre = args.padcharspre

if args.padcharspost:
  padding_chars_post = args.padcharspost

if args.verbose:
  VERBOSE = True

if args.debug:
  DEBUG = True

if args.strength:
  SHOW_STRENGTH = True

if DEBUG == 1:
  sys.stderr.write("Selected dictionary is: " + dictionary + ".\n")
  sys.stderr.write("Selected template is: " + template + ".\n")
  sys.stderr.write("passcount is: " + str(passcount) + "\n")
  sys.stderr.write("num_words is: " + str(num_words) + ".\n")
  sys.stderr.write("word_len_min is: " + str(word_len_min) + ".\n")
  sys.stderr.write("word_len_max is: " + str(word_len_max) + ".\n")
  sys.stderr.write("case_trans is: " + case_trans  + ".\n")
  sys.stderr.write("separators is: " + separators + ".\n")
  sys.stderr.write("pad_digits_pre is: " + str(pad_digits_pre) + ".\n")
  sys.stderr.write("pad_digits_post is: " + str(pad_digits_post) + ".\n")
  sys.stderr.write("padding_type is: " + padding_type + ".\n")
  sys.stderr.write("pad_to_length is: " + str(pad_to_length) + ".\n")
  sys.stderr.write("padding_chars is: " + padding_chars + ".\n")
  sys.stderr.write("padding_chars_pre is: " + str(padding_chars_pre) + ".\n")
  sys.stderr.write("padding_chars_post is: " + str(padding_chars_post) + ".\n\n")

pcount = 1
while pcount <= passcount:

  # Wordlist
  wordlist = get_wordlist(dictionary, word_len_min, word_len_max, num_words)
  pcount += 1
  transwordlist = set_case_trans(case_trans, wordlist)

  # Separators
  if len(separators) > 1:
    separator = get_separator(separators)
  elif len(separators) == 1:
    separator = separators
  else:
    separator = ""

  # Padding Digits
  padnumpre = ""
  padnumpost = ""
  if pad_digits_pre > 0:
    padnumpre = get_pad_digits(pad_digits_pre) + separator
  if pad_digits_post > 0:
    padnumpost = get_pad_digits(pad_digits_post)

  # Padding Characters
  if len(padding_chars) > 1:
    padchar = get_pad_char(padding_chars)
  elif len(padding_chars) == 1:
    padchar = padding_chars
  else:
    padchar = ""

  # Padding Type
  padpre = ""
  padpost = ""
  if padding_type == 'fixed':
    if padding_chars_pre != 0:
      count = 0
      while count < padding_chars_pre:
        padpre = padpre + padchar
        count += 1
    if padding_chars_post != 0:
      count = 0
      while count < padding_chars_post:
        padpost = padpost + padchar
        count += 1

  # Genrate the outword now before adapt padding
  tempout = ""
  rounds = len(transwordlist)
  count = 0
  while count < rounds:
    tempout = tempout + transwordlist[count] + separator
    count += 1
  tempout = padpre + padnumpre + tempout + padnumpost + padpost

  # padding_type == 'adapt'
  if padding_type == 'adapt':
    padpost=""
    curlength = len(tempout)
    if curlength < pad_to_length:
      rounds = (pad_to_length - curlength)
      count = 0
      while count < rounds:
        padpost = padpost + padchar
        count += 1
    tempout = tempout + padpost
  print(tempout)
  if VERBOSE == True or SHOW_STRENGTH == True:
    entropy = get_cryto_vlaue(tempout)
    if DEBUG == True:
      sys.stderr.write("Entropy: " + str(entropy) + " bits\n\n")
    ENTROPY.append(entropy)

if VERBOSE == True or SHOW_STRENGTH == True:
  top = int(len(ENTROPY)) - 1
  ENTROPY.sort()
  mine = ENTROPY[0]
  maxe = ENTROPY[top]
  avge = sum(ENTROPY) / len(ENTROPY)
  print("\nEntropy: min " + str(mine) + " bits, max " + str(maxe) + " bits, avg " + str(round(avge)) + " bits.")

if SHOW_STRENGTH == True:
  strength = get_min_crypto_values()
  print("Minimum " + str(strength) + " bits of entropy (if attacker knows the scheme).")

# End
