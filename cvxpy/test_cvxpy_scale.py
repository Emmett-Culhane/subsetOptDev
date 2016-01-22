
# - test cvxpy opt scale

import numpy as np
from cvxpy import * 


# - init log testing 
solutionLog - []


# - define function 
def evalSubSum(rows, cats, upperBound): 
  mat = np.random.randint(10, upperBound, (rows, cats))
  vec = np.round(np.random.rand(cats))
  solution_vec = []
  for i in mat: 
      t = sum(i * vec)
      solution_vec.append(t)
  # run operation
  A   = mat
  x   = Bool(A.shape[1])
  y   = solution_vec
  out = Problem(Minimize(sum_squares(A*x - y)), []).solve()
  sol = np.array(np.round(x.value + 0.001).T)[0]
  ## look at errors in boolean object
  diff_mat = [] 
  for k in range(0, cats): 
    sub = np.absolute(vec[k] - sol[k])
    diff_mat.append(sub)
  # payload
  l = {
    'sumSq'   : np.round(out), 
    'boolErr' : sum(diff_mat), 
    'rows'    : rows, 
    'cats'    : cats, 
    'bound'   : upperBound
  }
  solutionLog.append(l)
  return l



# - evaluate
evalSubSum(10, 10, 100)

