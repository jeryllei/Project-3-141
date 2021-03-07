from collections import defaultdict
import pymongo
import json
import math
import os
from scipy import spatial

def loadBookkeeping():
    with open('WEBPAGES_RAW/bookkeeping.json', 'r') as json_file:
        data = json.load(json_file)
    return data

def calculateQueryTFIDF(query, collection, collectionSize):
    queryTFIDFs = defaultdict(float)
    normalizedTFIDFs = defaultdict(float)
    wordFrequency = defaultdict(int)
    for word in query:
        # TF is calculated using the raw number of occurences of the term in the search query.
        wordFrequency[word] += 1
    for word in query:
        if collection.find_one({'_id': word}) != None:
            df = len(collection.find_one({'_id': word})['postings'])
            tf_idf = wordFrequency[word] * math.log((collectionSize / df), 10)
            queryTFIDFs[word] += tf_idf
        else:
            queryTFIDFs[word] += 0
    queryLength = math.sqrt(sum([tf_idf**2 for tf_idf in list(queryTFIDFs.values())]))
    for word, tf_idf in queryTFIDFs.items():
        normalizedTFIDFs[word] = tf_idf * queryLength
    return normalizedTFIDFs

def createDocVectors(query, collection):
    # document vector structure:
    '''
    {docID1: [tf-idf1, tf-idf2], docID2: [tf-idf1, tf-idf2]}
    '''
    docVectors = defaultdict(list)
    listOfPostings = []
    # Grab all postings for the query
    for term in query:
        termPostings = collection.find_one({'_id': term})
        if termPostings != None:
            listOfPostings.append(termPostings['postings'])
        else:
            listOfPostings.append([])
    # Initializes docVectors with every docID that is found by the query
    for postings in listOfPostings:
        for posting in postings:
            docVectors[posting['docID']] = []
    # Grabs all docIDs from document vectors.
    docIDs = list(docVectors.keys())
    for postings in listOfPostings:
        # postingsIDs is the list of docIDs in that particular postings
        postingsIDs = []
        for posting in postings:
            postingsIDs.append(posting['docID'])
        # If document in docIDs was not found in the postings list, then it is assigned a score of 0 for that term.
        for docID in docIDs:
            if docID not in postingsIDs:
                docVectors[docID].append(0)
        # Assigns the tf-idf scores to document vectors
        for posting in postings:
            docVectors[posting['docID']].append(posting['tf_idf'])
    # Normalize tf-idf scores
    for docID, tf_idfs in docVectors.items():
        docLength = math.sqrt(sum([tf_idf**2 for tf_idf in tf_idfs]))
        docVectors[docID] = [tf_idf / docLength for tf_idf in tf_idfs]
    return docVectors

# Function to print out results of the search query. Limited to 20 results, extra results are truncated.
def printResults(rankedDocIDs, docIDs):
    if len(rankedDocIDs) > 0:
        i = 1
        if len(rankedDocIDs) <= 20:
            for docID in rankedDocIDs:
                print(f'Result {i} of {len(rankedDocIDs)}\tURL: {docIDs[docID]}')
                i += 1
        else:
            for docID in rankedDocIDs:
                print(f'Result {i} of {len(rankedDocIDs)}\tURL: {docIDs[docID]}')
                i += 1
                if i > 20:
                    break
    else:
        print(f'Search query returned no results.\n')

# Prints out results of the search query, with docIDs but no URLs attached. URLs are printed out in a file instead.
def printResultsDebug(rankedDocIDs, docIDs):
    file = open('output.txt', 'w')
    if len(rankedDocIDs) > 0:
        i = 1
        if len(rankedDocIDs) <= 20:
            for docID in rankedDocIDs:
                print(f'Result {i} of {len(rankedDocIDs)}\tDocID: {docID}')
                file.write(docIDs[docID] + '\n')
                i += 1
        else:
            for docID in rankedDocIDs:
                print(f'Result {i} of {len(rankedDocIDs)}\tDocID: {docID}')
                file.write(docIDs[docID] + '\n')
                i += 1
                if i > 20:
                    break
    file.close()

# Structure of DB:
'''
{
    '_id': 'token',
    'postings': [{'docID': '0/11', 'frequency': 10, 'tf_idf': 2, 'tags':['h1', 'h2', 'title', 'strong']}, {'docID': '0/34', 'frequency': 10, 'tf_idf': 4, 'tags':[]}]
}
'''
if __name__ == '__main__':
    debugMode = False
    myClient = pymongo.MongoClient('mongodb://localhost:27017/')
    mydb = myClient['myDatabase']
    myCollection = mydb['oneGramIndex']

    docIDs = loadBookkeeping()
    collectionNumber = float(myCollection.count_documents({}))
    # Weighting scheme is ltc.ntc
    debugModeInput = input('Enter debug mode (Y/N): ').lower()
    if debugModeInput == 'y':
        debugMode = True
        # Count number of unique docIDs in the index.
        '''uniqueDocIDs = set()
        cursors = myCollection.find()
        for document in cursors:
            for posting in document['postings']:
                uniqueDocIDs.add(posting['docID'])
        print('Number of unique docIDs: ' + str(len(uniqueDocIDs)))'''
    while True:
        # Gets the user input and lower cases it. Index is also constructed with lower cased entries.
        userInput = input('Enter a query (type in \'quit\' to exit): ').lower()
        if userInput == 'quit':
            print('Exiting program...')
            break
        
        # document vectors structure:
        '''
        {docID1: [tf-idf1, tf-idf2], docID2: [tf-idf1, tf-idf2]}
        '''
        query = userInput.split(' ')
        queryTF_IDF = list(calculateQueryTFIDF(query, myCollection, collectionNumber).values())
        documentVectors = createDocVectors(query, myCollection)
        documentCosineScores = defaultdict(float)
        numDocs = len(documentVectors.keys())
        x = 0
        for docID, tf_idfs in documentVectors.items():
            # calculating cosine similarity
            documentCosineScores[docID] += 1 - spatial.distance.cosine(queryTF_IDF, tf_idfs)
            if debugMode:
                print(f'Working on {x} out of {numDocs}')
            # adding HTML tag weighting
            for term in query:
                collectionResult = myCollection.find_one({'_id': term})
                if collectionResult != None:
                    postings = collectionResult['postings']
                    for posting in postings:
                        numTags = len(posting['tags'])
                        if numTags > 0 and posting['docID'] == docID:
                            documentCosineScores[docID] += numTags
                            break
            x += 1
        rankedIDs = [docID for docID, score in sorted(documentCosineScores.items(), key=lambda item: item[1], reverse=True)]
        # debugging is a dictionary of docID and scores
        debugging = {k: v for k, v in sorted(documentCosineScores.items(), key=lambda item: item[1], reverse=True)}
        if debugMode:
            printResultsDebug(rankedIDs, docIDs)
            i = 0
            for doc, score in debugging.items():
                print(f'{doc} with a score of {score}')
                i += 1
                if i > 20:
                    break
        else:
            printResults(rankedIDs, docIDs)