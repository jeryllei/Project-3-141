

if __name__ == '__main__':
    userInput = ''
    while True:
        userInput = input('Enter a query (type in \'quit\' to exit): ')
        quitWords = ['quit', 'Quit', 'QUIT']
        if userInput in quitWords:
            break
        

