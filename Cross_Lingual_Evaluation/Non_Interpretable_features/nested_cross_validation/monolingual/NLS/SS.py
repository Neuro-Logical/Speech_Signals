#!/usr/bin/env python
# coding: utf-8

# #% parts indicate changes by yiting
import pdb
from PCA_PLDA_EER_Classifier import PCA_PLDA_EER_Classifier
from statistics import mode
import random
random.seed(20)

import pandas as pd
import numpy as np
from sklearn.utils import shuffle
import os
import sys
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RepeatedStratifiedKFold


# !!!!!!!!!!!!!!!!!!!!!!!!
# set test_only = 0 if doing hyperparameter search. 
# uncomment best_param part under "for feat_used in ['xvector','trill']:", 
# set hyperparamters there, and set test_only = 1 if skipping hyperparameter search 
# !!!!!!!!!!!!!!!!!!!!!!!!
test_only = 0
feat_pth = sys.argv[1] # folder with saved feature files

#% try two feats
best_param_init =  {
            'xvector': 30,
            'trill': 25,
            }

def get_n_folds(arrayOfSpeaker):
    data = list(arrayOfSpeaker)  # list(range(len(arrayOfSpeaker)))
    num_of_folds = 10
    n_folds = []
    for i in range(num_of_folds):
        n_folds.append(data[int(i * len(data) / num_of_folds):int((i + 1) * len(data) / num_of_folds)])
    return n_folds

def normalize(train_split, test_split):
    train_set = train_split
    test_set = test_split
    # np.random.shuffle(tot)

    feat_train = train_set[:, :-1]
    lab_train = train_set[:, -1:]
    lab_train = lab_train.astype('int')

    feat_test = test_set[:, :-1]
    lab_test = test_set[:, -1:]
    lab_test = lab_test.astype('int')

    # X = StandardScaler().fit_transform(matrix_feat)

    X_train, X_test, y_train, y_test = feat_train, feat_test, lab_train, lab_test
    y_test = y_test.ravel()
    y_train = y_train.ravel()
    X_train = X_train.astype('float')
    X_test = X_test.astype('float')
    normalized_test_X = (X_test - X_train.mean(0)) / (X_train.std(0) + 0.01)
    normalized_train_X = (X_train - X_train.mean(0)) / (X_train.std(0) + 0.01)

    return normalized_train_X, normalized_test_X, y_train, y_test

#% try two feats
for feat_used in ['xvector','trill']:
    best_param = best_param_init[feat_used]
    print()
    print('---------------')
    print(feat_used)
    print('---------------')

    # get dataframe of all recordings with labels, filter out invalid speakers
    nls = pd.read_csv("/export/b15/afavaro/Frontiers/submission/Statistical_Analysis/NLS/total_new_training.csv")
    nls = nls.drop(columns=['Unnamed: 0'])
    nls = nls.dropna()

    nls['task'] = [m.split("_", 3)[3].split(".wav")[0] for m in nls['names'].tolist()]
    task = ['CookieThief']
    nls = nls[nls['task'].isin(task)]

    nls = nls.sort_values(by=['names'])
    nls['id'] = [m.split("_ses")[0] for m in nls['names'].tolist()]
    nls.columns.tolist()

    label_seneca = pd.read_excel("/export/b15/afavaro/Book3.xlsx")
    label = label_seneca['Label'].tolist()
    speak = label_seneca['Participant I.D.'].tolist()
    spk2lab_ = {sp: lab for sp, lab in zip(speak, label)}
    speak2__ = nls['id'].tolist()

    etichettex = []
    for nome in speak2__:
        if nome in spk2lab_.keys():
            lav = spk2lab_[nome]
            etichettex.append(([nome, lav]))
        else:
            etichettex.append(([nome, 'Unknown']))

    label_new_ = []
    for e in etichettex:
        label_new_.append(e[1])
    nls['label'] = label_new_

    label = label_seneca['Age'].tolist()
    speak = label_seneca['Participant I.D.'].tolist()
    spk2lab_ = {sp: lab for sp, lab in zip(speak, label)}
    speak2__ = nls['id'].tolist()

    etichettex = []
    for nome in speak2__:
        if nome in spk2lab_.keys():
            lav = spk2lab_[nome]
            etichettex.append(([nome, lav]))
        else:
            etichettex.append(([nome, 'Unknown']))

    label_new_ = []
    for e in etichettex:
        label_new_.append(e[1])
    nls['age'] = label_new_

    TOT = nls.groupby('label')
    PD = TOT.get_group('PD')
    ctrl = TOT.get_group('CTRL')  # .grouby('ID')
    #ctrl = ctrl[ctrl['age'] > 68]

    PD = PD[~PD.id.str.contains("NLS_116")]
    PD = PD[~PD.id.str.contains("NLS_34")]
    PD = PD[~PD.id.str.contains("NLS_35")]
    PD = PD[~PD.id.str.contains("NLS_33")]
    PD = PD[~PD.id.str.contains("NLS_12")]
    PD = PD[~PD.id.str.contains("NLS_21")]
    PD = PD[~PD.id.str.contains("NLS_20")]
    PD = PD[~PD.id.str.contains("NLS_12")]

    ctrl = ctrl[~ctrl.id.str.contains("PEC_4")]
    ctrl = ctrl[~ctrl.id.str.contains("PEC_5")]
    ctrl = ctrl[~ctrl.id.str.contains("PEC_9")]
    ctrl = ctrl[~ctrl.id.str.contains("PEC_14")]
    ctrl = ctrl[~ctrl.id.str.contains("PEC_15")]
    ctrl = ctrl[~ctrl.id.str.contains("PEC_16")]
    ctrl = ctrl[~ctrl.id.str.contains("PEC_17")]
    ctrl = ctrl[~ctrl.id.str.contains("PEC_18")]
    ctrl = ctrl[~ctrl.id.str.contains("PEC_19")]
    ctrl = ctrl[~ctrl.id.str.contains("PEC_23")]
    ctrl = ctrl[~ctrl.id.str.contains("PEC_25")]
    ctrl = ctrl[~ctrl.id.str.contains("PEC_29")]
    ctrl = ctrl[~ctrl.id.str.contains("PEC_35")]

    test = pd.concat([PD, ctrl])
    test = test.dropna()
    test = test.drop(columns=['age'])

    new = []
    for m in test['label'].tolist():
        if m == 'PD':
            new.append(1)
        if m == 'CTRL':
            new.append(0)
    test['label'] = new


    # get speakers
    gr = test.groupby('label')
    ctrl_ = gr.get_group(0)
    pd_ = gr.get_group(1)

    arrayOfSpeaker_cn = ctrl_['id'].unique()
    random.shuffle(arrayOfSpeaker_cn)

    arrayOfSpeaker_pd = pd_['id'].unique()
    random.shuffle(arrayOfSpeaker_pd)

    cn_sps = get_n_folds(arrayOfSpeaker_cn)
    pd_sps = get_n_folds(arrayOfSpeaker_pd)


    # generate train/test splits for outer folds
    data = []
    for cn_sp, pd_sp in zip(sorted(cn_sps, key=len), sorted(pd_sps, key=len, reverse=True)):
        data.append(cn_sp + pd_sp)
    n_folds = sorted(data, key=len, reverse=True)

    folds = []
    for i in n_folds:
        data_fold = np.array(()) #%
        data_i = test[test["id"].isin(i)]
        #% extract features from files
        for index, row in data_i.iterrows():
            name_no_exten = os.path.splitext(row['names'])[0] # remove file extension if any
            label_row = row['label']
            feat = np.load(feat_pth+feat_used+'/' + name_no_exten + '.npy')
            feat = np.append(feat,label_row) # attach label to the end of array [1, feat dim + 1]
            data_fold = np.vstack((data_fold, feat)) if data_fold.size else feat
        # data_i = data_i.drop(columns=['names', 'id', 'task'])
        # folds.append((data_i).to_numpy())
        folds.append(data_fold)

    data_train_1 = np.concatenate(folds[:9])
    data_test_1 = np.concatenate(folds[-1:])

    data_train_2 = np.concatenate(folds[1:])
    data_test_2 = np.concatenate(folds[:1])

    data_train_3 = np.concatenate(folds[2:] + folds[:1])
    data_test_3 = np.concatenate(folds[1:2])

    data_train_4 = np.concatenate(folds[3:] + folds[:2])
    data_test_4 = np.concatenate(folds[2:3])

    data_train_5 = np.concatenate(folds[4:] + folds[:3])
    data_test_5 = np.concatenate(folds[3:4])

    data_train_6 = np.concatenate(folds[5:] + folds[:4])
    data_test_6 = np.concatenate(folds[4:5])

    data_train_7 = np.concatenate(folds[6:] + folds[:5])
    data_test_7 = np.concatenate(folds[5:6])

    data_train_8 = np.concatenate(folds[7:] + folds[:6])
    data_test_8 = np.concatenate(folds[6:7])

    data_train_9 = np.concatenate(folds[8:] + folds[:7])
    data_test_9 = np.concatenate(folds[7:8])

    data_train_10 = np.concatenate(folds[9:] + folds[:8])
    data_test_10 = np.concatenate(folds[8:9])


    # inner folds cross-validation - hyperparameter search
    if test_only == 0:
        best_params = []
        for i in range(1, 11):

            print(i)

            normalized_train_X, normalized_test_X, y_train, y_test = normalize(eval(f"data_train_{i}"),
                                                                                            eval(f"data_test_{i}"))
            #%
            tuned_params = {"PCA_n" : [5,10,15,20,25,30,35,40]} # cookiethief 40, rainbowpassage 35, joke 30, poem 35
            model = PCA_PLDA_EER_Classifier(normalize=0)

            cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=5, random_state=1)
            grid_search = GridSearchCV(estimator=model, param_grid=tuned_params, n_jobs=-1, cv=cv, scoring='accuracy', error_score=0)
            grid_result = grid_search.fit(normalized_train_X, y_train)
            # summarize result
        # print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
            print(grid_result.best_params_)

            means = grid_result.cv_results_['mean_test_score']
            stds = grid_result.cv_results_['std_test_score']
            params = grid_result.cv_results_['params']
            print(means)

            best_params.append(grid_result.best_params_['PCA_n'])
            
        # get best params
        print('**********best pca n:')
        best_param = mode(best_params)
        print(best_param)


    # outer folds testing
    predictions = []
    truth = []
    test_scores = []
    for i in range(1, 11):

        normalized_train_X, normalized_test_X, y_train, y_test = normalize(eval(f"data_train_{i}"), eval(f"data_test_{i}"))
        y_test = y_test.tolist()
        model = PCA_PLDA_EER_Classifier(PCA_n=best_param,normalize=0)
        model.fit(normalized_train_X, y_train)
        grid_predictions = model.predict(normalized_test_X)
        grid_test_scores = model.predict_scores_list(normalized_test_X)

        predictions = predictions + grid_predictions
        truth = truth + y_test
        test_scores += grid_test_scores[:,0].tolist()

    # report
    print()
    print(classification_report(truth, predictions, output_dict=False))
    print(confusion_matrix(truth, predictions))

    tn, fp, fn, tp = confusion_matrix(truth, predictions).ravel()
    specificity = tn / (tn+fp)
    sensitivity = tp/ (tp+fn)
    print('specificity')
    print(specificity)
    print('sensitivity')
    print(sensitivity)
    print('ROC_AUC')
    print(roc_auc_score(truth,test_scores))
    print('----------')

print()
print('PD, HC')
print((arrayOfSpeaker_pd.shape[0],arrayOfSpeaker_cn.shape[0]))
print()


