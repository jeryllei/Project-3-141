from collections import defaultdict
import pymongo
import json

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
if __name__ == '__main__':
    myClient = pymongo.MongoClient('mongodb://localhost:27017/')
    mydb = myClient['myDatabase']
    myCollection = mydb['testIndex']

    docIDs = loadBookkeeping()
    
    while True:
        userInput = input('Enter a query (type in \'quit\' to exit): ').lower()
        if userInput == 'quit':
            print('Exiting program...')
            break
        
        # Handles input that is more than 1 word.
        if len(userInput.split(' ')) > 1:
            userInput = [inpu for inpu in userInput.split(' ')]
            # ranked_results is a dictionary of docID keys and sum of tf-idf scores values.
            # Results that contain more parts of the query will be handled already by how a defaultdict functions.
            ranked_results = defaultdict(float)
            # ranked_IDs is a list of document IDs, in descending order of scores.
            ranked_IDs = []

            # For each word in the user input, it finds if it is in the index and collects the documents and tf-idf scores associated with them into ranked_results.
            for word in userInput:
                word_results = myCollection.find_one({'_id': word})
                if word_results != None:
                    # word results is the postings list for a token
                    word_results = word_results['postings']
                    # Assign docID and tf-idf pairs into ranked_results dictionary to be sorted later into ranked_IDs.
                    for post in word_results:
                        ranked_results[post['docID']] += post['tf_idf']
            
            # Sorting a dictionary by descending value and outputting keys to a list.
            # Modified code from: https://stackoverflow.com/a/613218
            ranked_IDs = [docID for docID, score in sorted(ranked_results.items(), key=lambda item: item[1], reverse=True)]

            i = 1
            if len(ranked_IDs) > 0:
                for docID in ranked_IDs:
                    print(f'Result {i} of {len(ranked_IDs)}\tDocID: {docID}\tURL: {docIDs[docID]}')
                    i += 1
                print(f'End of query results. {len(ranked_IDs)} total result(s) found.\n')
            else:
                print('Search query returned no results.\n')

        # Handles single word inputs.
        else:
            if myCollection.find_one({'_id': userInput}) != None:
                # Note: The code below is identical to the code used to handle multi-word input.
                ranked_results = defaultdict(float)
                ranked_IDs = []
                # results is a list of dictionaries
                results = myCollection.find_one({'_id': userInput})['postings']
                for post in results:
                    ranked_results[post['docID']] += post['tf_idf']
                ranked_IDs = [docID for docID, score in sorted(ranked_results.items(), key=lambda item: item[1], reverse=True)]
                i = 1
                if len(ranked_IDs) > 0:
                    for docID in ranked_IDs:
                        print(f'Result {i} of {len(ranked_IDs)}\tDocID: {docID}\tURL: {docIDs[docID]}')
                        i += 1
                    print(f'End of query results. {len(ranked_IDs)} total result(s) found. \n')
            else:
                print('Search query returned no results.\n')
    

