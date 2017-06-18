#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division
import nltk
import os
import random
from collections import Counter
# from nltk import word_tokenize
# from nltk.corpus import stopwords
# from stop_words import get_stop_word
from nltk import NaiveBayesClassifier, classify
import snowballstemmer
from nltk import wordpunct_tokenize

# stoplist = stopwords.words('english')
# stoplist1 = get_stop_words('tr')
stoplist = nltk.corpus.stopwords.words('turkish')

'''
A turkish language based NB classifier inspired from tutorial in web page:
https://cambridgecoding.wordpress.com/2016/01/25/implementing-your-own-spam-filter/
'''

def init_lists(folder):
    a_list = []
    file_list = os.listdir(folder)
    for a_file in file_list:
        f = open(folder + a_file, 'r')
        a_list.append(f.read())
    f.close()
    return a_list


def preprocess(sentence):
    stemmer = snowballstemmer.stemmer("turkish")
    return [stemmer.stemWord(word.lower()) for word in
            wordpunct_tokenize(str(sentence.encode('utf-8'), errors='ignore'))]


def get_features(text, setting):
    if setting == 'bow':
        return {word: count for word, count in
                Counter(preprocess(text)).items() if not word in stoplist}
    else:
        return {word: True for word in preprocess(text)
                if not word in stoplist}


def train(features, samples_proportion):
    train_size = int(len(features) * samples_proportion)
    # initialise the training and test sets
    train_set, test_set = features[:train_size], features[train_size:]
    print ('Training set size = ' + str(len(train_set)) + ' emails')
    print ('Test set size = ' + str(len(test_set)) + ' emails')
    # train the classifier
    classifier = NaiveBayesClassifier.train(train_set)
    return train_set, test_set, classifier


def evaluate(train_set, test_set, classifier):
    # check how the classifier performs on the training and test sets
    print ('Accuracy on the training set = ' +
           str(classify.accuracy(classifier, train_set)))
    print ('Accuracy of the test set = ' +
           str(classify.accuracy(classifier, test_set)))
    # check which words are most informative for the classifier
    classifier.show_most_informative_features(20)

if __name__ == "__main__":
    # initialise the data
    sensitive = init_lists('./dataset/HizmeteOzelTxt/')
    non_sensitive = init_lists('./dataset/TasnifDisiTxt/')
    all_emails = [(email, 'sensitive') for email in sensitive]
    all_emails += [(email, 'non_sensitive') for email in non_sensitive]
    random.shuffle(all_emails)
    print ('Corpus size = ' + str(len(all_emails)) + ' emails')

    # extract the features
    all_features = [(get_features(email, ''), label)
                    for (email, label) in all_emails]
    print ('Collected ' + str(len(all_features)) + ' feature sets')

    # train the classifier
    train_set, test_set, classifier = train(all_features, 0.8)

    # evaluate its performance
    evaluate(train_set, test_set, classifier)
