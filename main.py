from nltk.stem import WordNetLemmatizer
import json

# Loads in the bookkeeping.json as a dictionary.
def loadBookkeeping():
    with open('WEBPAGES_RAW/bookkeeping.json', 'r') as json_file:
        data = json.load(json_file)
    return data

def indexer():
    pass

# Creates an entry for the indexer.
def createEntry(token, docID):
    pass


if __name__ == '__main__':
    userInput = ''
    while True:
        userInput = input('Enter a query (type in \'quit\' to exit): ')
        userInput = userInput.lower()
        if userInput == 'quit':
            break

