from flask import Flask
from flask import request
from os import listdir
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello world!'

@app.route('/number/<name>', methods=['GET', 'POST'])
def home(name):
    f = open('file.txt','w')
    a = request.args.get('key', '')
    f.write('answer:'+str(a))
    f.close()

    if(name == 'save'):
        number = request.args.get('number', -1)
        numberString = request.args.get('result', '');
        saveNumber(number, numberString)

    return  'hello'

def saveNumber(number, numberString):
    count = 0
    trainingFileList = listdir('trainingSet')          
    m = len(trainingFileList)

    for i in range(m):
        fileNameStr = trainingFileList[i]
        fileStr = fileNameStr.split('.')[0]     #take off .txt
        classNumStr = int(fileStr.split('_')[0])

        if classNumStr == int(number):
            count += 1

    f = open('trainingSet/' + number + '_' + str(count) + '.txt','w')
    f.write(numberString)
    f.close()


if __name__ == '__main__':
    app.run(debug=True)