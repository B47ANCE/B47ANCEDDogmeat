"""Decode the supplied original GLB base color into PZ's PNG container, no edits."""
from pathlib import Path
import hashlib,io,json,struct
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
source=ROOT/'art/german_shepherd_selected/original/selected_shepherd.glb'
raw=source.read_bytes();size=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+size]);binary=raw[28+size:]
primitive=doc['meshes'][0]['primitives'][0];material=doc['materials'][primitive['material']]
texture=doc['textures'][material['pbrMetallicRoughness']['baseColorTexture']['index']]
view=doc['bufferViews'][doc['images'][texture['source']]['bufferView']];offset=view.get('byteOffset',0)
encoded=binary[offset:offset+view['byteLength']];original=Image.open(io.BytesIO(encoded)).convert('RGB')
target=ROOT/'art/german_shepherd_native/textures/B47Dogmeat_GSD_Original.png';target.parent.mkdir(exist_ok=True)
original.save(target)
assert original.tobytes()==Image.open(target).convert('RGB').tobytes()
record={'source':'art/german_shepherd_selected/original/selected_shepherd.glb','source_sha256':hashlib.sha256(raw).hexdigest(),
 'embedded_base_color_sha256':hashlib.sha256(encoded).hexdigest(),'operation':'JPEG decode to PNG only; no resize, repaint, flip, color adjustment or UV edit',
 'decoded_rgb_pixel_sha256':hashlib.sha256(original.tobytes()).hexdigest(),'png_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'size':list(original.size),'pixel_parity':True}
(target.parent.parent/'validation/original-diffuse.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Original GLB diffuse pixels preserved in PNG')
