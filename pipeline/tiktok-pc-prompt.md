Post the next Prep'Up TikTok posts (videos or photo slideshows) with a trending sound.

1. Open https://raw.githubusercontent.com/prep-upp/media/main/pipeline/state.json and read the "videos" list. Pick every entry whose "tiktok" object has "status": "to_post" and whose "slot_local" (Africa/Tunis time) is in the future. If there is none, stop and tell me "Nothing to post on TikTok".

2. For each of them, first open TikTok Studio (https://www.tiktok.com/tiktokstudio/content) in Chrome, where I am logged in as @prep__upp, and check the Posts and Scheduled lists. If a post whose caption starts with the same first line already exists, skip it: it is already done.

3. Get the media from https://raw.githubusercontent.com/prep-upp/media/main/ + the path (upload it straight from that link if you cannot save to my Downloads):
   - if "tiktok"."type" is "photos": download every file in "tiktok"."images", in order (slide-01.jpg, slide-02.jpg, …);
   - otherwise: download the video at "tiktok"."file".

4. In TikTok Studio, click Upload and upload the media:
   - photos: select ALL the images at once, in order slide-01 to the last, so it becomes a photo post (slideshow). Check the order in the preview: slide-01 (the cover) must be first. If TikTok Studio on the web does not accept a photo post, do NOT post a video instead: stop and tell me.
   - video: upload the single video file.

5. Sound:
   - Video with an "audio" field: the video already has its own music. Do NOT add a TikTok sound; keep the original audio at full volume.
   - Video with a "sound" object: search for "sound"."search" and pick the ORIGINAL official sound by "sound"."artist" (not sped-up, slowed, remix or cover). Keep TikTok's default start of the clip, full volume (the video has no audio of its own). Do not try to align it: I do that by ear (see step 8). If that exact sound is not available, do NOT pick another song: stop and tell me.
   - Photo slideshow: look at the trending sounds and pick the one that best matches the "mood" (for example "chill study lofi"). Prefer a song that is clearly trending right now.

6. Paste the "tiktok"."caption" text exactly as written as the description.

7. Turn on "Schedule" and set the date and time to "slot_local" (Africa/Tunis time, convert to my computer's time zone if it differs).

8. Before the final Schedule button:
   - Video with a "sound" object: always STOP here and leave the upload page open in Chrome. Send me a push notification: "Places/<video name> is ready in TikTok Studio: drag the sound so the cuts hit the beat, then click Schedule." I align the sound by ear and click Schedule myself.
   - Photo slideshow: if @prep__upp already has at least one photo post in Posts or Scheduled, click Schedule directly. Otherwise (first slideshow) stop, leave the page open, and send me a push notification asking me to check it and click Schedule myself.
   - Video with an "audio" field: click Schedule.
   - Anything else: click Schedule.
   Only one post can be left open at a time: if you have to stop on one, finish the others first, and stop on that one last.

9. At the end, tell me in one short message, in English: what you scheduled (video or photo slideshow, which one), which trending sound you chose, and for which date and time. If something failed (not logged in, upload error, no sound panel, photo posts not supported), tell me exactly what and do not post anything half-done.

Never change anything else on the account (profile, other posts, settings, messages).
