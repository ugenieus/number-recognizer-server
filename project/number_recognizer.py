from bsddb.dbtables import ExactCond
from flask import Flask
from flask import request
from os import listdir
from numpy import *
from flask import jsonify
import operator

TRAINING_SET_PATH = '/var/www/nr-api/trainingSet'

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello world!'

@app.route('/hello')
def hello():
    return 'hello'

@app.route('/number/<name>',  methods=['POST', 'GET'])
def home(name):
    if name == 'save':
        if request.method == 'POST':
            number = request.form['number']
            numberString = request.form['result']
        else:
            number = request.args.get('number', -1)
            numberString = request.args.get('result', '')
        saveNumber(number, numberString)
    elif name == 'classify':
        if request.method == 'POST':
            numberString = request.form['result']
        else:
            numberString = request.args.get('result', '')

        print numberString

        return classify(numberString)

    return jsonify(result=True)

def stringToArray(string):
    stringSize = len(string)
    width = 1

    while width * width < stringSize:
        width += 1

    stringArray = []
    for i in range(width):
        stringArray.append(string[i*width:(i+1)*width])
    return width, stringArray

def stringToVector(width, stringArray):
    returnVect = zeros((1,width * width))
    for i in range(width):
        for j in range(width):
            returnVect[0,width*i+j] = int(stringArray[j])

    return width, returnVect

def saveNumber(number, numberString):
    count = 0
    trainingFileList = listdir(TRAINING_SET_PATH)
    m = len(trainingFileList)

    width, stringVector = stringToArray(numberString)

    for i in range(m):
        fileNameStr = trainingFileList[i]
        fileStr = fileNameStr.split('.')[0]     #take off .txt
        classNumStr = int(fileStr.split('_')[0])

        if classNumStr == int(number):
            count += 1

    if(count >= 40):
        return

    f = open(TRAINING_SET_PATH + '/' + number + '_' + str(count) + '.txt','w')

    for i in range(len(stringVector)):
        f.write(stringVector[i]+'\n')

    f.close()

def classify(numberString):
    width, stringArray = stringToArray(numberString)
    width, stringVector = stringToVector(width, stringArray)

    hwLabels = []
    trainingFileList = listdir(TRAINING_SET_PATH)           #load the training set
    m = len(trainingFileList)
    trainingMat = zeros((m,width * width))

    for i in range(m):
        fileNameStr = trainingFileList[i]
        fileStr = fileNameStr.split('.')[0]     #take off .txt
        classNumStr = int(fileStr.split('_')[0])
        hwLabels.append(classNumStr)
        trainingMat[i,:] = img2vector(TRAINING_SET_PATH + '/' + fileNameStr, width)

    classifierResult = classify0(stringVector, trainingMat, hwLabels, 3)
    resultDic = {}

    for i in range(len(classifierResult)):
        print classifierResult[i][0]
        resultDic[str(i)] = classifierResult[i][0]

    return jsonify(reuslt=resultDic)

def classify0(inX, dataSet, labels, k):
    dataSetSize = dataSet.shape[0]
    diffMat = tile(inX, (dataSetSize,1)) - dataSet
    sqDiffMat = diffMat**2
    sqDistances = sqDiffMat.sum(axis=1)
    distances = sqDistances**0.5
    sortedDistIndicies = distances.argsort()
    classCount={}
    for i in range(k):
        voteIlabel = labels[sortedDistIndicies[i]]
        classCount[voteIlabel] = classCount.get(voteIlabel,0) + 1
    sortedClassCount = sorted(classCount.iteritems(), key=operator.itemgetter(1), reverse=True)
    return sortedClassCount

def file2matrix(filename):
    fr = open(filename)
    numberOfLines = len(fr.readlines())         #get the number of lines in the file
    returnMat = zeros((numberOfLines,3))        #prepare matrix to return
    classLabelVector = []                       #prepare labels return
    fr = open(filename)
    index = 0
    for line in fr.readlines():
        line = line.strip()
        listFromLine = line.split('\t')
        returnMat[index,:] = listFromLine[0:3]
        classLabelVector.append(int(listFromLine[-1]))
        index += 1
    return returnMat, classLabelVector

def autoNorm(dataSet):
    minVals = dataSet.min(0)
    maxVals = dataSet.max(0)
    ranges = maxVals - minVals
    normDataSet = zeros(shape(dataSet))
    m = dataSet.shape[0]
    normDataSet = dataSet - tile(minVals, (m,1))
    normDataSet = normDataSet/tile(ranges, (m,1))   #element wise divide
    return normDataSet, ranges, minVals

def img2vector(filename, width):
    returnVect = zeros((1,width*width))
    fr = open(filename)
    for i in range(width):
        lineStr = fr.readline()
        for j in range(width):
            try:
                returnVect[0,width*i+j] = int(lineStr[j])
            except Exception, e:
                returnVect[0,width*i+j] = 0

    return returnVect


if __name__ == '__main__':
    app.run(debug=True)