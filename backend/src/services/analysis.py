import hashlib,json,statistics
from src.services.permutation import permutation_test

def analyze(snapshot):
 data=snapshot['dataset'];policy=snapshot['policy'];a=[[r[k] for k in ('l','a','b')] for r in data['batch_a']];b=[[r[k] for k in ('l','a','b')] for r in data['batch_b']]
 result=permutation_test(a,b,policy['permutations'],policy['seed'],policy['scaling'],policy['bandwidth'],policy['sigma'])
 summaries=[]
 for label,rows in (('A',a),('B',b)):
  summaries.append({'batch':label,'n':len(rows),'mean':[statistics.fmean(x[j] for x in rows) for j in range(3)],'population_sd':[statistics.pstdev(x[j] for x in rows) for j in range(3)]})
 return {**result,'raw_a':data['batch_a'],'raw_b':data['batch_b'],'summaries':summaries,'policy':policy,'checksum':hashlib.sha256(json.dumps(snapshot,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),'assumptions':['Energy V使用欧氏距离，组内均值包含对角；MMD U使用RBF核，组内排对角并按n(n-1)归一，原始U值可为负，不截0。','缩放仅在合并样本上估计总体均值/SD；自动sigma为合并样本全部非对角欧氏距离中位数，包含零距离，仅估计一次。固定sigma也在置换前锁定。','合并样本SD=0维显式以scale=1保留，中心化后为0；pooled median=0则自动核宽失败，须改明确固定正sigma，不静默加epsilon或跳过零值。','两个统计共享同一seed排列，每次保持两批样本数；p=(1+置换统计>=观测数的次数)/(B+1)。原始统计、全部排列索引和两条置换分布保留。','独立、可交换样本假设；成对、时序或同缸相关读数可能不适用。两个检验的p未作多重校正，分别复核，不合成为自动迁移结论。','p不是迁移概率，有限随机置换有分辨率与Monte Carlo变动；模拟L*a*b*分布变化不是颜色质量或工艺因果判定。']}
