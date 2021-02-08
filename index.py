from collections import defaultdict
import json

def loadBookkeeping():
    with open('WEBPAGES_RAW/bookkeeping.json', 'r') as json_file:
        data = json.load(json_file)
    return data

class Index:
    def __init__(self):
        # Structure: {token: [{docID: '0/100', tfidf: '1'}]}
        self.index = defaultdict(list)

    # Returns the index itself.
    def getIndex(self):
        return self.index

    # Returns a list of documents for a given token.
    def getIndexEntry(self, token):
        return self.index[token]

    # Adds an entry to the Index, creates a new entry automatically if the token didn't already exist.
    def addIndexEntry(self, token, docid, tf_idf):
        self.index[token].append(dict(docID=docid, tfidf=tf_idf))

if __name__ == "__main__":
    pass