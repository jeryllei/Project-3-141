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
        userInput = userInput.lower()
        if userInput == 'quit':
            break
        else:
            if myCollection.find_one({'_id': userInput}) != None:
                pass
            else:
                print('Search query returned no results.')
    

