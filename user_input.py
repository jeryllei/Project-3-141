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
        userInput = input('Enter a query (type in \'quit\' to exit): ')
        if userInput == 'quit':
            print('Exiting program...')
            break
        
        # Handles input that is more than 1 word.
        if len(userInput.split(' ')) > 1:
            userInput = [inpu.lower() for inpu in userInput.split(' ')]
            i = 1

            for word in userInput:
                pass

        # Handles single word inputs.
        else:
            userInput = userInput.lower()
            if myCollection.find_one({'_id': userInput}) != None:
                # results is a list of dictionaries
                results = myCollection.find_one({'_id': userInput})['postings']
                i = 1
                for post in results:
                    result_docID = post['docID']
                    print(f'Result {i} of {len(results)}\tDocID: {result_docID}\tURL: {docIDs[result_docID]}')
                    i += 1
                print(f'End of query results. {len(results)} total results found.\n')
            else:
                print('Search query returned no results.\n')
    

