

# - test cvxpy functionality KC data


# - import dependancies

import cvxpy
import pandas as pd
from pprint import pprint
import numpy as np
from cvxpy import *
from operator import itemgetter
from itertools import groupby
import json
import pyproj
import csv
import decimal
from decimal import * 

# - load file (have to edit path/to/file)

jdata = json.loads(open('/Users/culhane/Desktop/formatted-data/fx3a-kauu.json').read())

KC = []

for i in jdata['fx3a-kauu']: 
    KC.append(i)

# - munge

rows = []
for i in range(0, len(KC)):
    out = { 
        'county'        : KC[i]['county'],
        'month'         : KC[i]['month'].zfill(2),
        'day'           : KC[i]['day'],
        'year'          : KC[i]['year'], 
        'value'         : KC[i]['permit_value'],
        'res_non'       : KC[i]['res_non'],
        'sf_mf'         : KC[i]['sf_mf'], 
        'struc_class'   : KC[i]['structure_class'], 
        'type'          : KC[i]['type'],
        'class_desc'    : KC[i]['class_description'],
        'units'         : KC[i]['dwelling_units_gained_or_lost']
    }
    out['group_id'] = (str(out['struc_class']).replace(' ','').lower()).replace('-', '')
    out['place_id'] = str(out['year']) + '_' + str(out['month'])
    rows.append(out)


df = pd.DataFrame(rows)
temp = df[df.year == '2011'].groupby(['month', 'group_id']).units.agg(lambda x: sum(map(int,x))).reset_index()
mat = temp.pivot(index= 'month', columns = 'group_id', values = 'units').fillna(0)
mat = np.array(mat)



# - evaluate

A = mat
x = Bool(A.shape[1])
y = np.array([18 , 36 , 39 , 37, 93 , 34, 35 , 69, 27, 36, 39 , 46])  # 2011

# alternative periods [2012, 2010, 10-12]

# y = np.array([35 , 46 , 50 , 128, 69 , 115, 43 , 342, 117, 42, 32 , 43]) # 2012
# y = np.array([9, 2, 134, 0, 7, 0, 1, 0, 5, 65, 25, 32]) # 2010
# y = np.array([9, 2, 134, 0, 7, 0, 1, 0, 5, 65, 25, 32, 18, 36, 39, 37, 93, 34, 35, 69, 27, 36, 39, 46, 35, 46, 50, 128, 69, 115, 43, 342, 117, 42, 32, 43])


sumSqrs      = Problem(Minimize(sum_squares(A*x - y)), []).solve()
solutionVec = np.round(x.value + 0.001).T 
residuals    = A.dot(np.round(x.value + 0.001)).T - y






# - parametrize as function

## nb. still have to fill out 10, 12 and entire year for values

targets = {
    'units' : { 
        '2010' : [9, 2, 134, 0, 7, 0, 1, 0, 5, 65, 25, 32],
        '2011' : [18 , 36 , 39 , 37, 93 , 34, 35 , 69, 27, 36, 39 , 46],
        '2012' : [35 , 46 , 50 , 128, 69 , 115, 43 , 342, 117, 42, 32 , 43],
        'whole': [9, 2, 134, 0, 7, 0, 1, 0, 5, 65, 25, 32, 18, 36, 39, 37, 93, 34, 35, 69, 27, 36, 39, 46, 35, 46, 50, 128, 69, 115, 43, 342, 117, 42, 32, 43]
    },
    'values' : { 
        '2010' : [1391229, 412678, 7077891, 0, 811496, 0, 193665, 0, 489182, 6707331, 4634302, 5755298],
        '2011' : [3485975, 6971951, 7552947, 7456003, 14283795, 6851462, 5927813, 9027256, 5440867, 7254489, 7859030, 879544],
        '2012' : [7052976, 8757487, 9681061, 15830215, 11815355, 17953634, 9164156, 25768056, 19997888, 4085964, 6819837, 8068326],
        'whole': [1391229, 412678, 7077891, 0, 811496, 0, 193665, 0, 489182, 6707331, 4634302, 5755298, 3485975, 6971951, 7552947, 7456003, 14283795, 6851462, 5927813, 9027256, 5440867, 7254489, 7859030, 879544, 7052976, 8757487, 9681061, 15830215, 11815355, 17953634, 9164156, 25768056, 19997888, 4085964, 6819837, 8068326]
    }
}


# - single value optimization 

solutionLogA = []

# parms [inputs --> ['units';'values']; period --> ['2010'; '2011'; '2012'; 'whole']; scale --> [int ie. 10,100,1000]

def evaluateSubset(inputs, period, scale): 
    df = pd.DataFrame(rows)
    if period == 'whole': 
        temp = df.groupby(['month', 'group_id']).units.agg(lambda x: sum(map(int,x)) / int(scale)).reset_index()
    else: 
        temp = df[df.year == period].groupby(['month', 'group_id']).units.agg(lambda x: sum(map(int,x)) / int(scale)).reset_index()
    ## solve 
    mat          = temp.pivot(index= 'month', columns = 'group_id', values = inputs).fillna(0)
    A            = np.array(mat)
    x            = Bool(A.shape[1])
    y            = np.array(targets[inputs][period]) 
    sumSqrs      = Problem(Minimize(sum_squares(A*x - y)), []).solve()
    solutionVec  = np.round(x.value + 0.001).T 
    residuals    = A.dot(np.round(x.value + 0.001)).T - y
    payload = {
        'units'       : inputs, 
        'period'      : period,
        'scale'       : scale,
        'sumSqrs'     : sumSqrs, 
        'solutionVec' : solutionVec,
        'residuals'   : residuals
    }
    solutionLogA.append(payload)
    return payload


# - evaluate

evaluateSubset('units', '2011', '1')




# - multi-value optimization 

solutionLogB = []

# parms [period --> ['2010'; '2011'; '2012'; 'whole']; scaleU --> [int ie. 1,10,100,1000]; scaleV --> [int ie. 10,100,1000]

def evaluateSubsets(period, scaleU, scaleV): 
    df = pd.DataFrame(rows)
    if period == 'whole': 
        tempU = df.groupby(['month', 'group_id']).units.agg(lambda x: sum(map(int,x)) / int(scaleU)).reset_index()
        tempV = df.groupby(['month', 'group_id']).value.agg(lambda x: sum(map(int,x)) / int(scaleV)).reset_index()
    else: 
        tempU = df[df.year == period].groupby(['month', 'group_id']).units.agg(lambda x: sum(map(int, x)) / int(scaleU)).reset_index()
        tempV = df[df.year == period].groupby(['month', 'group_id']).value.agg(lambda x: sum(map(int,x)) / int(scaleV)).reset_index()
    ## solve 
    matU         = tempU.pivot(index= 'month', columns = 'group_id', values = 'units').fillna(0)
    matV         = tempV.pivot(index= 'month', columns = 'group_id', values = 'value').fillna(0)
    A0           = np.array(matU)
    A1           = np.array(matV)
    x            = Bool(A0.shape[1])
    y0           = np.array(targets['units'][period]) 
    y1           = np.array(targets['values'][period])
    sumSqrs      = Problem(Minimize(sum_squares(A0*x - y0) + sum_squares(A1*x - y1)), []).solve()
    solutionVec  = np.round(x.value + 0.001).T 
    residualsU   = A0.dot(np.round(x.value + 0.001)).T - y0
    residualsV   = A1.dot(np.round(x.value + 0.001)).T - y1
    payload = {
        'period'      : period,
        'scaleU'      : scaleU,
        'scaleV'      : scaleV,
        'sumSqrs'     : sumSqrs, 
        'solutionVec' : solutionVec,
        'residualsU'  : residualsU,
        'residualsV'  : residualsV 
    }
    solutionLogB.append(payload)
    return payload


# - evaluate

evaluateSubsets('2011', '1', '1')




