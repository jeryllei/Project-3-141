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

# Structure of DB:
'''
{
    '_id': 'token',
    'postings': [{'docID': '0/11', 'frequency': 10, 'tf_idf': 2, 'tags':['h1', 'h2', 'title', 'strong']}, {'docID': '0/34', 'frequency': 10, 'tf_idf': 4, 'tags':[]}]
}
'''
def constructIndex(data, collection):
    currentProgress = 1.0
    for docID, url in data.items():
        directory = 'WEBPAGES_RAW/' + docID
        with open(directory, 'r', encoding='utf-8') as html_page:
            soup = BeautifulSoup(html_page, 'html.parser')
            page_text = soup.getText()
            
            page_text_tokenized = word_tokenize(page_text)
            lemmatizer = WordNetLemmatizer()
            page_text_lemmatized = [lemmatizer.lemmatize(word) for word in page_text_tokenized if word.isalnum()]
            # token dictionary is a dictionary of each token inside a document with a count of how many appeared
            token_dictionary = defaultdict(int)
            for word in page_text_lemmatized:
                token_dictionary[word.lower()] += 1
            
            for token, freq in token_dictionary.items():
                # Goes through the entire token dictionary and adds it to the index if it doesn't exist, otherwise update the postings list for that token.
                if collection.find_one({'_id': token}) == None:
                    collection.insert_one({'_id': token,
                                            'postings': [{'docID': docID, 'frequency': freq, 'tf_idf': 0, 'tags': []}]
                    })
                else:
                    new_post = {'docID': docID, 'frequency': freq, 'tf_idf': 0, 'tags': []}
                    collection.find_one_and_update({'_id': token}, {'$push': {'postings': new_post}})
            
            print(f'Page indexed (ID: {docID}) {(currentProgress / 37497) * 100}%: {url}')
            currentProgress += 1
    return

'''
{
    '_id': 'token',
    'postings': [{'docID': '0/11', 'frequency': 10, 'tf_idf': 2, 'tags':['h1', 'h2', 'title', 'strong']}, {'docID': '0/34', 'frequency': 10, 'tf_idf': 4, 'tags':[]}]
}
'''
def addHTMLTags(data, collection):
    for docID, url in data.items():
        directory = 'WEBPAGES_RAW/' + docID
        with open(directory, 'r', encoding='utf-8') as html_page:
            soup = BeautifulSoup(html_page, 'html.parser')
            lemmatizer = WordNetLemmatizer()
            # Getting text inside an HTML tag: https://www.w3resource.com/python-exercises/BeautifulSoup/python-beautifulsoup-exercise-11.php
            h1 = [lemmatizer.lemmatize(word).lower() for word in word_tokenize(' '.join([x.text.strip() for x in soup.find_all('h1')])) if word.isalnum()]
            h2 = [lemmatizer.lemmatize(word).lower() for word in word_tokenize(' '.join([x.text.strip() for x in soup.find_all('h2')])) if word.isalnum()]
            title = [lemmatizer.lemmatize(word).lower() for word in word_tokenize(' '.join([x.text.strip() for x in soup.find_all('title')])) if word.isalnum()]
            strong = [lemmatizer.lemmatize(word).lower() for word in word_tokenize(' '.join([x.text.strip() for x in soup.find_all('strong')])) if word.isalnum()]
            # Could be done in a single function with HTML tags as an argument passed in as well.
            # Adds HTML tags to postings inside the postings list.
            for word in h1:
                entryPostings = collection.find_one({'_id': word})
                if entryPostings != None:
                    entryPostings = entryPostings['postings']
                    for posting in entryPostings:
                        if posting['docID'] == docID:
                            posting['tags'].append('h1')
                            break
                    collection.find_one_and_replace({'_id': word}, {'postings': entryPostings})
            for word in h2:
                entryPostings = collection.find_one({'_id': word})
                if entryPostings != None:
                    entryPostings = entryPostings['postings']
                    for posting in entryPostings:
                        if posting['docID'] == docID:
                            posting['tags'].append('h2')
                            break
                    collection.find_one_and_replace({'_id': word}, {'postings': entryPostings})
            for word in title:
                entryPostings = collection.find_one({'_id': word})
                if entryPostings != None:
                    entryPostings = entryPostings['postings']
                    for posting in entryPostings:
                        if posting['docID'] == docID:
                            posting['tags'].append('title')
                            break
                    collection.find_one_and_replace({'_id': word}, {'postings': entryPostings})
            for word in strong:
                entryPostings = collection.find_one({'_id': word})
                if entryPostings != None:
                    entryPostings = entryPostings['postings']
                    for posting in entryPostings:
                        if posting['docID'] == docID:
                            posting['tags'].append('strong')
                            break
                    collection.find_one_and_replace({'_id': word}, {'postings': entryPostings})
            print(f'Tagged {docID}.')
    return

def calculateTF_IDF(collection):
    # n is total number of documents inside the index collection
    n = float(collection.count_documents({}))
    # cursors is an iterable of every single document in the index collection
    cursors = collection.find()
    for document in cursors:
        # entry id is a single word
        entryID = document['_id']
        df = len(document['postings'])
        idf = math.log((n / df), 10)
        # constructs a new postings list to be inserted back in the database
        newPostings = []
        i = 0
        while i < len(document['postings']):
            # calculates the tf-idf by going through each posting in the postings list for a word
            tf_idf = (1 + math.log(float(document['postings'][i]['frequency']))) * idf
            # temp_post is a dictionary of the current posting from the postings list
            temp_post = document['postings'][i]
            # sets the tf-idf of the current posting
            temp_post['tf_idf'] = tf_idf
            # adds the updated posting with the tf-idf to the postings list
            newPostings.append(temp_post)
            i += 1
        # replaces the old postings list that is missing tf-idfs with the new updated postings list
        collection.find_one_and_replace({'_id': entryID}, {'postings': newPostings})
        print(f'Calculated {entryID} postings TF-IDF.')
    return

if __name__ == "__main__":
    myClient = pymongo.MongoClient('mongodb://localhost:27017/')
    mydb = myClient['myDatabase']
    myCollection = mydb['oneGramIndex']
    myData = loadBookkeeping()

    constructIndex(myData, myCollection)
    calculateTF_IDF(myCollection)
    addHTMLTags(myData, myCollection)
