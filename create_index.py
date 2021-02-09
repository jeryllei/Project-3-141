from collections import defaultdict
import json
from bs4 import BeautifulSoup
import pymongo

def loadBookkeeping():
    with open('WEBPAGES_RAW/bookkeeping.json', 'r') as json_file:
        data = json.load(json_file)
    return data

def loadBookkeepingTest():
    with open('bookkeeperTEST.json', 'r') as json_file:
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


# Structure of DB:
'''
{
    '_id': 'token',
    'postings': [{'docID': '0/11', 'frequency': 10, 'tf_idf': 2, 'tags':['h1', 'h2', 'title', 'strong']}, {'docID': '0/34', 'frequency': 10, 'tf_idf': 4, 'tags':[]}]
}
'''
def constructIndex(data, collection):
    for docID, url in data.items():
        directory = 'WEBPAGES_RAW/' + docID
        with open(directory, 'r', encoding='utf-8') as html_page:
            soup = BeautifulSoup(html_page, 'html.parser')
            page_text = soup.getText()
            page_title = soup.head
            if page_title != None and soup.head.title != None:
                page_title = str(soup.head.title.text).strip()
            else:
                page_title = 'No title'
            collection.insert_one({'docID': docID, 'url': url, 'page_title': page_title})
            print('Page indexed (ID: %s): %s', (docID, url))
    return

if __name__ == "__main__":
    myClient = pymongo.MongoClient('mongodb://localhost:27017/')
    mydb = myClient['myDatabase']
    myCollection = mydb['testIndex']

    myData = loadBookkeeping()
    constructIndex(myData, myCollection)