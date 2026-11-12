import math,re

def validate_dataset(batch_a,batch_b):
 seen=set()
 for label,rows in (('A',batch_a),('B',batch_b)):
  if not 4<=len(rows)<=120:raise ValueError('每批须4至120条独立模拟读数')
  for row in rows:
   key=row['sample_id']
   if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,30}',key) or key in seen:raise ValueError('样本ID须跨两批唯一且为英数短ID')
   seen.add(key)
   if not all(math.isfinite(row[k]) for k in ('l','a','b')):raise ValueError('L*a*b*须有限，不能填补缺读数')
 return True
