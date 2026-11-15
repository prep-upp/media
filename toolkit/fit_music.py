# Puts a generated track under a silent video whose cuts sit on a 120 BPM grid (beat = 0.5 s from t = 0).
# Finds the track's beats, picks a downbeat after the intro as the start, so video t=0 and every cut land on beats.
# usage: python fit_music.py <music.wav> <silent.mp4> <out.mp4> [bpm=120]
import sys, subprocess, numpy as np, librosa

wav, vid, out = sys.argv[1:4]
bpm = float(sys.argv[4]) if len(sys.argv) > 4 else 120.0
beat = 60.0 / bpm
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', vid]))

y, sr = librosa.load(wav, sr=22050, mono=True)
# Downbeat phase: fold the low-band (kick/bass) onset envelope over one bar (4 beats at the known bpm)
# and take the strongest position. Robust to triplet patterns that fool beat trackers.
S = np.abs(librosa.stft(y, n_fft=2048, hop_length=512))
low = librosa.onset.onset_strength(S=librosa.amplitude_to_db(S[:40]), sr=sr)
hop = 512 / sr
bar = 4 * beat
total = len(y) / sr
cand = np.arange(0, bar, 0.005)
def fold(env, ph):
    ts = np.arange(ph, len(env) * hop, bar)
    return float(np.mean(np.interp(ts, np.arange(len(env)) * hop, env)))
score = [fold(low, ph) for ph in cand]
phase = float(cand[int(np.argmax(score))])
downbeats = np.arange(phase, total, bar)
tempo = bpm
# start on a downbeat after the intro (>= 2 s), leaving room for the whole video
cands = [t for t in downbeats if t >= 2.0 and t + dur <= total - 0.2] or [t for t in downbeats if t + dur <= total] or [0.0]
start = float(cands[0])
print(f'tempo {float(np.atleast_1d(tempo)[0]):.1f}  phase {phase:.3f}  start {start:.3f}  dur {dur:.2f}  track {total:.1f}')
af = f'atrim=start={start:.4f}:duration={dur:.4f},asetpts=PTS-STARTPTS,afade=t=out:st={dur - 0.6:.3f}:d=0.6,loudnorm=I=-14:TP=-1.0:LRA=11'
subprocess.check_call(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', wav, '-filter_complex', f'[1:a]{af}[a]', '-map', '0:v', '-map', '[a]',
                       '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', out])
print('saved', out)
