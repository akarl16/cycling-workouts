---
name: align-workout-videos
description: Use when adding a Spotify playlist's songs as YouTube videos to a workout JSON's `videos` array, or re-syncing videos that drift out of time with the music. Triggers on "add the playlist/songs/videos to the workout", a Spotify playlist URL plus a workout, or "the videos are out of sync". Not for a single backdrop video (see VIDEOS.md).
---

# Align Playlist Videos to a Workout

The app plays each `videos[]` entry muted while Spotify plays the music, so the video for a song has to start when the song starts. Spotify **crossfades** (default **10s**, noted in Karl's worksheets), so a song starts earlier than the sum of the previous durations. Summing raw durations drifts a further ~10s per song: after 15 songs the videos are minutes off.

Two rules fix this:

1. **Subtract crossfade per transition.** Song *n* starts at `Σ (duration[k] − crossfade)` for k < n.
2. **Pin to interval starts.** A video with no `triggerOffset` restarts in sync every time its interval begins, so error cannot accumulate. Use `triggerOffset` only when no interval boundary is within ~15s of the song start (long steady intervals).

Never place songs from raw summed durations with mid-interval offsets everywhere. That is the failure this skill exists to prevent.

## Process

Run from the repo root.

### 1. Get the tracks with durations

Build a `tracks.json` in playlist order: `[{"name","videoId","duration"}]` (`duration` in seconds).

- **Playlist and durations:** `curl -A "Mozilla/5.0" https://open.spotify.com/embed/playlist/<ID>` and read `props.pageProps.state.data.entity.trackList` from the `__NEXT_DATA__` script. Each item has `title`, `subtitle` (artists) and `duration` in **ms**. The normal `open.spotify.com/playlist/` page only returns a title, so use the embed URL.
- **YouTube IDs:** scrape `https://www.youtube.com/results?search_query=<artist+title>` and take the first `videoRenderer.videoId`. Show the user the title picked for each. Bare titles ("Kingdom", "Let It Rock") may be the wrong version or a cover, so flag them.
- Strip `(feat. …)` from names. The artists are in the YouTube title.

### 2. Dry-run the schedule

```bash
python3 .claude/skills/align-workout-videos/align_videos.py workouts/60min/<file>.json tracks.json
```

Options: `--crossfade 10` (default), `--snap 15`, `--min-tail 30`. It prints the planned start, the actual (pinned) start, the mode (`pin` or `+Ns`) and the trigger per song, plus tracks dropped for lack of room. Check that `actual` is within a few seconds of `planned` for every song. A large gap means the song straddles a long interval, so look at it.

### 3. Write and validate

```bash
python3 .claude/skills/align-workout-videos/align_videos.py <workout> tracks.json --write [--replace]
python3 utils/validate_workout.py <workout>
```

`--replace` is needed when the workout already has `videos`. Validation only checks the schema, **not the sync**. Say so in your report; do not call the result "in sync" until Karl has ridden it or scrubbed it.

### 4. Report

State the crossfade used, how many songs fit and which were dropped, and which links are uncertain matches. If the playlist is longer than the workout, the tail songs are dropped; with crossfade the last song usually fits fully.

## Conventions the script follows (see VIDEOS.md)

- Block intervals use the fully expanded ID `{intervalId}-block-{blockId}-rep-{n}`. A bare `foo-1` only matches rep 1.
- Adjacent videos hand off with `endIntervalId` = the interval **before** the next trigger. Only when the next song starts mid-interval do they share it: the previous `endOffset` equals the next `triggerOffset`.
- `startTime` stays 0 (each video is the song from its start). `audioSource` stays the default so Spotify carries the music.
- Edits are textual so the rest of the file's formatting is untouched. It expects top-level `"videos"` before `"sequence"`.

## Other crossfade values

Default is 10s. If the user's worksheet or message says otherwise, pass `--crossfade`. Ask if there is no worksheet and the user hasn't said.
