import time
import numpy as np
from cvxpy import * 

# - define function 
def evalSubSum(nrows, nlevs, entry_bound, entry_min = 10): 
    T   = time.time()
    
    data   = np.random.randint(entry_min, entry_bound, (nrows, nlevs))
    act    = (np.random.rand(nlevs) > 0.5) + 0
    target = data.dot(act)
    
    # run operation
    x    = Bool(nlevs)
    _    = Problem(Minimize(sum_squares(data * x - target)), []).solve()
    pred = np.array(np.round(x.value).T)[0].astype(int)
    
    # payload
    return {
    'residuals' : data.dot(pred) - target,
    'time'      : time.time() - T,
    'params' : {
            "nrows" : nrows,
            "nlevs" : nlevs,
            "entry_bound" : entry_bound
        }
    }

'''
# For example:

evalSubSum(**{
    "nrows"       : 100,
    "nlevs"       : 10,
    "entry_bound" : 100
})
'''