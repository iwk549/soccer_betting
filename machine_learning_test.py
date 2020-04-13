import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn import svm


"""Perform cross validation test for gathered results to find best evaluator"""


"""initialize scalers and parameter grids"""
scaler = MinMaxScaler()
gscv_svc_param_grid = [
    {'C': [1, 10, 100, 1000], 'kernel': ['linear']},
    {'C': [1, 10, 100, 1000], 'gamma': [0.001, 0.0001], 'kernel': ['rbf']}
]
gscv_knn_param_grid = {'n_neighbors': np.arange(1, 26)}

"""Pull in data and process"""
# import data and select columns needed
training_data = pd.read_excel('All Soccer Results.xlsx', sheet_name='Sheet1')
# replace spaces in column headers with underscores
training_data.columns = [c.lower().replace(' ', '_') for c in training_data.columns]
# remove pushed games
spread_data = training_data.drop(training_data[training_data.spread_winner == 'Push'].index)
line_data = training_data.drop(training_data[training_data.over_under_winner == 'Push'].index)


"""FOR SPREAD RESULTS"""

# prediction column variables
spread_prediction_columns = ['ht_spread',
                             'ht_spread_fract',
                             'at_spread_fract',
                             ]
# split data into X and y sets and scale data
spread_x = scaler.fit_transform(spread_data[spread_prediction_columns])
spread_y = spread_data['spread_winner']

# find optimal estimators using cross validation
# for SVC
spread_svc_gscv = GridSearchCV(estimator=svm.SVC(), param_grid=gscv_svc_param_grid, n_jobs=-1,
                               cv=5, iid=True)
spread_svc_gscv.fit(spread_x, spread_y)
spread_svc_kernel = spread_svc_gscv.best_estimator_.kernel
spread_svc_gamma = spread_svc_gscv.best_estimator_.gamma
spread_svc_c = spread_svc_gscv.best_estimator_.C
# for KNN
spread_knn_gscv = GridSearchCV(estimator=KNeighborsClassifier(), param_grid=gscv_knn_param_grid,
                               cv=5, iid=True)
spread_knn_gscv.fit(spread_x, spread_y)
spread_knn_k = next(iter(spread_knn_gscv.best_params_.values()))

# get cross validation scores
spread_svc_cv_score = np.mean(cross_val_score(svm.SVC(kernel=spread_svc_kernel, C=spread_svc_c,
                                                      gamma=spread_svc_gamma),
                                              spread_x, spread_y, cv=5))
spread_knn_cv_score = np.mean(cross_val_score(KNeighborsClassifier(n_neighbors=spread_knn_k),
                                              spread_x, spread_y, cv=5))


"""FOR LINE RESULTS"""

# prediction column variables
line_prediction_columns = ['over_under',
                           'over_fract',
                           'under_fract',
                           ]
# split data into X and y sets and scale data
line_x = scaler.fit_transform(line_data[line_prediction_columns])
line_y = line_data['over_under_winner']

# find optimal estimators using cross validation
# for SVC
line_svc_gscv = GridSearchCV(estimator=svm.SVC(), param_grid=gscv_svc_param_grid, n_jobs=-1,
                             cv=5, iid=True)
line_svc_gscv.fit(line_x, line_y)
line_svc_kernel = line_svc_gscv.best_estimator_.kernel
line_svc_gamma = line_svc_gscv.best_estimator_.gamma
line_svc_c = line_svc_gscv.best_estimator_.C
# for KNN
line_knn_gscv = GridSearchCV(estimator=KNeighborsClassifier(), param_grid=gscv_knn_param_grid,
                             cv=5, iid=True)
line_knn_gscv.fit(line_x, line_y)
line_knn_k = next(iter(line_knn_gscv.best_params_.values()))

# get cross validation score
line_svc_cv_score = np.mean(cross_val_score(svm.SVC(kernel=line_svc_kernel,
                                                          C=line_svc_c,
                                                          gamma=line_svc_gamma),
                                            line_x, line_y, cv=5))
line_knn_cv_score = np.mean(cross_val_score(KNeighborsClassifier(n_neighbors=line_knn_k),
                                            line_x, line_y, cv=5))


"""PRINT OUTPUTS"""

print(str(training_data.shape[0]), 'records in the original dataset.')

print('\n______CROSS VALIDATIONS______')
print('\n\n_Support Vector Classification Predictions_')
print('\nSpread Results')
print('\tKernel:', spread_svc_kernel, '\tC:', spread_svc_c, '\tGamma:', spread_svc_gamma)
print('\tcv Score:', str(round(spread_svc_cv_score, 2)))

print('\nOver Under Results')
print('\tKernel:', line_svc_kernel, '\tC:', line_svc_c, '\tGamma:', line_svc_gamma)
print('\tcv Score:', str(round(line_svc_cv_score, 2)))

print('\n\n_Known Nearest Neighbors Predictions_')
print('\nSpread Results')
print('\tk:', spread_knn_k)
print('\tcv Score:', str(round(spread_knn_cv_score, 2)))

print('\nOver Under Results')
print('\tk:', line_knn_k)
print('\tcv Score:', str(round(line_knn_cv_score, 2)))
