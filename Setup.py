import os.path
from os import path

import json

from hashlib import blake2s
from PyPDF2 import PdfFileReader, PdfFileWriter
import fitz
import math



#settings setup
class SETTINGS():
  SEARCH_PROXIMITY = 10
  RELATIONAL_PROXIMITY = 20


class Document():
  def __init__(self, _pdf_filename, _save=False, _out_text_filename=''):
    self.title = _pdf_filename.split('.')[0]
    self.pdf_filename = _pdf_filename
    self.text_filename = _out_text_filename
    self.saved = _save
    #updated package used to retrieve pdf text
    self.pages, self.full_text = self.generatePagesMU()
    self.mu_doc = None


  def generatePagesMU(self):
    pdf = fitz.open(self.pdf_filename)
    self.mu_doc = pdf
    pdf_pages = pdf.pages()

    #check saving options for output
    if(self.saved):
      text_filename = self.text_filename
    else:
      text_filename = './temp.txt'

    page_list = []
    full_text = ''
    with open(text_filename, 'w', encoding='utf-8') as text_file:
      for page in pdf_pages:
        text = page.getTextPage().extractText()
        exp_page = Page(text, page.number, len(text))
        page_list.append(exp_page)
        full_text +=  text

        if(self.saved):
              #write text to text file
              text_file.write('Page {0}\n'.format(page.number))
              text_file.write(''.center(100, '-'))
              text_file.write('\n')
              text_file.write(text)
      text_file.close()
    
    return (page_list, full_text)


  def getInTextFormat(self):
    return self.full_text

  def getPages(self):
    return self.pages

  def getPage(self, page_num):
    return self.pages[page_num]
          


class Page():
  def __init__(self, _page_text, _page_num, _wc):
    self.index_mapping = []
    self.page_text = _page_text
    self.page_num = _page_num
    #raw text character count
    self.page_raw_cc = _wc
    #map text character count
    self.page_cc_map = 0
  
  def getWord(self, index):
    return self.index_mapping[index]

  def getPageText(self):
    return self.page_text
  
  def getPageNumber(self):
    return self.page_num

  def setCCM(self, ccm):
    self.page_cc_map = ccm

  def getCCM(self):
    return self.page_cc_map

  def indexMapSize(self):
    return len(self.index_mapping)

  def getSubText(self, begin_idx, end_idx):
    sub_text = ''
    for i in range(begin_idx, end_idx):
      sub_text += self.index_mapping[i] + ' '
    return sub_text.rstrip()




class Indexer():
  
  def __init__(self, _doc, _hashObj, _lower, _save, _savefile):
    self.mapping = {}
    self.isSaved = _save
    if(_save):
      self.save_file = _savefile
    else:
      self.save_file = './temp_save.txt'
    if(_lower):
      self.text = _doc.getInTextFormat().lower()
    else:
      self.text = _doc.getInTextFormat()

    self.hash_object = _hashObj
    self.document = _doc

  def hasher(self, word, hash_obj):
    hash_obj.update(bytes(word, encoding='utf-8'))
    hash = hash_obj.hexdigest()
    return hash

  def getDocument(self):
    return self.document

  def isSave(self):
    return self.isSaved

  def getSaveFile(self):
    return self.save_file

    
  def generateMap(self):
    for page in self.document.getPages():
      index = 0
      words = page.getPageText().replace('\n', '').replace('.', ' ').replace(',', ' ').replace(';', ' ').replace('  ', ' ').replace('   ', ' ').strip().split(' ')
      ccm = 0
      for word in words:
        #reset hash object to store multiple copies of the same word in the same bucket
        self.hash_object = blake2s()
        hash = self.hasher(word.lower(), self.hash_object)
      

        if(hash in self.mapping):
          self.mapping[hash]['page_numbers'].append(page.getPageNumber())
          self.mapping[hash]['occurences'] += 1
          self.mapping[hash]['indicies'].append(index)
        else:
          self.mapping[hash] = {
            'word': word,
            'indicies': [index],
            'page_numbers': [page.getPageNumber()],
            'occurences': 1
          }

        index+=1
        page.index_mapping.append(word)
        ccm += len(word)
      
      page.setCCM(ccm)
      ccm = 0

    return 1

  def saveMap(self):
    with open(self.save_file, 'w', encoding="utf-8") as text_file:
      #TODO: CREATE DOCUMENT FILE SAVE,
      
      #word map data
      text_file.write(json.dumps(self.mapping, indent=4))
    text_file.close()


  def getMap(self):
    return self.mapping

  def getHashObject(self):
    return self.hash_object



class Loader():
  def __init__(self, _indexer, _mapping_file):
    self.indexer = _indexer
    self.mapping = _indexer.getMap()
    self.loaded = False
    self.document = _indexer.getDocument() 

    #checks to see if we have created a map for the document
    if(os.path.exists(_mapping_file)):
      self.mapping = json.loads(open(_mapping_file, 'r', encoding='utf-8').read())
      self.loaded = True
  
  def getMap(self):
    return self.mapping
  
  def getDocument(self):
      return self.document

  


class Searcher():
  def __init__(self, _loader):
    self.loader = _loader
    self.mapping = _loader.getMap()
    self.relational_database = self.generateRelationalDatabase()
    
  
  def hasher(self, word, hash_obj=blake2s()):
    hash_obj.update(bytes(word, encoding='utf-8'))
    hash = hash_obj.hexdigest()
    return hash

  def printMap(self):
    print(self.mapping)

  def getRDB(self):
    return self.relational_database

  def generateRelationalDatabase(self):
    r_db = {}
    for page in self.loader.document.getPages():
      words = page.index_mapping
      for word in words:
        #reset hash object to store multiple copies of the same word in the same bucket
        hash_object = blake2s()
        hash = self.loader.indexer.hasher(word.lower(), hash_object)

        if(hash in r_db):
          continue
        else:
          r_db[hash] = {
            'word': word,
            'proximity_text': self.findAllWithWordProximity(word),
            'doubles_text': self.getCombination(2, word),
            'triples_text': self.getCombination(3, word),
            'quadruples_text':self.getCombination(4, word),
            'quintuples_text':self.getCombination(5, word)
            #'filtered_text_relations':self.filterTextRelations(word)
          }

    return r_db

  def filterTextRelations(self, word):
    search_objects = self.find(word)
    pages_found = search_objects['page_numbers']
    surroundingWords = []

    for page in pages_found:
      surroundingWords.append(self.findAllWithWordProximityInPage(page, word))

    return surroundingWords

  
  def reccurentPhrases(self, word, occurence_amt, rdb):
    occurences = {}
    results = []
    rdb = rdb[self.hasher(word, blake2s())]
    for double_amt in range(len(rdb['doubles_text'])):
      if(rdb['doubles_text'][double_amt] in occurences):
        occurences[rdb['doubles_text'][double_amt]]['counter'] += 1
      else:
        occurences[rdb['doubles_text'][double_amt]] = {'counter': 0}

      if(occurences[rdb['doubles_text'][double_amt]]['counter'] >= occurence_amt):
          results.append(rdb['doubles_text'][double_amt])

    for triple_amt in range(len(rdb['triples_text'])):
      if(rdb['triples_text'][triple_amt] in occurences):
        occurences[rdb['triples_text'][triple_amt]]['counter'] += 1
      else:
        occurences[rdb['triples_text'][triple_amt]] = {'counter': 0}

      if(occurences[rdb['triples_text'][triple_amt]]['counter'] >= occurence_amt):
          results.append(rdb['triples_text'][triple_amt])

    for quad_amt in range(len(rdb['quadruples_text'])):
      if(rdb['quadruples_text'][quad_amt] in occurences):
        occurences[rdb['quadruples_text'][quad_amt]]['counter'] += 1
      else:
        occurences[rdb['quadruples_text'][quad_amt]] = {'counter': 0}

      if(occurences[rdb['quadruples_text'][quad_amt]]['counter'] >= occurence_amt):
          results.append(rdb['quadruples_text'][quad_amt])


    for quin_amt in range(len(rdb['quintuples_text'])):
      if(rdb['quintuples_text'][quin_amt] in occurences):
        occurences[rdb['quintuples_text'][quin_amt]]['counter'] += 1
      else:
        occurences[rdb['quintuples_text'][quin_amt]] = {'counter': 0}

      if(occurences[rdb['quintuples_text'][quin_amt]]['counter'] >= occurence_amt):
          results.append(rdb['quintuples_text'][quin_amt])

    return results

  def getCombination(self, amt, keyword):
    #need to reset hasher
    find_hasher = blake2s()
    results = []
    try:
      search_object = self.mapping[self.hasher(keyword.lower(), find_hasher)]

      for idx in range(len(search_object['indicies'])):
        #grab word details and setting preferences
        associated_page_num = search_object['page_numbers'][idx]
        associated_index = search_object['indicies'][idx]
        padding = 0
        if(associated_index == 0):
          padding = amt // 2

        if(amt % 2 == 0):
          text_begin = associated_index - int(math.ceil(amt / 2)) - padding
          text_end = associated_index + int(math.ceil(amt / 2)) + padding
        else:
          text_begin = associated_index + 1 - int(math.ceil(amt / 2)) - padding
          text_end = associated_index + int(math.ceil(amt / 2)) + padding

        #index_map
        page_wcm = self.loader.getDocument().getPage(associated_page_num).indexMapSize()
        
        if(text_end > page_wcm):
          text_end = associated_index + len(keyword)
        
        if(text_begin < 0):
          text_begin = associated_index
        

        #create subtext
        sub_text = self.loader.getDocument().getPage(associated_page_num).getSubText(text_begin, text_end)
        results.append(sub_text)
        
       

    except IndexError:
      #print('Page num: ', associated_page_num, 'keyword: ', keyword, 'index: ', associated_index, 'text_begin: ', text_begin, 'text_end: ', text_end, 'Out of index')
      pass
    except KeyError:
      print('{} wasn\'t found.'.format(keyword))
      pass


    return results


  def find(self, keyword):
    #need to reset hasher
    find_hasher = blake2s()
    hash = self.hasher(keyword.lower(), find_hasher)
    try:
      #get word details
      search_object = self.mapping[hash]
      
      return search_object
    except KeyError:
      print('{} wasn\'t found.'.format(keyword))
      return ''

  
  def findAllWithWordProximity(self, keyword):
    return self.getCombination(SETTINGS.SEARCH_PROXIMITY, keyword)

  def findAllWithWordProximityInPage(self, page_num, keyword):
    #need to reset hasher
    find_hasher = blake2s()
    results = []
    try:
      search_object = self.mapping[self.hasher(keyword.lower(), find_hasher)]

      for idx in range(len(search_object['indicies'])):
        #grab word details and setting preferences
        associated_page_num = search_object['page_numbers'][idx]
        if(associated_page_num == page_num):
          associated_index = search_object['indicies'][idx]
          text_begin = associated_index - SETTINGS.SEARCH_PROXIMITY
          text_end = associated_index + 1 + SETTINGS.SEARCH_PROXIMITY

          #index_map
          page_wcm = self.loader.getDocument().getPage(associated_page_num).indexMapSize()
          
          if(text_end > page_wcm):
            text_end = associated_index + len(keyword)
          
          if(text_begin < 0):
            text_begin = associated_index
          

          #create subtext
          sub_text = self.loader.getDocument().getPage(associated_page_num).getSubText(text_begin, text_end)
          results.append(sub_text)
        else:
          continue
        
       

    except IndexError:
      #print('Page num: ', associated_page_num, 'keyword: ', keyword, 'index: ', associated_index, 'text_begin: ', text_begin, 'text_end: ', text_end, 'Out of index')
      pass
    except KeyError:
      print('{} wasn\'t found.'.format(keyword))
      pass


    return results

  def findAllWithRelationTo(self, keyword, relation):
    #reset hasher
    find_hasher = blake2s()
    #contain search results in results array
    results = []

    try:
      #results given keyword
      keyword_search = self.mapping[self.hasher(keyword.lower(), find_hasher)]
      
      #reset hasher!
      find_hasher = blake2s()
      
      #results given relation
      relational_search = self.mapping[self.hasher(relation.lower(), find_hasher)]

      page_numbers = keyword_search['page_numbers']
      for page_num in page_numbers:
        #get word indicies
        keyword_index = keyword_search['indicies'][page_num]
        relation_index = relational_search['indicies'][page_num]

        #create sub text bounds
        text_begin = keyword_index - SETTINGS.RELATIONAL_PROXIMITY
        text_end = relation_index + SETTINGS.RELATIONAL_PROXIMITY

        #check page bounds
        page_wcm = self.loader.getDocument().getPage(page_num).indexMapSize()
        if(text_end > page_wcm):
          text_end = relation_index + len(relation)
        if(text_begin < 0):
          text_begin = keyword_index

        #retrieve sub text
        if(int(math.fabs(keyword_index - relation_index)) <= SETTINGS.RELATIONAL_PROXIMITY):
          sub_text = self.loader.getDocument().getPage(page_num).getSubText(text_begin, text_end)
          results.append(sub_text)

    except:
      pass

    return results





''''
@implementation details:

  maps are currently only used to index documents for faster and better searching, 
  they aren't a file format to read and load documents (maybe in the future), that is why the Searcher
  generates the map and not the Indexer

'''



