# StandUp Reminder

A tiny desktop reminder that tells you to **STAND UP** after sitting too long,
then to **SIT DOWN** after a short standing break — so you regularly take pressure
off your lower back.

When the timer fires, a funny message appears as **big words floating over your
screen**. Click the words (or press `Esc`) to confirm you moved — that closes it
and starts the next timer.

It runs on **any computer that has Python**. It uses **only the Python standard
library**, so there is **nothing extra to install** — which means it also works
on locked-down work / Citrix / HIPAA computers that allow Python but block
package installs.

---

## ⚡ Easiest install (Windows)

1. Click the green **`Code`** button on this page → **Download ZIP**, then unzip it
   (or clone — see below).
2. Open the folder and **double-click `setup.bat`**.

That's it. It puts a **"StandUp Reminder" icon on your Desktop** and starts the
app. From then on, just **double-click the Desktop icon** to run it.

### One-line install (if you have Git)

```
git clone https://github.com/johntsunami/StandUpReminder.git
StandUpReminder\setup.bat
```

### Requirements

- **Python 3.7 or newer.** On Windows, get it from
  [python.org/downloads](https://www.python.org/downloads/) and **tick
  "Add Python to PATH"** during install. Nothing else is needed.

---

## How to use it

A small window opens with three tabs:

- **Home** — current state + **Pause / Start**, **Reset**, **Skip** buttons.
- **Timer** — a live `mm:ss` countdown and progress bar, so you can confirm the
  timer is running (and see when it's paused).
- **Settings** — all the options below, right inside the window (no separate popup).

There's also a **Quotes** menu for managing your quote lists.

**When a popup appears:**

| Action | Result |
|--------|--------|
| Click the words, or press `Esc` (also `Space`/`Enter`) | Confirms you moved, closes it, starts the next timer |
| Right-click, or press `D` | Skips that quote and shows a different one |

Only **one popup is ever on screen at a time**, and the timer **pauses while a
popup is showing** — so nothing piles up if you step away from your desk.

### Settings (menu → Settings)

- **Sit time** before STAND UP (default **45 min**)
- **Stand time** before SIT DOWN (default **5 min**)
- **Start timer this long after launch** (default **30 min**) — a grace period
  after you turn the computer on before the cycle begins.
- **Pause when locked / screen asleep** (default ON) — the timer holds while your
  workstation is locked, the screen is asleep, or you've been away from the
  keyboard for a couple of minutes, so a break never counts while you're not there.
- **Pause during calls** (default ON) — the timer holds whenever your microphone
  or camera is in use (Teams, Zoom, etc.), so it won't tell you to move mid-meeting.
- **Restart cycle if away/locked over (min)** (default **30**) — if your screen was
  locked or asleep for at least this long, the timer **restarts when you log back
  in** and the **next popup is STAND UP** (since you were probably already up and
  moving while away). Counts time the PC spent fully asleep too.
- **Sound** on/off, **popup transparency**, keep the control window on top.
- **Start automatically at login** — **ON by default** (per-user, no admin rights
  needed). Uncheck it here if you ever want to disable it on a particular machine.
- **Test popup** buttons — press them to preview STAND UP / SIT DOWN as many
  times as you like, without affecting your real timer.

The small control window and the Settings window open in the **lower-right corner**
of the screen.

### Quotes (menu → Quotes)

Separate lists for STAND UP and SIT DOWN. You can **add**, **delete**,
**import** (a `.txt` file with one quote per line, or a `.json` list),
**export**, or **restore the built-in defaults**. There are 100+ quotes to start.

---

## Put the Desktop icon on another computer

On each new computer, after downloading the files, run once:

```
python install.py
```

This drops the **"StandUp Reminder"** icon on that machine's Desktop. (It tries
the native Windows method first, then PowerShell, then a plain `.bat` launcher —
so it still works on restricted machines.) `setup.bat` does this for you
automatically.

---

## Where your settings are stored

In your home folder, so they survive updates:

```
~/.standup_reminder/config.json
~/.standup_reminder/stand_quotes.json
~/.standup_reminder/sit_quotes.json
```

---

## Updating it later (and handing off to Claude)

Want to change something — more quotes, different look, new feature? Open this
project in **Claude Code** and read **[CLAUDE.md](CLAUDE.md)**: it's a full map of
the project written so Claude (or anyone) can pick it up and make changes safely.

To publish your changes back to GitHub, from inside the project folder:

```
git add .
git commit -m "describe what changed"
git push
```

On any other computer, get the latest version with:

```
git pull
```

---

## What's in this repo

| File | What it is |
|------|-----------|
| `standup.py` | The app (standard library only) |
| `setup.bat` | One-click installer: makes the Desktop icon and launches the app |
| `install.py` | Creates the Desktop shortcut (used by `setup.bat`) |
| `make_icon.py` | Generates `standup.ico` with no extra libraries |
| `standup.ico` | The app/Desktop icon |
| `run.bat` | Launches the app with no console window |
| `CLAUDE.md` | Project handoff doc for Claude / developers |

## License

MIT
