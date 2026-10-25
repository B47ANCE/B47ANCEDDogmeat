"""Arrange actual Blender renders for review; never alter the model or textures."""
from pathlib import Path
from PIL import Image, ImageDraw

OUT=Path(__file__).resolve().parents[1]/'previews'

def sheet(files,labels,columns,title):
    width=320;height=344;rows=(len(files)+columns-1)//columns
    result=Image.new('RGB',(width*columns,height*rows+32),'#20242a')
    draw=ImageDraw.Draw(result);draw.text((12,10),title,fill='white')
    for i,(file,label) in enumerate(zip(files,labels)):
        x=i%columns*width;y=i//columns*height+32
        with Image.open(file) as frame:result.paste(frame.convert('RGB').resize((width,320)),(x,y))
        draw.text((x+10,y+325),label,fill='white')
    return result

for coat in ('Coat1','Coat2'):
    for kind,start,seconds in [('Walk',0,1.2),('Run',8,.7)]:
        files=[OUT/f'B47Dogmeat_GSD_{coat}_{i:02}_{kind}.png' for i in range(start,start+8)]
        result=sheet(files,[f'{kind}: {i}/8 cycle' for i in range(8)],4,f'{coat} / {kind} / Blender offline')
        result.save(OUT/f'{coat}_{kind.lower()}_review.jpg',quality=90)
        if coat=='Coat1':result.save(OUT/f'{kind.lower()}_review.jpg',quality=90)
        frames=[Image.open(p).convert('RGB').resize((480,480)) for p in files]
        frames[0].save(OUT/f'{coat}_{kind.lower()}.gif',save_all=True,append_images=frames[1:],duration=round(seconds*1000/8),loop=0)
    states=['LieDown','Lie','GetUp','Death','Dead']
    files=[OUT/f'B47Dogmeat_GSD_{coat}_{21+i:02}_{kind}.png' for i,kind in enumerate(states)]
    result=sheet(files,states,3,f'{coat} / Rest and death / Blender offline')
    result.save(OUT/f'{coat}_rest_review.jpg',quality=90)
    if coat=='Coat1':result.save(OUT/'rest_review.jpg',quality=90)
files=[];labels=[]
for coat in ('Coat1','Coat2'):
    for i,h in [(16,0),(18,50),(20,100)]:
        files.append(OUT/f'B47Dogmeat_GSD_{coat}_{i:02}_Idle.png');labels.append(f'{coat}: {h}% health')
result=sheet(files,labels,3,'Tail health / Actual Blender renders / PZ runtime NOT TESTED')
result.save(OUT/'tail_health_comparison.png');result.save(OUT/'health_review.jpg',quality=90)
files=[OUT/f'B47Dogmeat_GSD_{coat}_{i:02}_Idle.png' for coat in ('Coat1','Coat2') for i in range(26,30)]
sheet(files,[f'{coat}: {h}% health' for coat in ('Coat1','Coat2') for h in (12.5,37.5,62.5,87.5)],4,'Between health anchors / Native steady-state blend emulation').save(OUT/'health_blend_review.jpg',quality=90)
print('Review sheets and gait GIFs refreshed from 60 actual Blender renders')
