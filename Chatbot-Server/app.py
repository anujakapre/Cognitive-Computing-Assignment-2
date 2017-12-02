import numpy as np
import pickle
import tensorflow as tf
from flask import Flask, jsonify, render_template, request
import model
#import fcntl
FB_ACCESS_TOKEN ='EAAB6uiRvoZBMBAI1iIxQwvCZB65QZAdmsYgsOToj82fkB8xBQVAP7lqZA3vmJ4GIeA0gBVdmr5ZCrimj7ugPnkcGArFduZApIJqeqy9pjzV7TtWrZAte24OxHNyfAizVMlhZBfTDsoDARVMH9T2JLZAFFhh8L28BCOb5vZAsxt6hMPOvZAK3kFYdD1m'
FB_VERIFY_TOKEN = 'allonsy'
API_KEY='2f77d7e61e6962a55a93c88383cc9b75'

# Load in data structures
with open("data/wordList.txt", "rb") as fp:
    wordList = pickle.load(fp)
wordList.append('<pad>')
wordList.append('<EOS>')

# Load in hyperparamters
vocabSize = len(wordList)
batchSize = 24
maxEncoderLength = 15
maxDecoderLength = 15
lstmUnits = 112
numLayersLSTM = 3

# Create placeholders
encoderInputs = [tf.placeholder(tf.int32, shape=(None,)) for i in range(maxEncoderLength)]
decoderLabels = [tf.placeholder(tf.int32, shape=(None,)) for i in range(maxDecoderLength)]
decoderInputs = [tf.placeholder(tf.int32, shape=(None,)) for i in range(maxDecoderLength)]
feedPrevious = tf.placeholder(tf.bool)

encoderLSTM = tf.nn.rnn_cell.BasicLSTMCell(lstmUnits, state_is_tuple=True)
#encoderLSTM = tf.nn.rnn_cell.MultiRNNCell([singleCell]*numLayersLSTM, state_is_tuple=True)
decoderOutputs, decoderFinalState = tf.contrib.legacy_seq2seq.embedding_rnn_seq2seq(encoderInputs, decoderInputs, encoderLSTM, 
                                                            vocabSize, vocabSize, lstmUnits, feed_previous=feedPrevious)

decoderPrediction = tf.argmax(decoderOutputs, 2)

# Start session and get graph
sess = tf.Session()
#y, variables = model.getModel(encoderInputs, decoderLabels, decoderInputs, feedPrevious)

# Load in pretrained model
saver = tf.train.Saver()
saver.restore(sess, tf.train.latest_checkpoint('models'))
zeroVector = np.zeros((1), dtype='int32')

def pred(inputString):
    inputVector = model.getTestInput(inputString, wordList, maxEncoderLength)
    feedDict = {encoderInputs[t]: inputVector[t] for t in range(maxEncoderLength)}
    feedDict.update({decoderLabels[t]: zeroVector for t in range(maxDecoderLength)})
    feedDict.update({decoderInputs[t]: zeroVector for t in range(maxDecoderLength)})
    feedDict.update({feedPrevious: True})
    ids = (sess.run(decoderPrediction, feed_dict=feedDict))
    return model.idsToSentence(ids, wordList)

# webapp
app = Flask(__name__)


@app.route('/prediction', methods=['POST', 'GET'])
def prediction():
   print("Data received:",request.form['msg'])
   response =  pred(str(request.form['msg']))
   return jsonify(response)

@app.route('/')
def main():
   return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)