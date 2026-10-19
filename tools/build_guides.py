#!/usr/bin/env python3
"""Builds guides/*.html from the content below. The built pages are committed, so the
site needs no build step; run this again after editing a guide:  python3 tools/build_guides.py"""
import html
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "guides"


def webp_size(path):
    """Width/height of a WebP file (VP8, VP8L or VP8X), without Pillow."""
    b = path.read_bytes()[:40]
    fmt = b[12:16]
    if fmt == b"VP8 ":
        w, h = struct.unpack("<HH", b[26:30])
        return w & 0x3FFF, h & 0x3FFF
    if fmt == b"VP8L":
        bits = int.from_bytes(b[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if fmt == b"VP8X":
        return int.from_bytes(b[24:27], "little") + 1, int.from_bytes(b[27:30], "little") + 1
    raise ValueError(path)


def btn(name, alt, inline=False):
    p = ROOT / "img/buttons" / f"{name}.webp"
    w, h = webp_size(p)
    w, h = w // 2, h // 2  # crops are about 2x density: show them at their on-phone size
    cls = "btnimg inline" if inline else "btnimg"
    return (f'<img class="{cls}" src="../img/buttons/{name}.webp" width="{w}" height="{h}" '
            f'loading="lazy" alt="{html.escape(alt)}">')


def btns(*pairs):
    return '<span class="btnrow">' + "".join(btn(n, a, True) for n, a in pairs) + "</span>"


def screen(name, alt, caption=""):
    p = ROOT / "img/screens" / f"{name}.webp"
    w, h = webp_size(p)
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    return (f'<figure><img class="phone" src="../img/screens/{name}.webp" width="{w}" height="{h}" '
            f'loading="lazy" alt="{html.escape(alt)}">{cap}</figure>')


# ---------------------------------------------------------------- content
# Each page: (file, title, lede, colour, [guides]); each guide: (id, title, intro, screen_html, [steps], tip)
PAGES = []

PAGES.append(("playing.html", "Playing", "Everything on the Play screen. Every key here fires the moment your finger touches it, and nothing you need mid-song is behind a menu.", "var(--orange)", [
    ("play", "Play a song", "From a cold start to drums in under 30 seconds.",
     screen("play-stopped", "Play screen, stopped, with Harbor Lights loaded and a big PLAY key at the bottom.", "Stopped: PLAY waits at the bottom"),
     [
         "Open DrumFill2. On first launch the featured groove is already loaded. To pick a song, tap the <strong>library key</strong> (top left), then tap a song's name." + btn("library-key", "Library key: a square icon at the top left of the Play screen"),
         "Tap <strong>▶ PLAY</strong>. You hear a 1-bar count-in (spoken “one, two, three, four” by default), then the drums." + btn("play", "The wide PLAY key"),
         "While it plays, the display shows the section, the bar, four beat lights and the arrangement strip with a moving playhead.",
         "Tap <strong>■ STOP</strong> to stop at once. There is no confirmation." + btn("stop", "The red STOP key"),
     ], "After your first STOP the app asks to allow notifications: say yes, so the lock-screen controls work."),
    ("follow", "Follow chart or Follow me", "One switch decides who moves between sections: the chart, or you.",
     screen("play-followme-waiting", "Follow me: the intro reads BAR 3 of 1 and waiting for NEXT; NEXT glows blue and the FILL pad glows white.", "Follow me: it waits for you"),
     [
         "Find the switch under the song title. <strong>FOLLOW CHART</strong> is the default." + btn("follow-switch", "Follow chart / Follow me switch with Follow chart selected"),
         "<strong>Follow chart</strong>: tap PLAY and don't touch anything. Sections change by their bar counts, end fills and crashes happen by themselves, and the song stops on its ending.",
         "<strong>Follow me</strong>: tap the right half. Each section keeps looping (the display counts on: “BAR 9 of 8”) until you tap <strong>NEXT</strong>. When a section has run its length, NEXT glows blue and FILL gets hotter, as a reminder." + btn("follow-me-on", "The switch with Follow me selected") + btn("next-armed", "NEXT key with a blue glow, armed"),
         "You can switch mid-song; it takes effect at the next bar. The app remembers your choice for that song.",
     ], "Default for new songs: Settings → Play screen → New songs start in."),
    ("fill", "FILL and BIG FILL", "Fills that land where they should, every time.",
     screen("play-followme-fill", "Play screen with the FILL pad lit blue in the A section, labelled big fill (loud).", "FILL tells you what it will play"),
     [
         "Tap <strong>FILL</strong> any time. The fill starts at the same position inside the bar, so it always lands on the next downbeat. Tap too late in the bar (under an eighth note left) and it waits for the next bar." + btn("fill", "The large FILL pad, lit orange, labelled small fill"),
         "Mid-section FILL plays a small fill; in the last bar of a section it plays a big one. Its label tells you which. Loud intensity makes fills bigger.",
         "<strong>BIG</strong> always plays a 1–2 bar fill with toms and a crash." + btn("big", "The BIG pad, 1–2 bars"),
         "Fills rotate, so you never hear the same one twice in a row.",
     ], "In Follow chart the end fill before each section plays by itself; you only tap FILL when you want an extra one."),
    ("sections", "NEXT, PREV and jumping around", "Move through the song; changes always wait for the bar line.",
     screen("play-chart-chorus", "Play screen in the chorus; NEXT reads NEXT, A.", "NEXT shows where you are going"),
     [
         "<strong>NEXT</strong> moves to the upcoming section (its name is on the key) at the next bar line, with that section's end fill and crash." + btn("next", "The NEXT key labelled NEXT, A"),
         "<strong>PREV</strong> goes back one section." + btn("prev", "The PREV key"),
         "Tap any block in the arrangement strip to jump there; while playing, the jump is queued to the next bar line." + btn("strip", "The arrangement strip in the display with section blocks A, B, CHORUS"),
         "While stopped, tap a block to set the start point: it highlights and PLAY starts from there. Tap it again to clear it.",
     ], ""),
    ("extend", "+2 BARS: stretch a section", "The band took one more round. Keep going without breaking the form.",
     "",
     [
         "Tap <strong>+2 BARS</strong> to add two bars to the current section, this time through only. Tap again to add more." + btn("plus2", "The +2 BARS key"),
         "In Follow chart this, plus LOOP, is usually all you need mid-song.",
     ], "Want to stay in a section indefinitely? Use LOOP (see Practice)."),
    ("end", "END and endings", "Finish like a drummer, not like a loop that ran out.",
     screen("editor-ending", "Song Editor Ending tab: Fixed, Ring-out, a Ritard switch and the ending pattern.", "Ending styles in the Song Editor"),
     [
         "Tap <strong>END</strong>: the song goes to its outro at the next bar line, plays the ending and stops by itself." + btn("end", "The END key"),
         "Choose the ending style in the Song Editor's <strong>Ending</strong> tab: <strong>Fixed</strong> (play the ending, stop), <strong>Ring-out</strong> (a cymbal/tom roll until you tap END again; Follow chart cuts it after a few bars) or switch on <strong>Ritard</strong> to slow into the final hit." + btn("editor-tabs", "Song Editor tabs: Sections, Arrangement, Ending, Text"),
         "Need silence now? <strong>■ STOP</strong> cuts immediately." + btn("stop", "The red STOP key"),
     ], ""),
    ("intensity", "Quiet · Normal · Loud", "Live dynamics with one tap, applied on the next beat.",
     "",
     [
         "Tap <strong>QUIET</strong>, <strong>NORMAL</strong> or <strong>LOUD</strong>." + btn("intensity", "Intensity switch: Quiet, Normal, Loud with Normal lit"),
         "Quiet plays softer, drops ghost notes and crashes, and closes the hi-hat. Loud hits harder, opens up the hats or moves to the ride, adds crashes and makes fills bigger. Many grooves have hand-written quiet and loud versions.",
         "Each section has its own default (choruses louder, breakdowns quieter); your choice holds until you change it or stop.",
     ], ""),
    ("tempo", "Tempo, TAP and CRASH", "Set the tempo by ear, by number or by tapping.",
     screen("play-save-tempo", "Stopped Play screen with the banner Tempo 117 (song is 112), Save to song, Just this time.", "The save-tempo banner"),
     [
         "<strong>− / +</strong> change the tempo; tap the BPM number in the display to type one." + btn("tempo", "Tempo minus and plus keys"),
         "<strong>TAP</strong>: tap it in time a few times to set the tempo." + btn("tap", "The TAP key"),
         "<strong>CRASH</strong> adds a crash accent right now." + btn("crash", "The CRASH key"),
         "If you changed the tempo, STOP shows a banner: <strong>Save to song</strong>, <strong>Save to setlist</strong> (in a set) or <strong>Just this time</strong>. It never interrupts playback." + btn("save-tempo", "Banner: Tempo 117 (song is 112), Save to song, Just this time"),
     ], ""),
    ("practice", "Practice: LOOP, TRAIN, DROP", "Drill the hard part, speed it up, and check your own time.",
     screen("play-practice", "Play screen with LOOP and TRAIN +5 lit; the display says looping, pass 2.", "Looping the chorus with the trainer"),
     [
         "Tap the section you want in the strip (it's queued to the bar line), then tap <strong>LOOP</strong>: it repeats until you tap LOOP again." + btn("loop", "LOOP key with its light on"),
         "Tap <strong>TRAIN</strong> to raise the tempo every few passes (default +5 BPM every 2 passes). The small ⚙ on the key opens its settings: step, passes and a cap." + btn("train", "TRAIN +5 key with its light on"),
         "<strong>DROP</strong> cuts the drums for random bars so you can test your own time; its ⚙ sets how often. A setting can keep the click going in the gaps." + btn("drop", "The DROP key"),
     ], "When you stop, save the faster tempo to the song with the banner, or keep it just this time."),
    ("click", "Drums | Click, count-ins and the click", "A metronome that knows the song form.",
     screen("click-settings", "Click & count-in settings: count-in off, 1 bar or 2 bars, voice count-in, accent on beat 1, click sounds.", "Settings → Click & count-in"),
     [
         "Flip the header switch to <strong>CLICK</strong> for click only: no drums, but sections, count-ins, cues and tempo changes all stay." + btn("drums-click", "Drums / Click switch with Drums selected"),
         "Open <strong>Settings → Click &amp; count-in</strong> for count-in length (off, 1 or 2 bars), the spoken count-in, accent on beat 1, the click sound (beep, woodblock, cowbell, side stick, hi-hat or a voice) and subdivisions." + btn("click-row", "Settings row: Click & count-in"),
     ], ""),
    ("arrange", "Quick arrange", "Change the form while it plays.",
     screen("play-arrange", "Play screen with the arrange panel: CHORUS 8 bars and A 8 bars, each with minus, plus, x2 and DEL keys.", "ARR: edits apply live"),
     [
         "Tap <strong>ARR</strong>. The display turns into arrangement blocks." + btn("arr", "The ARR key with its light on"),
         "Each block has <strong>− / +</strong> (bars), <strong>×2</strong> (duplicate) and <strong>DEL</strong>. Changes to upcoming sections apply while the song plays." + btn("arrange-panel", "Arrange panel with minus, plus, x2 and DEL keys under each block"),
         "Tap <strong>ARR</strong> again to finish.",
     ], ""),
    ("band", "Band view", "Point the phone at the band: a giant, high-contrast count they can read from across the stage.",
     screen("band-view", "Band view in landscape: a huge 3, CHORUS, 5 bars left, NEXT Bridge.", "Band view"),
     [
         "Tap the <strong>eye key</strong> at the top of Play. The screen goes landscape and full screen." + btn("band-key", "The eye-shaped Band view key"),
         "It shows the beat number (the downbeat flashes the section colour), the section, bars left, the next section and countdowns like “STOP IN 2 BARS”. Flashes are shifted by the measured output delay, so they match what the band hears.",
         "<strong>FILL</strong>, <strong>NEXT</strong> and <strong>STOP</strong> stay along the bottom; <strong>×</strong> goes back." + btn("band-bar", "Band view bottom bar: FILL, NEXT, STOP and close"),
     ], ""),
    ("stagelock", "Stage lock", "No accidental trips into menus mid-song.",
     screen("play-gig-playing", "Play screen with stage lock on: the lock key is lit and a note says hold the lock for 1 s to unlock.", "Stage lock on"),
     [
         "Tap the <strong>lock key</strong> (top right). The library key, the switches and the practice row disappear; every performance key still works." + btn("lock-key", "The lock key, off") + btn("lock-key-on", "The lock key, on (lit blue)"),
         "To unlock, <strong>hold</strong> the lock key for one second.",
     ], "Gig mode turns stage lock on for you."),
    ("background", "Screen-off and background playback", "Pocket the phone; the drummer keeps going.",
     "",
     [
         "Start a song with <strong>▶ PLAY</strong>, then lock the phone or switch apps. Playback continues with a notification." + btn("play", "The PLAY key"),
         "The notification and lock screen have <strong>Play</strong>, <strong>Stop</strong> and <strong>Fill</strong>.",
         "Unplugging wired headphones or a phone call stops playback cleanly (it doesn't restart by itself).",
     ], "The Play screen keeps the display awake while playing; Settings → Play screen can turn that off."),
]))

PAGES.append(("songs.html", "Songs and patterns", "Find a song, build one in seconds, type one, or edit every bar of it.", "var(--teal)", [
    ("library", "The Library", "19 demo songs to start with, plus everything you make.",
     screen("library", "Library: Build a song, Type a chart, Beatbox and Patterns keys, a search box, genre chips and the song list.", "Library"),
     [
         "On Play, tap the <strong>library key</strong>; the tab bar then reaches Library, Setlists, Kits and Settings." + btn("library-key", "Library key"),
         "Filter by genre chips or search. Tap a song's name to open it on Play.",
         "The <strong>•••</strong> key on a song: Play, Edit song, Edit as text, Duplicate, Add to favorites, Add to setlist, Share, Export audio, Delete (with undo)." + btn("song-more", "The ••• key on a song row"),
     ], ""),
    ("builder", "Song Builder", "Genre + form → a complete, playable song.",
     screen("builder-result", "Built song: Intro, A, Chorus, Solo and Outro, each named groove with reroll and swap keys.", "A built song"),
     [
         "Library → <strong>Build a song</strong>." + btn("lib-build", "Build a song key"),
         "Pick a <strong>genre</strong> and a <strong>form</strong> (Pop, Rock, AABA, 12-bar blues, Folk, Build/drop, Jam), and a tempo, then <strong>BUILD SONG</strong>." + btn("build-song", "BUILD SONG key"),
         "For any section: <strong>🎲</strong> rerolls it; <strong>⇄</strong> opens the pattern browser already filtered to the song's genre, feel and tempo." + btn("reroll-swap", "Reroll (dice) and swap (arrows) keys"),
         "<strong>REROLL ALL</strong> starts over; <strong>SAVE &amp; PLAY</strong> keeps it and opens it on Play." + btns(("reroll-all", "REROLL ALL key"), ("save-play", "SAVE & PLAY key")),
     ], "At the bottom of Song Builder, Build by beatboxing makes a song from your voice: see the Beatbox guides."),
    ("quickchart", "Quick Chart", "Type a song the way musicians write charts on a napkin.",
     screen("chart-error", "Quick chart with the hint X4 isn't a section, did you mean S4 (solo)? and a Use S4 button.", "Live checking with fixes"),
     [
         "Library → <strong>Type a chart</strong> (or a song's ••• → Edit as text)." + btn("lib-chart", "Type a chart key"),
         "Type the tempo, meter, genre and sections, e.g. <code>@120 4/4 rock I2 V8 C8 V8 C8 O2</code>. Section letters: <code>I</code> intro, <code>V</code>/<code>A</code> verse, <code>P</code>/<code>B</code> pre-chorus, <code>C</code> chorus, <code>Br</code> bridge, <code>S</code> solo, <code>Bk</code> breakdown, <code>O</code> outro; the number is bars.",
         "Extras: <code>(V8 C8)x2</code> repeats, <code>[2/4]</code> an odd bar, <code>Br8:3/4</code> another meter, <code>C8@+10</code> or <code>Br8@half</code> tempo changes, <code>C8{stop 8.1}</code> cues, <code>V8'</code> a variation, <code>O2~</code> ring-out, <code>\"vocals in\"</code> a cue note. The shortcut keys type them for you." + btn("chart-keys", "Quick chart shortcut keys: I, V, P, C, Br, O, 4, 8, prime, x2, brackets, braces, at, tilde, quote"),
         "Mistakes are underlined with a plain-English fix; tap it to apply." + btn("chart-fix", "Use S4 fix key"),
         "<strong>SAVE &amp; PLAY</strong>. Grooves are picked for the genre, so it plays right away." + btn("chart-save", "SAVE & PLAY key"),
     ], "Commas, new lines and lowercase are fine, so you can paste a chart from a message."),
    ("editor", "Song Editor", "Every detail of a song, in four tabs.",
     screen("editor-sections", "Song Editor Sections tab: Intro, A Verse, B Pre-chorus, Chorus, Bridge, Outro with audition keys.", "Sections tab"),
     [
         "A song's <strong>•••</strong> → <strong>Edit song</strong>." + btn("song-more", "The ••• key"),
         "<strong>Sections</strong>: each section's groove, fills, end fill, intensity, cue note, meter and tempo. Edit the Chorus once and every Chorus changes. ▶ auditions it." + btn("editor-tabs", "Tabs: Sections, Arrangement, Ending, Text"),
         "<strong>Arrangement</strong>: drag steps to reorder, − / + bars, tap a step to duplicate, remove, add a note or cues, or insert odd bars.",
         "<strong>Ending</strong>: fixed, ring-out or ritard. <strong>Text</strong>: the whole song as a Quick Chart.",
         "Tap <strong>SAVE</strong>; ▶ opens it on Play." + btn("editor-save", "SAVE and play keys"),
     ], ""),
    ("cues", "Cues: stops, hits and tacets", "The band stop on beat 3 of the last chorus bar? Write it in.",
     screen("editor-cue", "Add cue: pick bar 1–8, beat 1–4 and subdivision, then Stop, Hit, Hit + Stop or Resume.", "Adding a cue"),
     [
         "Song Editor → <strong>Arrangement</strong> → tap a step, then <strong>Add cue</strong>." + btn("add-cue", "Add cue key"),
         "Choose the bar and beat, then <strong>Stop</strong> (drums cut), <strong>Hit</strong> (kick + crash, groove continues), <strong>Hit + Stop</strong>, <strong>Resume</strong> (with a fill, sticks or nothing) or <strong>Tacet</strong> (no drums for some bars while time keeps running).",
         "<strong>ADD CUE</strong>, then SAVE. On Play the block shows a small marker and “STOP on 1” flashes one bar early." + btn("add-cue-confirm", "ADD CUE key"),
     ], ""),
    ("patterns", "Pattern Browser", "300 original patterns: 200 grooves, 50 fills, 25 intros, 25 endings.",
     screen("patterns", "Patterns: the featured Gospel Chops card, search, kind and filter chips, and pattern cards with step previews.", "The browser"),
     [
         "Library → <strong>Patterns</strong>." + btn("lib-patterns", "Patterns key"),
         "Filter by kind, genre, feel, meter and “fits” the current tempo; the sliders key adds tempo, complexity, energy and sort." + btn("pattern-filters", "Filter chips: Grooves, Fills, Intros, Endings, Genre, Feel, Meter, Fits 112"),
         "Tap a card to hear it loop at your tempo with your kit; tap again to stop. Long-press for a favourite. Use “Similar” to find neighbours.",
     ], ""),
    ("pattern-editor", "Pattern Editor", "Make your own groove on a step grid.",
     screen("pattern-editor", "Pattern editor with hits on crash, closed hat, snare and kick, and the velocity panel for the crash.", "Step grid with velocity"),
     [
         "Patterns → <strong>+</strong>." + btn("pattern-new", "New pattern + key"),
         "Choose 16, 32 or triplet steps. Tap a cell to add a hit, tap again to remove it; long-press for velocity (ghost, normal, accent). <strong>+ Row</strong> adds instruments.",
         "<strong>Tap-record</strong> lets you play it in instead." + btn("tap-record", "Tap-record key"),
         "▶ loops it; ✓ saves it. Use it in any song section." + btn("pattern-tools", "Audition play key and save tick key"),
     ], ""),
    ("share", "Share songs, import MIDI, export audio", "Get the whole band on the same chart.",
     screen("song-menu", "Song menu: Play, Edit song, Edit as text, Duplicate, Add to favorites, Add to setlist, Share, Export audio, Delete.", "The song menu"),
     [
         "A song's <strong>•••</strong> → <strong>Share</strong> sends a <code>.pdsong</code> file through any app (email, chat, Drive, Nearby Share). A setlist's share key sends a <code>.pdset</code> with all its songs." + btn("song-more", "The ••• key"),
         "Whoever opens it sees a preview and taps <strong>Import</strong>. Missing kits fall back to Studio. Set your name in Settings → Your name so they see who made it.",
         "Library's <strong>↑</strong> key imports a General MIDI drum file or a shared song." + btn("lib-import", "Library import key (up arrow)"),
         "••• → <strong>Export audio</strong> renders the song to a WAV file.",
     ], ""),
]))

PAGES.append(("live.html", "Live", "Setlists, gig mode, pedals and headset buttons for the stage.", "var(--blue)", [
    ("setlists", "Setlists and segues", "Run a whole set, with songs flowing into each other.",
     screen("setlist", "Setlist Friday at the Harbor with 4 songs: Segue with a 2-bar ramp, Click through, Stop, Stop.", "A setlist"),
     [
         "<strong>Setlists</strong> tab → <strong>New setlist</strong>, give it a name." + btn("new-setlist", "NEW SETLIST key"),
         "<strong>ADD SONGS</strong>, tick them, Add. Drag the handles to reorder." + btn("add-songs", "ADD SONGS key"),
         "Each song's <strong>•••</strong> sets what happens after it: <strong>Stop</strong>, <strong>Segue</strong> (next song starts on the downbeat after the ending; tempo change instant or over 1–4 bars) or <strong>Click through</strong> (the click keeps time at the next song's tempo until you press PLAY). You can also set a tempo for this set only." + btn("after-more", "The ••• key on a setlist song") + btn("after-choice", "Stop, Segue, Click through choice"),
         "<strong>PLAY SET</strong>. Between songs the big <strong>NEXT SONG</strong> key loads the next one with one tap." + btn("play-set", "PLAY SET key") + btn("next-song", "NEXT SONG key: Backroad Two-Step, 150"),
     ], ""),
    ("gig", "Gig mode", "A pre-show checklist, then a locked stage screen.",
     screen("gig-checklist", "Gig mode checklist: Do Not Disturb on, battery, output test, screen, setlist loaded; START GIG.", "The checklist"),
     [
         "Open the setlist and tap <strong>🎤 GIG MODE</strong>." + btn("gig-mode", "GIG MODE key"),
         "Work down the list: <strong>Do Not Disturb</strong> (allow access once; it is restored after the gig), <strong>battery</strong> (warns under 40%), <strong>output</strong> (▶ plays a 2-second test hit with a level meter; Bluetooth gets a warning), <strong>screen</strong> (stays awake, brightness locked, stage lock) and <strong>setlist</strong> (all songs and kits loaded).",
         "<strong>START GIG</strong> opens Play on song 1 with stage lock on. (<strong>START ANYWAY</strong> appears if something isn't green; <strong>FIX LATER</strong> leaves.)" + btn("start-gig", "START GIG key"),
         "After the show, back on the setlist, <strong>END GIG</strong> puts Do Not Disturb and brightness back how they were." + btn("end-gig", "END GIG key"),
     ], ""),
    ("pedals", "Foot pedals", "Optional: the same actions as the on-screen keys, under your feet.",
     screen("pedal-4", "Pedal setup with 4 buttons: 1 PLAY/END, 2 FILL, 3 AUX, 4 NEXT/END, each with its learned key.", "A learned 4-button pedal"),
     [
         "Open <strong>Settings → Pedals &amp; inputs</strong>. (After a few songs, Play also suggests it once; SET UP goes to the same place.)" + btn("pedals-row", "Settings row: Pedals & inputs") + btn("pedal-hint", "Play screen hint: Got a foot pedal or page-turner? SET UP"),
         "Connect your pedal: Bluetooth MIDI, USB MIDI, or a page-turner that sends key presses (those work with no setup).",
         "Choose how many buttons it has: <strong>2</strong>, <strong>4</strong> or <strong>MORE</strong>." + btn("pedal-count", "Pedal buttons choice: 2, 4, MORE"),
         "Tap <strong>LEARN 4 BUTTONS</strong> (or a single row) and press each pedal button when asked." + btn("learn-4", "LEARN 4 BUTTONS key"),
         "The 4-button layout: <strong>1 PLAY / END</strong> (PLAY when stopped, END when playing) · <strong>2 FILL</strong> · <strong>3 AUX</strong> (+2 BARS; hold = STOP; double-tap = PREV; TAP tempo when stopped) · <strong>4 NEXT / END</strong> (tap = NEXT, hold = END). Two buttons: MAIN (tap FILL, hold NEXT, double-tap END, PLAY when stopped) and AUX.",
         "Check the <strong>On the Play screen</strong> preview (numbered badges show which button does what) and the <strong>Live test</strong>.",
     ], "Turned the pedal off and on? It reconnects by itself within seconds."),
    ("headset", "Headset button and volume keys", "No pedal? Your earbuds have a button.",
     screen("pedal-preview", "Pedal setup preview of the Play screen with numbered badges on PLAY, FILL, +2 BARS, NEXT, END and STOP.", "Which button does what"),
     [
         "In <strong>Settings → Pedals &amp; inputs</strong>, the headset section maps the play/pause button of wired or Bluetooth headphones: PLAY when stopped and, while playing, FILL (or NEXT or +2 BARS, your choice). It works with the screen locked." + btn("pedals-row", "Settings row: Pedals & inputs"),
         "Optional on Android: map the <strong>volume keys</strong> (up = main, down = aux) while Play is open. Off by default.",
     ], ""),
]))

PAGES.append(("sounds.html", "Sounds", "Seven kits built in, plus your own kits and Freesound sounds.", "var(--green)", [
    ("kits", "The seven built-in kits", "Five sampled acoustic kits recorded from real drums, and two generated electronic kits.",
     screen("kits", "Kits tab: Studio (public domain), Jazz Club, Vintage, Brushes (CC0), Heavy.", "Kits"),
     [
         "Open the <strong>Kits</strong> tab. <strong>Studio</strong> (the default), <strong>Jazz Club</strong>, <strong>Vintage</strong>, <strong>Brushes</strong> and <strong>Heavy</strong> are sampled with several velocity layers and round-robins; <strong>Vintage Machine</strong> and <strong>Lo-Fi</strong> are synthesised.",
         "Tap <strong>▶</strong> on a kit to hear it." + btn("kit-audition", "Kit audition play key"),
         "Change a song's kit in the Song Editor. Settings → Credits lists every kit's author and licence.",
     ], ""),
    ("import", "Import an SFZ or Hydrogen kit", "Bring your own multisampled kit.",
     screen("kit-import", "Import kit preview of GarageSketch.zip (SFZ): kick, snare, hats, tom and crash all mapped, each with a play key.", "Import preview"),
     [
         "Kits → <strong>↑</strong> (Import kit), then pick a Hydrogen <code>.h2drumkit</code> or a zipped SFZ kit." + btn("kit-import", "Import kit key (up arrow)"),
         "The preview shows the kit's name, licence and each detected instrument with ▶. Sounds it couldn't place are in a <em>Needs a slot</em> list: assign them.",
         "<strong>IMPORT KIT</strong>. The kit editor then lets you play and mix each slot, and shows an import report." + btn("import-kit-btn", "IMPORT KIT key"),
     ], "Imported kits are for your own use on your phone; songs you share refer to them by name only."),
    ("browse", "Browse free kits", "A public list of free kits, with licences up front.",
     screen("kits-browse", "Browse free kits: License and Has velocity layers filters and a kit with GPL and velocity layers badges.", "The free-kit list"),
     [
         "Kits → <strong>Browse free kits</strong>. Filter by licence and velocity layers." + btn("kit-tabs", "Kits tabs: Installed, Browse free kits, Get more sounds"),
         "Tap <strong>↓</strong> on a kit; it downloads in your browser. Then import the file with ↑ as above." + btn("kit-download", "Download key (down arrow)"),
     ], ""),
    ("freesound", "Freesound with your own key", "600,000+ free sounds. About two minutes to set up, and the key never leaves your phone.",
     screen("freesound-3", "Create a key step: Name, Description and Callback URL with copy buttons, and OPEN FREESOUND.ORG/APIV2/APPLY.", "Step 3: create a key"),
     [
         "Kits → <strong>Get more sounds</strong> → <strong>GET MORE SOUNDS</strong> → <strong>SET UP FREESOUND</strong>." + btn("more-sounds", "GET MORE SOUNDS key"),
         "<strong>CREATE FREESOUND ACCOUNT</strong>, or <strong>I ALREADY HAVE ONE</strong>." + btn("have-account", "I ALREADY HAVE ONE key"),
         "Open the key form; copy the three values the app shows into it." + btn("fs-apply", "OPEN FREESOUND.ORG/APIV2/APPLY key"),
         "Back in the app, <strong>Paste</strong> the key, then <strong>CHECK KEY</strong>. A green “Key works” means you're done." + btns(("fs-paste", "Paste key"), ("fs-check", "CHECK KEY key")),
         "Now search per kit slot (Snare suggests “snare one shot”), ▶ preview, and <strong>Use</strong> to fill the slot. CC0 only by default; switch on CC-BY if you like. Credits are written for you.",
     ], "Non-commercial sounds are never offered. Remove the key any time in Settings → Freesound."),
    ("audio", "Output presets, split output, Bluetooth", "Sound right on headphones, a phone speaker or a PA.",
     screen("audio", "Audio & output: presets Headphones, Phone speaker, Small BT, PA / amp; low-cut; EQ.", "Settings → Audio & output"),
     [
         "<strong>Settings → Audio &amp; output</strong>." + btn("audio-row", "Settings row: Audio & output"),
         "Pick a preset: <strong>Headphones</strong>, <strong>Phone speaker</strong>, <strong>Small BT</strong> or <strong>PA / amp</strong>. Then tweak low-cut, EQ and the gentle bus compressor. A limiter is always on to protect the PA." + btn("presets", "Output presets"),
         "<strong>Split: drums L · click R</strong> sends the click to one ear for in-ear monitoring." + btn("split", "Output mode: Stereo or Split drums L, click R"),
         "On a Bluetooth speaker the app warns once about delay; <strong>Bluetooth delay compensation</strong> lines up Band view and your taps.",
     ], ""),
]))

PAGES.append(("gear.html", "Gear", "MIDI out and multi-output interfaces, for players with more boxes than friends.", "var(--violet)", [
    ("midi-notes", "MIDI notes out", "Play an e-drum module, a synth or a plugin from DrumFill2's grooves.",
     screen("midi", "MIDI out: Sound source Internal, MIDI, Both; MIDI offset; General MIDI note map.", "Settings → MIDI"),
     [
         "<strong>Settings → MIDI</strong>." + btn("midi-row", "Settings row: MIDI"),
         "Under <strong>Send to</strong>, plug in a USB MIDI interface and tap <strong>Refresh</strong>, or <strong>Scan Bluetooth</strong> for a Bluetooth MIDI device, then pick it." + btn("midi-send", "Send to: Refresh and Scan Bluetooth keys"),
         "<strong>Sound source</strong>: Internal, MIDI (the phone's kit goes quiet) or Both." + btn("sound-source", "Sound source: Internal, MIDI, Both"),
         "Adjust <strong>MIDI offset</strong> until the module lines up with the phone. The note map (General MIDI by default, channel 10) can be changed per instrument; hi-hat openness can go out as CC4.",
     ], ""),
    ("midi-clock", "MIDI clock", "Loopers, delays and drum machines follow DrumFill2's tempo.",
     screen("midi-clock", "Send MIDI clock switch on, Status waiting for the device.", "Clock on"),
     [
         "In <strong>Settings → MIDI</strong>, pick the device and switch on <strong>Send MIDI clock</strong>." + btn("midi-clock", "Send MIDI clock switch"),
         "Clock follows the count-in, tempo changes and ritards; Start goes out on the song's first downbeat and Stop on STOP. The status line reports how it's going.",
     ], ""),
    ("outputs", "Multi-output audio interfaces", "Drums to the PA, click and count-ins to your in-ears.",
     screen("outputs", "Outputs: Separate outputs switch; Drums on 1/2, Click on 3/4, Cue voice on 3/4, each with a test tone key.", "Routing"),
     [
         "Connect a USB audio interface with more than two outputs. <strong>Settings → Audio &amp; output → Multi-output interface</strong>." + btn("multi-row", "Multi-output interface row"),
         "Switch on <strong>Separate outputs</strong>." + btn("separate", "Separate outputs switch"),
         "Route <strong>Drums</strong>, <strong>Click</strong> and <strong>Cue voice</strong> to 1/2, 3/4, 3, 4 or Off. ▶ plays a test tone on each." + btn("test-tone", "Test tone play key"),
         "If the phone only opens two channels on your interface, the page says so and DrumFill2 falls back to split mode instead of going silent.",
     ], "Support varies by phone; four-channel streams can have more latency than stereo."),
]))

PAGES.append(("beatbox.html", "Beatbox", "Turn the groove in your head into drums. Everything is analysed on the phone; nothing is uploaded.", "var(--pink)", [
    ("groove", "Beatbox a groove", "2 to 8 bars of “pm-ti-ta-ti” become a drum pattern.",
     screen("beatbox", "Record Beatbox: Click in headphones switch, length 2, 4 or 8 bars, RECORD key.", "Record Beatbox"),
     [
         "Library → <strong>Beatbox</strong>. Allow the microphone when asked." + btn("lib-beatbox", "Beatbox key"),
         "Put headphones on and switch on <strong>Click in headphones</strong> (without it, the tempo comes from your take). Pick 2, 4 or 8 bars.",
         "<strong>● RECORD</strong> and beatbox: “pm” for kick, “ta” for snare, “ti” for hi-hat. <strong>■ STOP</strong> when done." + btns(("record", "RECORD key"), ("stop-rec", "STOP key")),
         "Your hits appear on the step grid and play back with a real kit, with a “sounds like” match from the library. Fix any hit, then make a song from the groove.",
     ], "Get close to the mic. If it says “No beat heard”, try again a little louder."),
    ("teach", "Teach it your sounds", "Your snare sounds like someone else's hi-hat? Teach it.",
     screen("beatbox-teach", "Teach it your sounds: RECORD keys for Kick (try pm), Snare (ta), Closed hat (ti), Open hat (chi).", "5 examples each"),
     [
         "On Record Beatbox, tap <strong>Teach it your sounds</strong>." + btn("teach", "Teach it your sounds row"),
         "For Kick, Snare and Closed hat (Open hat is optional): <strong>● RECORD</strong> and make the sound 5 times, about once a second." + btn("teach-record", "RECORD key for one sound"),
         "Retake your groove. <strong>FORGET MY SOUNDS</strong> goes back to the general rules.",
     ], ""),
    ("song", "Beatbox Song Builder", "A whole song, one section at a time.",
     screen("beatbox-song-prompt", "Beatbox Song Builder: Intro, 2 bars, 1 of 6, 96 BPM locked, a section progress strip and the hint Count in or build up.", "One section at a time"),
     [
         "Library → <strong>Build a song</strong> → scroll down → <strong>Build by beatboxing</strong>." + btn("lib-build", "Build a song key"),
         "Choose a form (Pop, or your own section list), the tempo (<strong>Set it now</strong> or <strong>From my first take</strong>), the meter and the kit. <strong>START WITH THE INTRO</strong>." + btn("start-intro", "START WITH THE INTRO key"),
         "Each section shows a hint (“Count in or build up”, “keep it simple”, “bigger, more energy”…). <strong>● RECORD</strong>: count along, beatbox, and it stops by itself at the last bar. From the second section on you hear the last 2 bars of the previous one first, so you can play into it." + btn("bb-progress", "Section progress strip: Intro, A, B, Chorus, Bridge, Outro"),
         "Keep the take, retake it, edit it or swap in the closest library groove. Repeated sections reuse your take.",
         "On the finish screen, ▶ plays the whole song; tap any section to redo it, then save it to the Library. Progress saves after every kept take, so you can stop and resume.",
     ], ""),
]))

# ---------------------------------------------------------------- templates
HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · DrumFill2 guides</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#18191C">
<link rel="icon" href="../img/icon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@600;700&family=IBM+Plex+Sans:wght@400;600&family=Share+Tech+Mono&display=swap">
<link rel="stylesheet" href="../css/site.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top">
  <div class="wrap">
    <a class="brand" href="../" aria-label="DrumFill2 home"><img src="../img/icon.svg" width="30" height="30" alt="">DrumFill2</a>
    <nav class="nav" aria-label="Main">
{nav}
      <a class="dl" href="../#download">Download</a>
    </nav>
    <button class="theme-btn" type="button" aria-label="Switch theme"><svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 3a9 9 0 1 0 9 9 7 7 0 0 1-9-9z"/></svg></button>
  </div>
</header>
<main id="main">
"""
FOOT = """</main>
<footer>
  <div class="wrap">
    <nav aria-label="Footer"><a href="../">Home</a><a href="./">All guides</a><a href="../#download">Download</a><a href="../#faq">FAQ</a></nav>
    <p>DrumFill2 is an independent hobby project, not affiliated with any drum machine maker. Screenshots are from the app on an Android emulator; your phone may look slightly different.</p>
  </div>
</footer>
<script src="../js/site.js" defer></script>
</body>
</html>
"""


def nav(current):
    items = [("index.html", "All guides")] + [(f, t) for f, t, *_ in PAGES]
    out = []
    for f, t in items:
        href = "./" if f == "index.html" else f
        cur = ' aria-current="page"' if f == current else ""
        out.append(f'      <a href="{href}"{cur}>{t}</a>')
    return "\n".join(out)


def guide_html(g):
    gid, title, intro, shot, steps, tip = g
    steps_html = "\n".join(f"        <li>{s}</li>" for s in steps)
    tip_html = f'\n      <p class="note tip">{tip}</p>' if tip else ""
    landscape = ' landscape' if (not shot or 'band-view' in shot) else ''
    return f"""  <section class="guide" id="{gid}" aria-labelledby="{gid}-h">
    <h2 id="{gid}-h">{title}</h2>
    <p class="intro">{intro}</p>
    <div class="guide-body{landscape}">
      <div>
      <ol class="howto">
{steps_html}
      </ol>{tip_html}
      </div>
      {shot}
    </div>
  </section>
"""


def page(i, entry):
    f, title, lede, colour, guides = entry
    toc = "\n".join(f'      <li><a href="#{g[0]}">{g[1]}</a></li>' for g in guides)
    prev = PAGES[i - 1] if i > 0 else None
    nxt = PAGES[i + 1] if i + 1 < len(PAGES) else None
    pager = '<nav class="pager" aria-label="More guides">'
    pager += f'<a class="key ghost" href="{prev[0]}">← {prev[1]}</a>' if prev else '<a class="key ghost" href="./">← All guides</a>'
    pager += f'<a class="key ghost" href="{nxt[0]}">{nxt[1]} →</a>' if nxt else '<a class="key ghost" href="../#download">Download →</a>'
    pager += "</nav>"
    body = f"""<div class="wrap guide-hero" style="--c: {colour}">
  <p class="crumbs"><a href="../">Home</a> › <a href="./">Guides</a> › {title}</p>
  <h1>{title}</h1>
  <p>{lede}</p>
</div>
<div class="wrap guide-layout">
  <nav class="toc" aria-label="On this page">
    <p class="silk">On this page</p>
    <ol>
{toc}
    </ol>
  </nav>
  <div>
{"".join(guide_html(g) for g in guides)}  {pager}
  </div>
</div>
"""
    return HEAD.format(title=title, desc=html.escape(lede), nav=nav(f)) + body + FOOT


def index():
    cards = "\n".join(
        f'    <li><a href="{f}" style="--c: {c}"><b>{t}</b><span>{html.escape(l)}</span></a></li>'
        for f, t, l, c, _ in PAGES)
    body = f"""<div class="wrap guide-hero">
  <p class="crumbs"><a href="../">Home</a> › Guides</p>
  <h1>How-to guides</h1>
  <p>Step-by-step instructions with pictures of the exact keys to tap. New here? Start with <a href="playing.html#play">Play a song</a>, or <a href="../#download">install the app</a> first.</p>
</div>
<div class="wrap" style="padding-bottom:80px">
  <ul class="guide-cards">
{cards}
  </ul>
</div>
"""
    return HEAD.format(title="How-to guides", desc="Step-by-step DrumFill2 guides with pictures of the keys to tap.", nav=nav("index.html")) + body + FOOT


OUT.mkdir(exist_ok=True)
(OUT / "index.html").write_text(index())
for i, entry in enumerate(PAGES):
    (OUT / entry[0]).write_text(page(i, entry))
print("wrote", 1 + len(PAGES), "guide pages,", sum(len(p[4]) for p in PAGES), "guides")
