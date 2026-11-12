import math,random,numpy as np
from src.services.distances import samples,pairwise
from src.services.energy import score as energy_score
from src.services.mmd import score as mmd_score,kernel_matrix

def permutation_test(a,b,permutations=199,seed=2407,scaling='pooled_std',bandwidth='pooled_median',sigma=None):
 a,b=samples(a,b)
 if isinstance(permutations,bool) or not isinstance(permutations,int) or not 1<=permutations<=1999:raise ValueError('invalid permutation count')
 if isinstance(seed,bool) or not isinstance(seed,int) or seed<0:raise ValueError('invalid seed')
 pooled=np.vstack([a,b]);n,m=len(a),len(b);N=n+m;center=np.zeros(pooled.shape[1]);scales=np.ones(pooled.shape[1]);constant=[]
 if scaling=='pooled_std':
  center=np.mean(pooled,axis=0);sd=np.std(pooled,axis=0,ddof=0)
  if not np.isfinite(center).all() or not np.isfinite(sd).all():raise ValueError('pooled scaling overflow')
  constant=np.flatnonzero(sd==0).tolist();scales=np.where(sd==0,1.,sd);pooled=(pooled-center)/scales
 elif scaling!='none':raise ValueError('unknown scaling')
 distance=pairwise(pooled);median=float(np.median(distance[np.triu_indices(N,1)]))
 if bandwidth=='pooled_median':
  if median<=0 or not math.isfinite(median):raise ValueError('pooled median为0，自动核宽不可估；请选择明确正值的固定sigma，不跳过零距离')
  sigma=median
 elif bandwidth=='fixed':
  if sigma is None or not math.isfinite(sigma) or sigma<=0:raise ValueError('fixed sigma must be positive')
 else:raise ValueError('unknown bandwidth policy')
 kernel=kernel_matrix(distance,sigma);ia=list(range(n));ib=list(range(n,N));observed_energy=energy_score(distance,ia,ib);observed_mmd=mmd_score(kernel,ia,ib)
 rng=random.Random(seed);orders=[];energy_null=[];mmd_null=[]
 for _ in range(permutations):
  order=list(range(N));rng.shuffle(order);pa=sorted(order[:n]);pb=sorted(order[n:]);orders.append(order);energy_null.append(energy_score(distance,pa,pb));mmd_null.append(mmd_score(kernel,pa,pb))
 def result(observed,values):
  extreme=sum(value>=observed for value in values)
  return {'statistic':observed,'extreme_count':extreme,'denominator':permutations+1,'pvalue':(1+extreme)/(permutations+1),'permutation_statistics':values}
 return {'energy':result(observed_energy,energy_null),'mmd':result(observed_mmd,mmd_null),'B':permutations,'seed':seed,'permutations':orders,'sample_sizes':[n,m],'transform':{'scaling':scaling,'center':center.tolist(),'scales':scales.tolist(),'constant_dimensions':constant,'constant_dimension_policy':'pooled SD=0 dimensions centered to 0 with scale=1; explicitly retained','bandwidth':bandwidth,'sigma':float(sigma),'pooled_median_distance':median,'label_independent':True},'transformed_a':pooled[:n].tolist(),'transformed_b':pooled[n:].tolist(),'comparison':'>= observed; strict Float64 evaluation; +1 numerator and denominator','pvalues_adjusted':False}
