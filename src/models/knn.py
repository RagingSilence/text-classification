# coding:utf-8

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.neighbors import KNeighborsClassifier

from src.utils.data_input import get_dataset

MAX_SEQUENCE_LENGTH = 100
EMBEDDING_DIM = 200
TEST_SPLIT = 0.2

train_texts, train_labels, test_texts, test_labels = get_dataset()
all_text = train_texts + test_texts

print("(2) doc to var...")

count_v0 = CountVectorizer()
counts_all = count_v0.fit_transform(all_text)
count_v1 = CountVectorizer(vocabulary=count_v0.vocabulary_)
counts_train = count_v1.fit_transform(train_texts)
print("the shape of train is ")
print(repr(counts_train.shape))
count_v2 = CountVectorizer(vocabulary=count_v0.vocabulary_)
counts_test = count_v2.fit_transform(test_texts)
print("the shape of train is ")
print(repr(counts_train.shape))

tfidftransformer = TfidfTransformer()
train_data = tfidftransformer.fit_transform(counts_train)
test_data = tfidftransformer.fit_transform(counts_test)

x_train = train_data
y_train = train_labels
x_test = test_data
y_test = test_labels

print("(3) KNN...")

for x in range(1, 15):
    knnclf = KNeighborsClassifier(n_neighbors=x)
    knnclf.fit(x_train, y_train)
    preds = knnclf.predict(x_test)
    num = 0
    preds = preds.tolist()
    for i, pred in enumerate(preds):
        if int(pred) == int(y_test[i]):
            num += 1
    print("precision_score:")
    print(str(float(num) / len(preds)))
