# Clean a phone scan: flatten uneven lighting and colour cast by dividing by a local paper estimate
# (max filter removes thin ink, blur smooths), then mild contrast and saturation.
import sys
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
small = im.resize((im.width // 4, im.height // 4))
bg = small.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(12)).resize(im.size, Image.BILINEAR)
a = np.asarray(im).astype(np.float32); b = np.asarray(bg).astype(np.float32) + 1
out = np.clip(a / b * 248.0, 0, 255).astype(np.uint8)
im = Image.fromarray(out)
im = ImageEnhance.Contrast(im).enhance(1.1); im = ImageEnhance.Color(im).enhance(1.25)
im.save(dst)
