from Setup import Document
from Setup import Indexer
from Setup import Loader
from Setup import Searcher

from hashlib import blake2s

import sys



pdf = './ALLGTMOOCR.pdf'
txt = './ALLGTMOOCR_TEXT.txt'
mapping = './ALLGTMOOCR_MAPPING.txt'

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
for line in sys.stdin:
  if 'quit()' == line.rstrip(): 
    break
  print('keyword: {}'.format(line.rstrip()))
  keyword = line.rstrip()
  searcher = Searcher(loader)
  results = searcher.find(keyword)

  print(results)