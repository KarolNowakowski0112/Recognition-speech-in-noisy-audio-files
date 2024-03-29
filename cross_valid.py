"""
Cross-validate models based on data in training set
"""


from sklearn.model_selection import KFold
import numpy as np
import pickle
from sklearn.mixture import GaussianMixture
import parametrization
import computing_gmm


def loadData(pathMFCC, pathMFCC_labels):
    with open(pathMFCC, 'rb') as fileMFCC:
        dataMFCC = pickle.load(fileMFCC)

    with open(pathMFCC_labels, 'rb') as fileMFCC_labels:
        dataMFCC_labels = pickle.load(fileMFCC_labels)

    return dataMFCC, dataMFCC_labels


def validateDigit(data, cfg, norm):
    """
    Cross-validate models
    :param data: matrix of mfcc matrices computed by parametrization.py
    :param cfg: config dictionary
    :param norm: normalize values in the matrix
    :return: confusion matrix for train-test data
    """

    kf = KFold(n_splits=int(len(data[0])/2), shuffle=False, random_state=None)

    """ Get indexes of train-test subsets """
    train_index = []
    test_index = []
    for train, test in kf.split(data[0]):
        train_index.append(train)
        test_index.append(test)
    train_index = np.asarray(train_index)
    test_index = np.asarray(test_index)

    print(train_index)
    print(test_index)

    rr_matrix = np.zeros((len(data), len(data[0])), dtype=int)
    tests = 0
    """ For each split """
    for i in range(len(train_index)):
        """ Split data into separate digits """
        models = []
        for digit in data:
            train_set = digit[train_index[i][0]]

            for index in train_index[i]:
                if not index == train_index[i][0]:
                    train_set = np.concatenate((train_set, digit[index]), axis=0)
            estimator = GaussianMixture(n_components=cfg['components'], max_iter=cfg['max_iterations'],
                                        tol=cfg['toleration'], covariance_type=cfg['covariance_type'])
            models.append(estimator.fit(train_set))
        models = np.asarray(models)

        """ For each speaker"""
        for j in range(len(test_index[i])):
            recog_matrix = []
            """ Check each digit """
            for digit in data:
                like = []
                recog = np.zeros((len(data), len(data[0])), dtype=int)
                """ Score it by fitted models """
                for model in models:
                    like.append(model.score(digit[test_index[i][j]]))
                """ Max likelihood is recognized digit """
                recog[like.index(max(like))] = 1
                recog_matrix.append(recog)

            """ Add it to recognition matrix """
            rr_matrix = np.add(rr_matrix, recog_matrix)
            tests += 1

    if norm:
        return np.asarray(rr_matrix / tests * 100).astype(int)
    else:
        return np.asarray(rr_matrix)


def main(normalized=True):
    """
    Calculate confusion matrix for previously parametrization train data based on kfold cross-validation
    :param normalized: should data in confusion matrix be in percent or in number of recognized samples
    :return: confusion matrix
    """


    data = parametrization.reconstruct('files/parametrization/parametrized_Mixed_snr_1_2')
    config = computing_gmm.load_config('files/config/gmm.cfg')

    MFCC = []
    MFCC_labels = []
    for key1 in data:
        MFCC_helpL = []
        MFCC_helpD = []
        for key2 in data[key1]:
            MFCC_helpL.append(key2)
            MFCC_helpD.append(data[key1][key2])
        MFCC_labels.append(MFCC_helpL)
        MFCC.append(MFCC_helpD)

    MFCC = MFCC[:len(MFCC)-1]
    MFCC_labels = MFCC_labels[:len(MFCC_labels)-1]
    print(MFCC_labels)
    print(validateDigit(MFCC, config, normalized))

main(normalized=True)