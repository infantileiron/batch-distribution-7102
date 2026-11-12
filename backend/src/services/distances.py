import numpy as np

def samples(a,b):
 a=np.asarray(a,dtype=np.float64);b=np.asarray(b,dtype=np.float64)
 if a.ndim!=2 or b.ndim!=2 or a.shape[1]!=b.shape[1] or a.shape[1]<1 or len(a)<2 or len(b)<2:raise ValueError('two groups need >=2 equal-dimensional samples')
 if not np.isfinite(a).all() or not np.isfinite(b).all():raise ValueError('samples must be finite')
 return a,b

def pairwise(points):
 differences=points[:,None,:]-points[None,:,:];squared=np.sum(differences*differences,axis=2,dtype=np.float64)
 if not np.isfinite(squared).all():raise ValueError('pairwise distance overflow')
 return np.sqrt(squared)
