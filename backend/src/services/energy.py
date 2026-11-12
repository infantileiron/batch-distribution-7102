import math,numpy as np
from src.services.distances import samples,pairwise

def energy(a,b):
 a,b=samples(a,b);n,m=len(a),len(b);d=pairwise(np.vstack([a,b]));return score(d,list(range(n)),list(range(n,n+m)))

def score(distance,ia,ib):
 n,m=len(ia),len(ib);aa=math.fsum(distance[np.ix_(ia,ia)].flat)/(n*n);bb=math.fsum(distance[np.ix_(ib,ib)].flat)/(m*m);ab=math.fsum(distance[np.ix_(ia,ib)].flat)/(n*m)
 return 2*ab-(aa+bb)
