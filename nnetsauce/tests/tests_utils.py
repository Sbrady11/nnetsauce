import numpy as np
from sklearn import datasets
import nnetsauce.utils.psdcheck as psdx
import nnetsauce.utils.matrixops as mo
import nnetsauce.utils.misc as mx
import nnetsauce.utils.lmfuncs as lmf
import nnetsauce.utils.timeseries as ts 
import unittest as ut


# Basic tests

class TestUtils(ut.TestCase):

    
    # 1 - tests matrixops
    
    def test_crossprod(self):
        A = 2*np.eye(4)
        mo.crossprod(A)
        self.assertTrue(np.allclose(mo.crossprod(A), 
                                4*np.eye(4)))

    
    def test_tcrossprod(self):
        A = np.array([[ 1,  2],
                      [ 3,  4]])
        B = np.array([[ 4,  3],
                      [ 2,  1]])         
        self.assertTrue(np.allclose(mo.tcrossprod(A, B), 
                         np.array([[10,  4],
                                   [24, 10]]))) 

    
    def test_cbind(self): 
        A = np.array([[ 1,  2],
                      [ 3,  4]])
        B = np.array([[ 4,  3],
                      [ 2,  1]])         
        self.assertTrue(np.allclose(mo.cbind(A, B), 
                                np.array([[1, 2, 4, 3],
                                          [3, 4, 2, 1]]))) 
    
    
    def test_rbind(self): 
        A = np.array([[ 1,  2],
                      [ 3,  4]])
        B = np.array([[ 4,  3],
                      [ 2,  1]])         
        self.assertTrue(np.allclose(mo.cbind(A, B), 
                                np.array([[1, 2], 
                                          [3, 4],
                                          [4, 3], 
                                          [2, 1]])))
        
        
    # 2 - tests misc
    
    def test_merge_two_dicts(self):
        x = {"a": 3, "b": 5}
        y = {"c": 1, "d": 4}
        self.assertEqual(mx.merge_two_dicts(x, y),
                                {'a': 3, 'b': 5, 'c': 1, 'd': 4})


    # 3 - psd_check -----
    
    def test_psd_check(self):
        A = 2*np.eye(4)
        self.assertTrue(psdx.isPD(A))
        
        
    def test_nearestPD(self):
        A = np.array([[ 1,  2],
                      [ 3,  4]])
        self.assertTrue(np.allclose(psdx.nearestPD(A),
                        np.array([[ 1.31461828,  2.32186616],
                                  [ 2.32186616,  4.10085767]])))  

    
    # 4 - lm
    
    def test_inv_penalized_cov(self):
        X, y = datasets.make_regression(n_samples=5, 
                                n_features=2,
                                random_state=123)
        self.assertTrue(np.allclose(lmf.inv_penalized_cov(X, lam = 0.1), 
                         np.array([[0.1207683,  0.04333116],
                                   [0.04333116, 0.15787413]])))
    
    
    def test_lmf_beta_hat(self):
        X, y = datasets.make_regression(n_samples=5, 
                                n_features=2,
                                random_state=123)
        self.assertTrue(np.allclose(lmf.beta_hat(X, y, lam = 0.1), 
                         np.array([ 43.30170911,   5.68353528])))
    
    # 5 - MTS  
    
    def test_MTS_train_inputs(self):        
        np.random.seed(123)
        X = np.random.rand(5, 2)
        self.assertEqual(ts.create_train_inputs(X, 2)[1][1, 1],
                         0.42310646012446096)

    
    def test_MTS_reformat_response(self):
        np.random.seed(123)
        X = np.random.rand(5, 2)
        self.assertEqual(ts.reformat_response(X, 2)[1], 
                         0.28613933495)
        
    
# 5 - lm_funcs -----

# fit training set 

sigma = 0.3 
s = 4

print("4 - Bayesian Ridge ----- \n")

print('----- beta_Sigma_hat: fit_intercept = True, return_cov = True')
print("\n")
print(lmf.beta_Sigma_hat_rvfl(X = X, y = y,
                              s = s, sigma = sigma,
                              fit_intercept = True,
                              return_cov = True))
print("\n")

print('----- beta_Sigma_hat: fit_intercept = True, return_cov = False')
print("\n")
print(lmf.beta_Sigma_hat_rvfl(X = X, y = y,
                              s = s, sigma = sigma,
                              fit_intercept = True,
                              return_cov = False))
print("\n")

print('----- beta_Sigma_hat: fit_intercept = False, return_cov = False')
print("\n")
print(lmf.beta_Sigma_hat_rvfl(X = X, y = y,
                              s = s, sigma = sigma,
                              fit_intercept = False,
                              return_cov = False))
print("\n")

print('----- beta_Sigma_hat: fit_intercept = False, return_cov = True')
print("\n")
print(lmf.beta_Sigma_hat_rvfl(X = X, y = y,
                              s = s, sigma = sigma,
                              fit_intercept = False,
                              return_cov = True))
print("\n")

print('----- beta_Sigma_hat: fit_intercept = True, return_cov = True, X_star')
print("\n")
print(lmf.beta_Sigma_hat_rvfl(X = X, y = y, X_star = X,
                              s = s, sigma = sigma,
                              fit_intercept = True,
                              return_cov = True))
print("\n")

print('----- beta_Sigma_hat: fit_intercept = True, return_cov = False, X_star')
print("\n")
print(lmf.beta_Sigma_hat_rvfl(X = X, y = y, X_star = X,
                              s = s, sigma = sigma,
                              fit_intercept = True,
                              return_cov = False))
print("\n")

print('----- beta_Sigma_hat: fit_intercept = False, return_cov = False, X_star')
print("\n")
print(lmf.beta_Sigma_hat_rvfl(X = X, y = y, X_star = X,
                              s = s, sigma = sigma,
                              fit_intercept = False,
                              return_cov = False))
print("\n")

print('----- beta_Sigma_hat:  fit_intercept = False, return_cov = True, X_star')
print("\n")
print(lmf.beta_Sigma_hat_rvfl(X = X, y = y, X_star = X,
                              s = s, sigma = sigma,
                              fit_intercept = False,
                              return_cov = True))
print("\n")



fit_obj = lmf.beta_Sigma_hat_rvfl2(X = x, y = y, X_star = x,
                                  sigma = sigma,
                                  fit_intercept = True,
                                  return_cov = True)

# 6 - time series -----

