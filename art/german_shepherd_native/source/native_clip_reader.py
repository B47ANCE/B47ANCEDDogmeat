"""Read installed native animation tracks locally; never export clip data."""
import re
from mathutils import Quaternion,Vector

def close(text,start):
 depth=1;index=start
 while depth:
  if text[index]=='{':depth+=1
  elif text[index]=='}':depth-=1
  index+=1
 return index-1

def tracks(path):
 text=path.read_text(encoding='utf-8-sig');result={}
 for match in re.finditer(r'\bAnimation\s*\{\s*\{\s*(\w+)\s*\}',text):
  block=text[match.end():close(text,text.index('{',match.start())+1)];channels={}
  for key in re.finditer(r'AnimationKey\s+\w+\s*\{\s*(\d+);\s*\d+;([^}]+)\}',block):
   channels[int(key[1])]=[(int(k[1]),[float(x) for x in k[3].split(',')]) for k in re.finditer(r'(\d+);(\d+);([^;]+);;',key[2])]
  result[match[1]]=channels
 return result

def sample(keys,time,quaternion=False):
 lower=keys[0];upper=keys[-1]
 for k in keys:
  if k[0]<=time:lower=k
  if k[0]>=time:upper=k;break
 t=(time-lower[0])/(upper[0]-lower[0]) if upper[0]!=lower[0] else 0
 if quaternion:return Quaternion(lower[1]).conjugated().slerp(Quaternion(upper[1]).conjugated(),t)
 return Vector(lower[1]).lerp(Vector(upper[1]),t)
