# Builds the two files the Prep'Up reels dashboard reads, from pipeline/state.json.
# usage: python3 toolkit/dashboard_files.py <out_dir>
import json, sys, os

s = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'pipeline', 'state.json')))
out = sys.argv[1]

videos = []
for v in s['videos']:
    music = v.get('music', {})
    videos.append({
        'video': v['nom'],
        'outil': v['tool'],
        'legende_debut': v['match'],
        'duree_s': v['duree_s'],
        'accroche': v['accroche'],
        'musique': f"{music.get('style', '')} · {music.get('key', '')}",
        'experience': v.get('experiment', ''),
        'fichier': v['file'],
    })

strategie = []
def add(kind, items):
    for i, text in enumerate(items):
        strategie.append({'id': f'{kind}-{i + 1}', 'type': kind, 'texte': text})
add('regle', s['strategy']['current'])
add('lecon', s['lessons'])
add('experience', s['strategy']['experiments_to_try'])
add('changement', s['strategy']['changelog'])

json.dump(videos, open(os.path.join(out, 'videos.json'), 'w'), ensure_ascii=False, indent=1)
json.dump(strategie, open(os.path.join(out, 'strategie.json'), 'w'), ensure_ascii=False, indent=1)
print(len(videos), 'videos,', len(strategie), 'strategy rows')
