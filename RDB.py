import json

class RDB:

    def __init__(self, _rdb):
        self.rdb = _rdb


    def save(self, text_file):
        with open(text_file, 'w', encoding='utf-8') as tf:
            json_object = json.dumps(self.rdb, indent=4)
            tf.write(json_object)
        tf.close()

    
    def getRDB(self):
        return self.rdb
        
    def setRDB(self, newRDB):
        self.rdb = newRDB
        return 1

    def load(self, text_file):
        json_string = open(text_file, 'r', encoding='utf-8').read()
        json_dict = json.loads(json_string)
        self.setRDB(json_dict)
        return json_dict

    


