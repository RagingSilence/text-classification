from keras.preprocessing.text import Tokenizer
from keras.utils.np_utils import to_categorical
from keras.layers import Dense, Input, Flatten, Dropout
from keras.layers import LSTM, Embedding
from keras.models import Sequential
from keras.utils.vis_utils import plot_model

import numpy as np

from src.utils.data_input import get_dataset

MAX_SEQUENCE_LENGTH = 100
EMBEDDING_DIM = 200
VALIDATION_SPLIT = 0.16
TEST_SPLIT = 0.2

print("(1) load texts...")
train_texts, train_labels, test_texts, test_labels = get_dataset()
all_texts = train_texts + test_texts
all_labels = train_labels + test_labels

print("(2) doc to var...")

tokenizer = Tokenizer()
tokenizer.fit_on_texts(all_texts)
sequences = tokenizer.texts_to_sequences(all_texts)
word_index = tokenizer.word_index
print('Found %s unique tokens.' % len(word_index))
data = tokenizer.sequences_to_matrix(sequences, mode='tfidf')
labels = to_categorical(np.asarray(all_labels))
print('Shape of data tensor:', data.shape)
print('Shape of label tensor:', labels.shape)

print("(3) split data set...")
p1 = int(len(data) * (1 - VALIDATION_SPLIT - TEST_SPLIT))
p2 = int(len(data) * (1 - TEST_SPLIT))
x_train = data[:p1]
y_train = labels[:p1]
x_val = data[p1:p2]
y_val = labels[p1:p2]
x_test = data[p2:]
y_test = labels[p2:]
print("train docs: " + str(len(x_train)))
print("val docs: " + str(len(x_val)))
print("test docs: " + str(len(x_test)))

print("(5) training model...")

model = Sequential()
model.add(Dense(512, input_shape=(len(word_index) + 1,), activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(labels.shape[1], activation='softmax'))
model.summary()
# plot_model(model, to_file='model.png', show_shapes=True)

model.compile(loss='categorical_crossentropy',
              optimizer='rmsprop',
              metrics=['acc'])
print(model.metrics_names)
model.fit(x_train, y_train, validation_data=(x_val, y_val), epochs=2, batch_size=128)
# model.save('mlp.h5')

print("(6) testing model...")
print(model.evaluate(x_test, y_test))
