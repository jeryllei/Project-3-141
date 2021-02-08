from nltk.stem import WordNetLemmatizer
import json
from index import Index

# Loads in the bookkeeping.json as a dictionary.
def loadBookkeeping():
    with open('WEBPAGES_RAW/bookkeeping.json', 'r') as json_file:
        data = json.load(json_file)
    return data


if __name__ == '__main__':
    myIndex = Index()
    bookKeeper = loadBookkeeping()
    

    '''
    while True:
        userInput = input('Enter a query (type in \'quit\' to exit): ')
        userInput = userInput.lower()
        if userInput == 'quit':
            break
    '''

