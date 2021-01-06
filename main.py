from Setup import Document
from Setup import Indexer
from Setup import Loader
from Setup import Searcher


from hashlib import blake2s

import sys
import COMMANDS

direc = 'sample/'
filename = 'sample'
pdf = './' + direc + filename + '.pdf'
txt = './' + direc + filename + '_TEXT' + '.txt'
mapping = './' + direc + filename + '_MAPPING' + '.txt'
rdb = './' + direc + filename + '_RDB' + '.txt'

#document setup
print('Converting document...')
try: 
  doc = Document(pdf, txt)
  print('Converting document [SUCCESS]')
except:
  print('Converting document [FAILURE]')
  exit(0)


#indexer setup
print('Indexing ...')
try:
  ind = Indexer(doc, blake2s(), True, mapping)
  print('Indexing [SUCCESS]')
except:
  print('Indexing [FAILURE] {}'.format(sys.exc_info()))
  exit(0)
  
  

#loading setup
print('Loading Document...')
try:
  loader = Loader(ind, mapping, rdb)
  print('Loading Document...[SUCCESS]')
except:
  print('Loading Document...[FAILURE]')
  exit(0)

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
      return searcher.getRDB()
    elif(id == 4):
      return searcher.getRDB()[searcher.hasher(arguments[0], blake2s())]['proximity_text']
    elif(id == 5):
      return searcher.getRDB()[searcher.hasher(arguments[0], blake2s())]['doubles_text']
    elif(id == 6):
      return searcher.getRDB()[searcher.hasher(arguments[0], blake2s())]['triples_text']
    elif(id == 7):
      return searcher.getRDB()[searcher.hasher(arguments[0], blake2s())]['quadruples_text']
    elif(id == 8):
      return searcher.getRDB()[searcher.hasher(arguments[0], blake2s())]['quintuples_text']
    elif(id == 11):
      return searcher.reccurentPhrases(arguments[0], int(arguments[1]), searcher.getRDB())

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