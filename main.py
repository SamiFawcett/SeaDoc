from Setup import Document
from Setup import Indexer
from Setup import Loader
from Setup import Searcher


from hashlib import blake2s

import sys
import COMMANDS


pdf = './ALLGTMOOCR.pdf'
txt = './ALLGTMOOCR_TEXT.txt'
mapping = './ALLGTMOOCR_MAPPING.txt'

#document setup
print('Converting document...')
doc = Document(pdf, True, txt)
print('Success...')

#indexer setup
print('Indexing document...')
ind = Indexer(doc, blake2s(), True, True, mapping)
ind.generateMap()
ind.saveMap()
print('Success...')

#loading setup
print('Loading Document...')
loader = Loader(ind, mapping)
print('Success...')

searcher = Searcher(loader)

def commands(id, arguments):
  try:
    if(id == 0):
      return searcher.find(arguments[0])
    elif(id == 1):
      return searcher.findAllWithWordProximity(arguments[0])
    elif(id == 2):
      return searcher.findAllWithRelationTo(arguments[0], arguments[1])
    elif(id == 3):
      return searcher.relational_database
    elif(id == 4):
      return searcher.relational_database[searcher.hasher(arguments[0], blake2s())]['proximity_text']
    elif(id == 5):
      return searcher.relational_database[searcher.hasher(arguments[0], blake2s())]['doubles_text']
    elif(id == 6):
      return searcher.relational_database[searcher.hasher(arguments[0], blake2s())]['triples_text']
    elif(id == 7):
      return searcher.relational_database[searcher.hasher(arguments[0], blake2s())]['quadruples_text']
    elif(id == 8):
      return searcher.relational_database[searcher.hasher(arguments[0], blake2s())]['quintuples_text']
    elif(id == 11):
      return searcher.reccurentPhrases(arguments[0], int(arguments[1]), searcher.relational_database)

  except KeyError:
    print('{} doesn\'t exist'.format(arguments[0]))
    return

  return None

#search begin
print("{} loaded and indexed. Ready for search!".format(pdf))
for line in sys.stdin:
  line = line.strip()
  if(line == 'quit()'):
    break

  try:
    tokens = line.split(' ')
    #clean up token spacing
    for tok_idx in range(len(tokens)):
      tokens[tok_idx] = tokens[tok_idx].strip()
    
    #get command
    command_details = COMMANDS.COMMANDS[tokens[0]]

    if(len(tokens) > 1):
      #get version
      try:
        command_version = command_details['versions'][tokens[1]]

        total_args = command_version['argument_num'] + 2
        arguments = []

        for arg_num in range(total_args - 2):
          arguments.append(tokens[arg_num + 2])

        #results
        print(commands(int(command_version['id']), arguments))
        
      except KeyError:
        print("{} is not recognized as a version. -v for list of versions".format(tokens[1]))
      except IndexError:
        print("You are missing function paramaters to command: {}".format(tokens[0]))

  except KeyError:
    print('{} is not a command. -l for list of commands'.format(tokens[0]))

print('Exiting...')