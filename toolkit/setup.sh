#!/bin/bash
# Idempotent setup for the Prep'Up reels routine in a fresh cloud container.
# Re-creates: the built site, the render work dir (server, renderer, compositions), the ACE-Step 1.5 music model.
# usage: bash /home/user/media/toolkit/setup.sh        (safe to run every time; skips what already exists)
set -e
MEDIA=/home/user/media
SITE=/home/user/rayenhassine007/prep-up
WORK=$SITE/brag-output/work
ACE=/home/user/ace15

# 1. site build (the videos film the real built site)
cd $SITE
git pull -q --ff-only || true
[ -d node_modules ] || npm ci --silent
npm run build --silent > /dev/null 2>&1
CSS=$(basename "$(ls $SITE/dist/assets/ui-*.css | head -1)")
echo "site built, css=$CSS"

# 2. render work dir: server + renderer + compositions from the toolkit (CSS hash rewritten to the current build)
mkdir -p $WORK/comp
cp $MEDIA/toolkit/serve.cjs $MEDIA/toolkit/render.cjs $MEDIA/toolkit/shoot-slides.cjs $WORK/
for f in $MEDIA/toolkit/comp/*.html; do
  n=$(basename "$f" .html); mkdir -p $WORK/comp/$n; cp "$f" $WORK/comp/$n/index.html
done
for d in $MEDIA/toolkit/comp/*/; do cp -r "$d" $WORK/comp/; done
sed -i -E "s#/assets/ui-[A-Za-z0-9_-]+\.css#/assets/$CSS#g" $WORK/comp/*/index.html
if ! curl -s -o /dev/null -m 3 http://localhost:4180/; then cd $WORK && setsid nohup node serve.cjs > serve.log 2>&1 < /dev/null & disown; fi
sleep 1
curl -s -o /dev/null -w "server %{http_code}\n" http://localhost:4180/

# 3. music model (ACE-Step 1.5, MIT): code, CPU venv, weights (DiT turbo + VAE + text encoder, ~6 GB)
[ -d $ACE ] || git clone -q --depth 1 https://github.com/ace-step/ACE-Step-1.5.git $ACE
if [ ! -x $ACE/.venv/bin/python ]; then
  python3 -m venv $ACE/.venv
  $ACE/.venv/bin/pip -q install --index-url https://download.pytorch.org/whl/cpu torch torchaudio
  $ACE/.venv/bin/pip -q install "transformers>=4.51.0,<4.58.0" "diffusers>=0.37.0" einops "accelerate>=1.12.0" \
    soundfile loguru scipy numba vector-quantize-pytorch toml diskcache huggingface_hub matplotlib librosa
fi
if [ ! -f $ACE/checkpoints/acestep-v15-turbo/model.safetensors ]; then
  cd $ACE && .venv/bin/python -c "from huggingface_hub import snapshot_download; snapshot_download('ACE-Step/Ace-Step1.5', local_dir='checkpoints', allow_patterns=['config.json','acestep-v15-turbo/*','vae/*','Qwen3-Embedding-0.6B/*'])"
fi
echo "music model ready"
mkdir -p /home/user/media-work/music /home/user/media-work/samples
echo "setup done"
