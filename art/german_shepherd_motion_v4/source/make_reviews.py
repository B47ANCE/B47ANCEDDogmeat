"""Assemble actual Blender frames into review loops; no model/image generation."""
from pathlib import Path
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;OUT=HERE.parent/'previews'

def main():
    # Assemble only frames rendered from this checkpoint.
    for kind,start,seconds in [('Walk',0,1.2),('Run',24,.7),('Look',72,3)]:
        frames=[Image.open(OUT/f'B47Dogmeat_GSD_Coat2_{start+i:02}_{kind}.png').convert('RGB') for i in range(24)]
        milliseconds=round(seconds*1000);boundaries=[round(i*milliseconds/24/10)*10 for i in range(25)]
        durations=[b-a for a,b in zip(boundaries,boundaries[1:])]
        frames[0].save(OUT/(kind.lower()+'.gif'),save_all=True,append_images=frames[1:],duration=durations,loop=0,optimize=False)
    down=[Image.open(OUT/f'B47Dogmeat_GSD_Coat2_{48+i:02}_LieDown.png').convert('RGB') for i in range(9)]
    up=[Image.open(OUT/f'B47Dogmeat_GSD_Coat2_{96+i:02}_GetUp.png').convert('RGB') for i in range(9)]
    frames=down+[down[-1]]*4+up+[up[-1]]*4
    frames[0].save(OUT/'rest-review.gif',save_all=True,append_images=frames[1:],duration=160,loop=0,optimize=False)
    sheet=Image.new('RGB',(1200,330),'#202124');draw=ImageDraw.Draw(sheet)
    for i,(index,label) in enumerate([(57,'Low health'),(61,'Half health'),(65,'Full health')]):
        frame=Image.open(OUT/f'B47Dogmeat_GSD_Coat2_{index:02}_Idle.png').convert('RGB');frame.thumbnail((400,300))
        sheet.paste(frame,(i*400,30));draw.text((i*400+12,8),label,fill='white')
    sheet.save(OUT/'tail-health-review.png')
    print('Actual-frame head/rest loops and tail review assembled')

if __name__=='__main__':main()
