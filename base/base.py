import numpy as np
from numpy import linalg as la
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from ..utils import matrixops as mo
from ..simulation import nodesimulation as ns


# do DOCSTRINGS
# do GCV
class Base(object):
    """Base model with direct link and nonlinear activation.
        
       Parameters
       ----------
       n_hidden_features: int
           number of nodes in the hidden layer
       activation_name: str
           activation function: 'relu', 'tanh' or 'sigmoid'
       nodes_sim: str
           type of simulation for the nodes: 'sobol', 'hammersley', 'halton', 'uniform'
       bias: boolean
           indicates if the hidden layer contains a bias term or not
       type_clust: str
           type of clustering method: currently k-means ('kmeans') or Gaussian Mixture Model ('gmm')
       n_clusters: int
           number of clusters for 'kmeans' or 'gmm' clustering (could be 0: no clustering)
       seed: int 
           reproducibility seed for nodes_sim=='uniform'
    """
        
    
    # construct the object -----
    
    def __init__(self, n_hidden_features=5, 
                 activation_name='relu',
                 nodes_sim='sobol',
                 bias = True,
                 type_clust = 'kmeans',
                 n_clusters=2,
                 seed = 123):
        
        activation_options = {
            'relu': lambda x: np.maximum(x, 0),
            'tanh': lambda x: np.tanh(x),
            'sigmoid': lambda x: 1/(1+np.exp(-x))}
        
        self.n_hidden_features = n_hidden_features
        self.activation_name = activation_name
        self.activation_func = activation_options[activation_name]
        self.nodes_sim = nodes_sim
        self.bias = bias
        self.seed = seed
        self.type_clust = type_clust
        self.n_clusters = n_clusters
        self.clustering_obj = None
        self.clustering_scaler = None
        self.nn_scaler = None
        self.scaler = None
        self.encoder = None
        self.W = None
        self.X = None
        self.y = None
        self.y_mean = None
        self.beta = None

    
    # getter -----
    
    def get_params(self):
        
        return {'n_hidden_features': self.n_hidden_features, 
                'activation_name': self.activation_name, 
                'activation_func': self.activation_func,
                'nodes_sim': self.nodes_sim,
                'bias': self.bias,
                'seed': self.seed,
                'type_clust': self.type_clust,
                'n_clusters': self.n_clusters,
                'nn_scaler': self.nn_scaler,  
                'scaler': self.scaler,  
                'W': self.W, 
                'y_mean': self.y_mean}
    
    
    # setter -----
    
    def set_params(self, n_hidden_features=5, 
                   activation_name='relu', 
                   nodes_sim='sobol',
                   bias = True,
                   n_clusters=None,
                   seed=123):
        
        activation_options = {
            'relu': lambda x: np.maximum(x, 0),
            'tanh': lambda x: np.tanh(x),
            'sigmoid': lambda x: 1/(1+np.exp(-x))}
        
        self.n_hidden_features = n_hidden_features
        self.activation_name = activation_name
        self.activation_func = activation_options[activation_name]
        self.nodes_sim = nodes_sim
        self.bias = bias
        self.n_clusters = n_clusters
        self.seed = seed
    
    
    # fit -----
    
    def fit(self, X, y):
        """Fit training data (X, y).
        
        Parameters
        ----------
        X: {array-like}, shape = [n_samples, n_features]
            Training vectors, where n_samples
            is the number of samples and
        n_features is the number of features.
        
        y: array-like, shape = [n_samples]
               Target values.
               
        Returns
        -------
        self: object
        """
        
        centered_y, scaled_Z = self.preproc_training_set(y = y, X = X)
        self.beta = la.lstsq(scaled_Z, centered_y)[0]
        
        return self            
        
    
    # predict -----
    
    def predict(self, X):
        """Predict test data X.
        
        Parameters
        ----------
        X: {array-like}, shape = [n_samples, n_features]
            Training vectors, where n_samples
            is the number of samples and
        n_features is the number of features.
               
        Returns
        -------
        model predictions: {array-like}
        """
        
        if len(X.shape) == 1:
            n_features = X.shape[0]
            new_X = mo.rbind(X.reshape(1, n_features), 
                             np.ones(n_features).reshape(1, n_features))        
            
            return (self.y_mean + np.dot(self.preproc_test_set(new_X), 
                                        self.beta))[0]
        else:
            
            return self.y_mean + np.dot(self.preproc_test_set(X), 
                                        self.beta)
        
        
    # "preprocessing" methods to be inherited -----
    
    
    def encode_clusters(self, X=None, predict=False, **kwargs): # 
        """ Create new covariates with kmeans or GMM clustering. 

        Parameters
        ----------
        X: {array-like}, shape = [n_samples, n_features]
            Training vectors, where n_samples
            is the number of samples and
        n_features is the number of features.
        
        predict: boolean
            is False on training set and True on test set
        
        **kwargs: 
            additional parameters to be passed to clustering method  
            
        Returns
        -------
        clusters' matrix, one-hot encoded: {array-like}        
        """
        if (X is None):
            X = self.X
                
        if predict == False: # encode training set 
            
            # scale input data
            scaler = StandardScaler(copy=True, 
                                    with_mean=True, 
                                    with_std=True)  
            scaler.fit(X)        
            scaled_X = scaler.transform(X)
            self.clustering_scaler = scaler
            
            if self.type_clust == 'kmeans':
            
                # do kmeans + one-hot encoding
                kmeans = KMeans(n_clusters=self.n_clusters, 
                                **kwargs)
                kmeans.fit(scaled_X)
                X_kmeans = kmeans.predict(scaled_X)
                self.clustering_obj = kmeans
                
                return mo.one_hot_encode(X_kmeans, self.n_clusters)
            
            if self.type_clust == 'gmm':
                
                gmm = GaussianMixture(n_components=self.n_clusters, 
                                      **kwargs)
                gmm.fit(scaled_X)
                X_gmm = gmm.predict(scaled_X)
                self.clustering_obj = gmm
                
                return mo.one_hot_encode(X_gmm, self.n_clusters) 
            
        else: # if predict == True, encode test set
            
            X_clustered = self.clustering_obj.predict(self.clustering_scaler.transform(X))
            
            return mo.one_hot_encode(X_clustered, self.n_clusters)
                        
        
    def create_layer(self, scaled_X, W=None):        
        """ Create hidden layer. """
        
        n_features = scaled_X.shape[1]
        
        if self.bias != True: # no bias term in the hidden layer
            
            if (W is None):
            
                if self.nodes_sim == 'sobol':
                    self.W = ns.generate_sobol(n_dims=n_features, 
                                           n_points=self.n_hidden_features)
                
                if self.nodes_sim == 'hammersley':
                    self.W = ns.generate_hammersley(n_dims=n_features, 
                                           n_points=self.n_hidden_features)
                    
                if self.nodes_sim == 'uniform':
                    self.W = ns.generate_uniform(n_dims=n_features, 
                                              n_points=self.n_hidden_features, 
                                              seed = self.seed)
                
                if self.nodes_sim == 'halton':
                    self.W = ns.generate_halton(n_dims=n_features, 
                                             n_points=self.n_hidden_features)
                
                return self.activation_func(np.dot(scaled_X, self.W))
        
            else:
            
                #self.W = W
                return self.activation_func(np.dot(scaled_X, W))    
        
        else: # with bias term in the hidden layer
            
            if (W is None):
            
                n_features_1 = n_features + 1 
                
                if self.nodes_sim == 'sobol':
                    self.W = ns.generate_sobol(n_dims=n_features_1, 
                                           n_points=self.n_hidden_features)
                
                if self.nodes_sim == 'hammersley':
                    self.W = ns.generate_hammersley(n_dims=n_features_1, 
                                           n_points=self.n_hidden_features)
                    
                if self.nodes_sim == 'uniform':
                    self.W = ns.generate_uniform(n_dims=n_features_1, 
                                              n_points=self.n_hidden_features, 
                                              seed = self.seed)
                
                if self.nodes_sim == 'halton':
                    self.W = ns.generate_halton(n_dims=n_features_1, 
                                             n_points=self.n_hidden_features)
            
                return self.activation_func(np.dot(mo.cbind(np.ones(scaled_X.shape[0]), 
                                                                   scaled_X), 
                                                   self.W))
        
            else:
            
                #self.W = W
                return self.activation_func(np.dot(mo.cbind(np.ones(scaled_X.shape[0]), 
                                                                   scaled_X), 
                                                   W))
        
        
    def preproc_training_set(self, y=None, X=None, W=None): 
        """ Create new data for training set, with hidden layer, center the response. """ 
        
        # either X and y are stored or not 
        #assert ((y is None) & (X is None)) | ((y is not None) & (X is not None))

        if self.n_hidden_features > 0: # has a hidden layer           
            nn_scaler = StandardScaler(copy=True, 
                                        with_mean=True, 
                                        with_std=True)
            
        scaler = StandardScaler(copy=True, 
                                    with_mean=True, 
                                    with_std=True)  
            
        # center y
        if (y is None):
            y_mean = self.y.mean()
            centered_y = self.y - y_mean
        else:
            y_mean = y.mean()
            self.y_mean = y_mean
            centered_y = y - y_mean
            
        if (X is None):
            input_X = self.X
        else:
            input_X = X
        
        
        if (self.n_clusters <= 0): # data without any clustering: self.n_clusters is None -----      
            
            if self.n_hidden_features > 0: # with hidden layer          
                
                nn_scaler.fit(input_X)
                scaled_X = nn_scaler.transform(input_X)
                self.nn_scaler = nn_scaler
            
                if (W is None):
                    Phi_X = self.create_layer(scaled_X)
                else:
                    Phi_X = self.create_layer(scaled_X, W=W) # beware: if there is a bias and W is provided
                
                Z = mo.cbind(input_X, Phi_X)
                scaler.fit(Z)
                self.scaler = scaler 
                
            else: # no hidden layer
                
                Z = input_X
                scaler.fit(Z)
                self.scaler = scaler 
        
        else: # data with clustering: self.n_clusters is not None -----  
            
            augmented_X = mo.cbind(input_X, self.encode_clusters(input_X))
            
            if self.n_hidden_features > 0: # with hidden layer          
                
                nn_scaler.fit(augmented_X)
                scaled_X = nn_scaler.transform(augmented_X)           
                self.nn_scaler = nn_scaler
            
                if (W is None):
                    Phi_X = self.create_layer(scaled_X)
                else:
                    Phi_X = self.create_layer(scaled_X, W=W)
                
                Z = mo.cbind(augmented_X, Phi_X)
                scaler.fit(Z)
                self.scaler = scaler 
            
            else: # no hidden layer
                
                Z = augmented_X
                scaler.fit(Z)
                self.scaler = scaler 

        return centered_y, self.scaler.transform(Z) 
    
    
    def preproc_test_set(self, X):
        """ Transform data from test set, with hidden layer. """
        
        if self.n_clusters <= 0: # data without clustering: self.n_clusters is None -----      
            
            if self.n_hidden_features > 0: # if hidden layer
                
                scaled_X = self.nn_scaler.transform(X)
                Phi_X = self.create_layer(scaled_X, self.W)
               
                return self.scaler.transform(mo.cbind(X, Phi_X))
            
            else: # if no hidden layer
                
                return self.scaler.transform(X)
        
        else: # data with clustering: self.n_clusters is None -----      
            
            predicted_clusters = self.encode_clusters(X = X, predict = True)
            augmented_X = mo.cbind(X, predicted_clusters)
                
            if self.n_hidden_features > 0: # if hidden layer
                
                scaled_X = self.nn_scaler.transform(augmented_X)    
                Phi_X = self.create_layer(scaled_X, self.W)
                
                return self.scaler.transform(mo.cbind(augmented_X, Phi_X))
            
            else: # if no hidden layer
                
                return self.scaler.transform(augmented_X)
            
    
#if __name__ == '__main__':
##
    from sklearn import datasets   
##    
#    # Example 1 -----
#    
    n_features = 5
    n_samples = 100
    X, y = datasets.make_regression(n_features=n_features, 
                       n_samples=n_samples, 
                       random_state=0)

#    fit_obj = Base(n_hidden_features=3, 
#                 activation_name='relu', 
#                 n_clusters=2)
#    
#    centered_y, scaled_Z = fit_obj.preproc_training_set(y=y, X=X)
#
#    print(centered_y.shape)
#    print(scaled_Z.shape)
#    print(centered_y.mean())
#    print(scaled_Z.mean(axis = 0))
#    print(np.sqrt(scaled_Z.var(axis = 0)))
#    
#    fit_obj.fit(X, y) 
#    print(fit_obj.beta)
#    print(len(fit_obj.beta))
#    print(fit_obj.predict(X))
#    
 
#    # Example 2 -----
    
    diabetes = datasets.load_diabetes()
#    
#    # data snippet
#    diabetes.feature_names
#    
#    # shape 
#    diabetes.data.shape
#    diabetes.target.shape
#    
#    # define X and y
    X = diabetes.data 
    y = diabetes.target
    
#    fit_obj = rvflBase(n_hidden_features=3, 
#                       activation_name='relu', 
#                       n_clusters=2)
#    
#    centered_y, scaled_Z = fit_obj.preproc_training_set(y=y, X=X)
#
#    print(centered_y.shape)
#    print(scaled_Z.shape)
#    print(centered_y.mean())
#    print(scaled_Z.mean(axis = 0))
#    print(np.sqrt(scaled_Z.var(axis = 0)))
#    
#    fit_obj.fit(X, y)    
#    z = fit_obj.predict(X) - y
#    print(fit_obj.predict(X))
#    print(y)
#    print(z.mean())
#
