# Generates original music with ACE-Step 1.5 (MIT, commercial use allowed) on CPU, DiT only (no LM).
# usage: python gen_music.py <out_dir> <name> <bpm> <key> <duration_s> <seed> "<caption>"
import sys, os, time
sys.path.insert(0, '/home/user/ace15')
os.chdir('/home/user/ace15')
from acestep.handler import AceStepHandler
from acestep.inference import GenerationParams, GenerationConfig, generate_music

out, name, bpm, key, dur, seed, caption = sys.argv[1:8]
h = AceStepHandler()
h.initialize_service(project_root='/home/user/ace15', config_path='acestep-v15-turbo', device='cpu')
p = GenerationParams(caption=caption, lyrics='[Instrumental]', instrumental=True, bpm=int(bpm), keyscale=key,
                     timesignature='4', duration=float(dur), inference_steps=8, shift=3.0, seed=int(seed),
                     thinking=False, use_cot_metas=False, use_cot_caption=False, use_cot_language=False)
c = GenerationConfig(batch_size=1, audio_format='wav', use_random_seed=False, seeds=[int(seed)])
# Free the DiT (about 10 GB in float32 on CPU) once its latents are ready, so the VAE decode fits in RAM.
import gc
_orig_decode = h._decode_generate_music_pred_latents
def _decode_after_freeing_dit(*a, **k):
    h.model = None
    gc.collect()
    return _orig_decode(*a, **k)
h._decode_generate_music_pred_latents = _decode_after_freeing_dit
t = time.time()
r = generate_music(h, None, p, c, save_dir=out)
print('time', round(time.time() - t), 's', r.success, r.error)
for a in r.audios:
    dst = os.path.join(out, name + '.wav'); os.replace(a['path'], dst); print('saved', dst)
