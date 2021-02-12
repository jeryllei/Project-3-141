from collections import defaultdict
import json
from bs4 import BeautifulSoup
import pymongo
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
import math

def loadBookkeeping():
    with open('WEBPAGES_RAW/bookkeeping.json', 'r') as json_file:
        data = json.load(json_file)
    return data

def loadBookkeepingTest():
    with open('bookkeeperTEST.json', 'r') as json_file:
        data = json.load(json_file)
    return data

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

            # page_title = soup.head
            # if page_title != None and soup.head.title != None:
            #     page_title = str(soup.head.title.text).strip()
            # else:
            #     page_title = 'No title'
            # collection.insert_one({'docID': docID, 'url': url, 'page_title': page_title})
            
            page_text_tokenized = word_tokenize(page_text)
            lemmatizer = WordNetLemmatizer()
            page_text_lemmatized = [lemmatizer.lemmatize(word) for word in page_text_tokenized if word.isalnum()]

            token_dictionary = defaultdict(int)
            for word in page_text_lemmatized:
                token_dictionary[word.lower()] += 1
            
            for token, freq in token_dictionary.items():
                if collection.find_one({'_id': token}) == None:
                    collection.insert_one({'_id': token,
                                            'postings': [{'docID': docID, 'frequency': freq, 'tf_idf': 0, 'tags': []}]
                    })
                else:
                    new_post = {'docID': docID, 'frequency': freq, 'tf_idf': 0, 'tags': []}
                    collection.find_one_and_update({'_id': token}, {'$push': {'postings': new_post}})
            
            print(f'Page indexed (ID: {docID}): {url}')
    return

'''
{
    '_id': 'token',
    'postings': [{'docID': '0/11', 'frequency': 10, 'tf_idf': 2, 'tags':['h1', 'h2', 'title', 'strong']}, {'docID': '0/34', 'frequency': 10, 'tf_idf': 4, 'tags':[]}]
}
'''
def calculateTF_IDF(collection):
    # Visits every entry in the index and sets the PF-IDF for each one.
    # https://stackoverflow.com/a/51596944
    '''
    collection.update_many(
        {},
        {'$set': {'postings.$[].tf_idf': 1}}
    )
    '''

    n = float(collection.count_documents({}))
    cursors = collection.find()
    for document in cursors:
        entryID = document['_id']
        df = len(document['postings'])
        idf = math.log((n / df), 10)
        newPostings = []
        i = 0
        while i < len(document['postinigs']):
            tf_idf = (1 + math.log(float(document['postings'][i]['frequency']))) * idf
            temp_post = document['postings'][i]
            temp_post['tf_idf'] = tf_idf
            newPostings.append(temp_post)
            i += 1
        collection.find_one_and_replace({'_id': entryID}, {'postings': newPostings})
    return

if __name__ == "__main__":
    myClient = pymongo.MongoClient('mongodb://localhost:27017/')
    mydb = myClient['myDatabase']
    myCollection = mydb['testIndex']

    myData = loadBookkeeping()
    # constructIndex(myData, myCollection)
    calculateTF_IDF(myCollection)