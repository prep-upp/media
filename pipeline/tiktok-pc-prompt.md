Post the next Prep'Up TikTok posts (videos or photo slideshows) with a trending sound.

1. Open https://raw.githubusercontent.com/prep-upp/media/main/pipeline/state.json and read the "videos" list. Pick every entry whose "tiktok" object has "status": "to_post" and whose "slot_local" (Africa/Tunis time) is in the future. If there is none, stop and tell me "Nothing to post on TikTok".

2. For each of them, first open TikTok Studio (https://www.tiktok.com/tiktokstudio/content) in Chrome, where I am logged in as @prep__upp, and check the Posts and Scheduled lists. If a post whose caption starts with the same first line already exists, skip it: it is already done.

3. Download the media from https://raw.githubusercontent.com/prep-upp/media/main/ + the path, into a new folder in my Downloads:
   - if "tiktok"."type" is "photos": download every file in "tiktok"."images", in order (slide-01.jpg, slide-02.jpg, …);
   - otherwise: download the video at "tiktok"."file".

4. In TikTok Studio, click Upload and upload the media:
   - photos: select ALL the images at once, in order slide-01 to the last, so it becomes a photo post (slideshow). Check the order in the preview: slide-01 (the cover) must be first. If TikTok Studio on the web does not accept a photo post, do NOT post a video instead: stop and tell me.
   - video: upload the single video file.

5. Add a sound: open the Sounds panel.
   - If the "tiktok" object has a "sound" object (videos): the video's cuts are timed to the beat of that exact recording. Search for "sound"."search", and pick the ORIGINAL official sound by "sound"."artist" (not a sped-up, slowed, remix or cover version). Then set where the sound starts to exactly "sound"."start_at" (mm:ss into the song), using the sound's trim / start-point control, and set it to full volume (the video has no audio of its own). If you cannot find that exact sound, or cannot set the start point, do NOT pick another song: stop and tell me.
   - Otherwise (photo slideshows): look at the trending sounds and pick the one that best matches the "mood" (for example "chill study lofi"). Prefer a song that is clearly trending right now.

6. Paste the "tiktok"."caption" text exactly as written as the description.

7. Turn on "Schedule" and set the date and time to "slot_local" (Africa/Tunis time, convert to my computer's time zone if it differs).

8. The FIRST time you post a photo slideshow, and the first time you post a video, stop before the final Schedule button, show me a screenshot of the filled-in post (media, sound name and start point, caption, date and time) and wait for my "OK". For a video with a "sound" object, also ask me to play the preview and check the cuts land on the beat. After that, schedule directly.

9. At the end, tell me in one short message, in English: what you scheduled (video or photo slideshow, which one), which trending sound you chose, and for which date and time. If something failed (not logged in, upload error, no sound panel, photo posts not supported), tell me exactly what and do not post anything half-done.

Never change anything else on the account (profile, other posts, settings, messages).
