
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import statsmodels.api


def compute_correlation_updrs(dataframe):
    """Compute correlation between biomarker values and UPDRS scores.
    dataframe: pandas dataframe where the columns represent the features,
    each row corresponds to a different subject and a single column contains the UPDRS score
    for each of the subject"""

    biomarkers = dataframe.iloc[:, :-7].dropna()
    updrs_pd = biomarkers['updrs'].tolist()
    feats = biomarkers.columns.values.tolist()
    file = []
    p_vals = []

    for fea in feats:
        data = atx[fea].tolist()
        corr, _ = spearmanr(data, updrs_pd)
        p_vals.append(_)
        file.append((f'Spearm correlation for feats {fea}: p_value {_} and correlation coeff is {corr}'))
        # print spearman's correlation values and respective p-value
       # if _ < 0.05:
         #   print(f'p_value pearson correlation for feats {fea} is {_} \n and value is {corr}')

    # Apply FDR correction
    res = statsmodels.stats.multitest.fdrcorrection(p_vals, alpha=0.05, method='indep', is_sorted=False)
    ows = np.where(res[1][:, ] < 0.05)
    l = list(ows[0])
    values = res[1][l]
    for m in zip(l, values):
        print(m, feats[m[0]])
