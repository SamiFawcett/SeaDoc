from Setup import Document
from Setup import Indexer
from Setup import Loader
from Setup import Searcher

from hashlib import blake2s

import sys



pdf = './sample.pdf'
txt = './sample.txt'
mapping = './sample_mapping.txt'

#document setup
print('Converting document...')
doc = Document(pdf, True, txt)
print('Success...')
print('Indexing document...')
#indexer setup
ind = Indexer(doc, blake2s(), True, True, mapping)
#indexer setup
ind.assignDocument()
ind.generateMap()
ind.saveMap()
print('Success...')

print('Loading Document...')
loader = Loader(mapping)
print('Success...')
print("Document processed... Ready for search.")

keyword = ''
relation = ''
for line in sys.stdin:
  line = line.strip()
  if 'quit()' == line.rstrip(): 
    break
  print('keyword: {}'.format(line))
  tokens = line.split(' ')
  keyword = tokens[0]
  relation = ''
  if(len(tokens) > 1):
    relation = tokens[1]
  
  searcher = Searcher(loader)
  results = searcher.findAllWithRelationTo(keyword, relation)

  print(results)