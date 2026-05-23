# Video Configuration Guide

Workouts support an optional `videos` array for interval-synced video playback in the CycleSync Coach app.

## Schema

```json
"videos": [
  {
    "id": "string (kebab-case)",
    "name": "string",
    "youtubeUrl": "https://www.youtube.com/watch?v=...",
    "startTime": 0,
    "triggerIntervalId": "i001",
    "endIntervalId": "i010"
  }
]
```

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique kebab-case identifier |
| `name` | No | Display name |
| `youtubeUrl` | No* | Full YouTube URL |
| `vimeoUrl` | No* | Full Vimeo URL |
| `startTime` | No | Seconds into the video to seek to on trigger (default: 0) — **ignored for playlist URLs** |
| `triggerIntervalId` | Yes | Interval ID that starts the video |
| `endIntervalId` | No | Interval ID where video stops (inclusive) |
| `audioSource` | No | `"spotify"` (default) keeps the video muted and lets Spotify play. `"video"` unmutes the video and pauses Spotify for the duration of this segment; Spotify resumes when the next non-`"video"` segment begins. YouTube only. |

> **Playlist URLs**: If `youtubeUrl` contains `&list=`, the app does not seek — YouTube manages track progression. `startTime` has no effect. A single entry spanning the whole workout works correctly; scrubbing does not reposition the playlist.

*One of `youtubeUrl` or `vimeoUrl` must be provided.

## Block Expansion

The app expands repeating blocks into a flat list of intervals before matching video IDs. A block with `id: "b001"` and intervals `["foo-1", "foo-2"]` running 3 repetitions expands to:

```
foo-1-block-b001-rep-1
foo-2-block-b001-rep-1
foo-1-block-b001-rep-2
foo-2-block-b001-rep-2
foo-1-block-b001-rep-3
foo-2-block-b001-rep-3
```

> **Important:** Block IDs (e.g. `b001`) are never in the expanded list and cannot be used as `triggerIntervalId` or `endIntervalId`.

## ID Matching Rules

The app matches interval IDs using a **prefix rule**:

- Exact match: `"i012"` matches only `"i012"`
- Prefix match: `"foo-1"` matches any expanded ID starting with `"foo-1-block-"`

This means `"triggerIntervalId": "foo-1"` will trigger at the **first** expanded interval that matches — i.e., rep 1 of the first matching block.

## Handoff Between Videos

When two videos are adjacent (video A ends where video B begins), use the **fully expanded ID** for `endIntervalId` to avoid overlap:

```
"endIntervalId": "{intervalId}-block-{blockId}-rep-{repNumber}"
```

Example — video ends at the last rep of block b001:
```json
"endIntervalId": "shift-mode-1-2-block-b001-rep-3"
```

The next video then triggers at the first interval after the block:
```json
"triggerIntervalId": "i012"
```

## Timing Calculation

To sync a specific video timestamp with a specific workout moment:

1. Sum all interval durations from the start of the workout up to **and including** the target moment → `workoutElapsedAtTarget`
2. Convert the video timestamp to seconds → `videoTimestamp`
3. Sum all interval durations from the trigger interval to the target moment → `elapsedFromTrigger`
4. `startTime = videoTimestamp - elapsedFromTrigger`

### Example

Goal: video timestamp `6:44:11` (= 24,251s) should align with the **end of i025**.

- i025 ends at 5,175s into the workout
- Trigger interval `shift-mode-6-1` starts at 3,600s
- Elapsed from trigger to end of i025: `5175 - 3600 = 1575s`
- `startTime = 24251 - 1575 = 22676`

```json
{
  "id": "video-ftp-prep",
  "name": "FTP Prep",
  "youtubeUrl": "https://www.youtube.com/watch?v=b6XqXXQjTJk",
  "startTime": 22676,
  "triggerIntervalId": "shift-mode-6-1",
  "endIntervalId": "i026"
}
```

## Full Example

```json
"videos": [
  {
    "id": "video-warmup",
    "name": "Warmup & Shift Block 1",
    "youtubeUrl": "https://www.youtube.com/watch?v=ZE-s56OP3rs",
    "startTime": 0,
    "triggerIntervalId": "i001",
    "endIntervalId": "shift-mode-1-2-block-b001-rep-3"
  },
  {
    "id": "video-shift-blocks",
    "name": "Shift Blocks 2–6",
    "youtubeUrl": "https://www.youtube.com/watch?v=yCUOxL4P3Cg",
    "startTime": 0,
    "triggerIntervalId": "i012",
    "endIntervalId": "i016"
  },
  {
    "id": "video-ftp-prep",
    "name": "FTP Prep",
    "youtubeUrl": "https://www.youtube.com/watch?v=b6XqXXQjTJk",
    "startTime": 22676,
    "triggerIntervalId": "shift-mode-6-1",
    "endIntervalId": "i026"
  }
]
```

## Audio Source

By default a workout video plays muted as a visual backdrop and Spotify carries the music. Set `"audioSource": "video"` on a `videos[]` entry to flip control during that segment: the video plays unmuted, and the app pauses Spotify until the next segment with `audioSource` of `"spotify"` (or no entry at all) takes over. Only Spotify pauses caused by this feature are auto-resumed — a manual user pause is respected.

```json
{
  "id": "video-luminous",
  "youtubeUrl": "https://www.youtube.com/watch?v=...",
  "startTime": 952,
  "triggerIntervalId": "i052",
  "endIntervalId": "i055",
  "audioSource": "video"
}
```

## Pre-class Intro Video

A separate top-level `introVideo` field plays an ambient video behind the workout-summary screen before the rider hits Start. It loops automatically and stops cleanly when the workout begins.

```json
{
  "id": "ride-with-walt-90",
  "name": "Ride with Walt (90)",
  "introVideo": {
    "name": "Walt Disney World pre-ride",
    "youtubeUrl": "https://www.youtube.com/watch?v=Z9nq1ym9h38",
    "startTime": 0,
    "audioSource": "video"
  },
  "videos": [ ... ],
  "sequence": [ ... ]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `name` | No | Display name |
| `youtubeUrl` | No* | Full YouTube URL |
| `vimeoUrl` | No* | Full Vimeo URL |
| `videoId` | No* | YouTube video ID (alternative to `youtubeUrl`) |
| `startTime` | No | Seconds into the video to start at (default: 0) |
| `audioSource` | No | `"spotify"` (default) plays the intro muted. `"video"` unmutes the intro and pauses Spotify until the rider hits Start. |

*One of `youtubeUrl`, `vimeoUrl`, or `videoId` must be provided.

The intro only renders on the true pre-class screen — workout loaded, never started. Pausing mid-workout does not re-show it.

## Limitations

- **PeacockTV / streaming services**: Cannot be embedded — DRM and `X-Frame-Options` headers block iframes. Only YouTube and Vimeo are supported.
- **`endIntervalId` is inclusive**: The video plays through the full duration of the named interval.
- **No seek on Vimeo**: Vimeo uses a hash fragment (`#t=Xs`) which may not work on all Vimeo embed configurations.
- **Restricted YouTube embeds**: Videos from production-style channels (with "playback on other websites" disabled, or with strict monetization/rights claims) may refuse to play. Test before relying on a video — the deployed HTTPS app accepts more videos than `http://localhost` does.
