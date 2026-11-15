# Puts a generated track under a silent video whose cuts sit on a 120 BPM grid (beat = 0.5 s from t = 0).
# Finds the track's beats, picks a downbeat after the intro as the start, so video t=0 and every cut land on beats.
# usage: python fit_music.py <music.wav> <silent.mp4> <out.mp4> [bpm=120]
import sys, subprocess, numpy as np, librosa

wav, vid, out = sys.argv[1:4]
bpm = float(sys.argv[4]) if len(sys.argv) > 4 else 120.0
beat = 60.0 / bpm
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', vid]))

y, sr = librosa.load(wav, sr=22050, mono=True)
onset = librosa.onset.onset_strength(y=y, sr=sr)
tempo, beats = librosa.beat.beat_track(onset_envelope=onset, sr=sr, start_bpm=bpm, tightness=400, units='time')
# phase of the beat grid (circular mean of beat times mod one beat)
ang = 2 * np.pi * (np.asarray(beats) % beat) / beat
phase = (np.angle(np.mean(np.exp(1j * ang))) % (2 * np.pi)) / (2 * np.pi) * beat
# downbeat: of the 4 positions in a bar, the one with the strongest low-end onsets
S = np.abs(librosa.stft(y, n_fft=2048, hop_length=512))
low = librosa.onset.onset_strength(S=librosa.amplitude_to_db(S[:40]), sr=sr)
times = librosa.times_like(low, sr=sr, hop_length=512)
def strength(t):
    return float(np.interp(t, times, low))
total = len(y) / sr
grid = np.arange(phase, total, beat)
score = [np.mean([strength(t) for t in grid[k::4]]) for k in range(4)]
k0 = int(np.argmax(score))
downbeats = grid[k0::4]
# start on a downbeat after the intro (>= 2 s), leaving room for the whole video
cands = [t for t in downbeats if t >= 2.0 and t + dur <= total - 0.2] or [t for t in downbeats if t + dur <= total] or [0.0]
start = float(cands[0])
print(f'tempo {float(np.atleast_1d(tempo)[0]):.1f}  phase {phase:.3f}  start {start:.3f}  dur {dur:.2f}  track {total:.1f}')
af = f'atrim=start={start:.4f}:duration={dur:.4f},asetpts=PTS-STARTPTS,afade=t=out:st={dur - 0.6:.3f}:d=0.6,loudnorm=I=-14:TP=-1.0:LRA=11'
subprocess.check_call(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', wav, '-filter_complex', f'[1:a]{af}[a]', '-map', '0:v', '-map', '[a]',
                       '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', out])
print('saved', out)
