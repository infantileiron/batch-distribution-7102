import math,numpy as np
from src.services.distances import samples,pairwise

def kernel_matrix(distance,sigma):
 if not math.isfinite(sigma) or sigma<=0:raise ValueError('sigma must be finite and positive')
 # Ratio form avoids overflow in sigma**2 for valid large sigma.
 ratio=distance/sigma
 with np.errstate(over='ignore'):return np.exp(-.5*ratio*ratio)

def mmd(a,b,sigma):
 a,b=samples(a,b);n,m=len(a),len(b);kernel=kernel_matrix(pairwise(np.vstack([a,b])),sigma);return score(kernel,list(range(n)),list(range(n,n+m)))

def score(kernel,ia,ib):
 n,m=len(ia),len(ib);aa=(math.fsum(kernel[np.ix_(ia,ia)].flat)-n)/(n*(n-1));bb=(math.fsum(kernel[np.ix_(ib,ib)].flat)-m)/(m*(m-1));ab=math.fsum(kernel[np.ix_(ia,ib)].flat)/(n*m)
 return (aa+bb)-2*ab
