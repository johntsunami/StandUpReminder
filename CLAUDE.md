# CLAUDE.md — handoff & developer guide

This file tells Claude Code (or any developer) everything needed to continue
working on **StandUp Reminder**. Read it first before changing anything.

## What this app is

A desktop reminder that alternates **STAND UP** and **SIT DOWN** prompts to help
the user (chronic lumbar/sacral back pain) take pressure off their spine during
desk work. When a phase timer ends, a popup shows a humorous line as big words
floating over the screen; closing the popup = the user confirming they moved, and
that click starts the next phase's countdown.

## NON-NEGOTIABLE constraints (do not break these)

1. **Standard library only. No `pip install`, ever.** The user runs this on a
   locked-down corporate / Citrix / HIPAA work laptop that allows Python scripts
   but may block package installs. Allowed modules: `tkinter`, `winsound`,
   `json`, `os`, `sys`, `random`, `platform`, `datetime`, `ctypes`, `zlib`,
   `struct`, `subprocess`. If you think you need a third-party package, find a
   stdlib way instead.
2. **Primary platform is Windows.** Degrade gracefully elsewhere (the code wraps
   Windows-only bits — `winsound`, `-transparentcolor`, COM, startup folder — in
   try/except), but Windows is what matters.
3. **Keep it simple to install.** A non-technical user must be able to
   double-click `setup.bat`. Don't add build steps.

## File map

| File | Purpose | Notes |
|------|---------|-------|
| `standup.py` | The whole app | Single file, `StandUpApp` class + `set_autostart()` + `main()` |
| `setup.bat` | One-click install + launch | Checks Python, runs `install.py`, starts app |
| `install.py` | Creates the Desktop shortcut | 3 fallback methods (ctypes COM → PowerShell → .bat) |
| `make_icon.py` | Generates `standup.ico` | Pure stdlib PNG (zlib) embedded in an .ico |
| `standup.ico` | App + shortcut icon | Regenerate by running `python make_icon.py` |
| `run.bat` | Launch with no console | `start "" pythonw standup.py` |
| `README.md` | User-facing docs | Keep beginner-friendly |

## How `standup.py` works

- **State:** `self.mode` is `"sit"` or `"stand"`; `self.remaining` is seconds left
  in the current posture; `self.running` enables the countdown; `self.popup_open`
  pauses it while a real popup is up; `self.active_popup` holds the one on-screen
  popup (real OR preview).
- **Timer loop:** `_tick()` reschedules itself every 1000 ms via
  `self.root.after`. It only decrements when
  `running and not popup_open and not _popup_alive()` — this is what guarantees
  the timer freezes while any popup is showing, so nothing stacks up if the user
  steps away.
- **Transition:** when `remaining` hits 0, `_fire_transition(next_mode)` sets
  `popup_open`, plays the sound, and calls `_show_popup(next_mode)`.
- **Popup (`_show_popup`):** a borderless full-screen `Toplevel`. On Windows it
  uses `attributes("-transparentcolor", ...)` so ONLY the words are visible
  (true per-pixel transparency); other platforms fall back to a faint dark tint
  with `-alpha`. A drop-shadow label sits behind the colored text for
  readability. **Single-popup rule:** the method returns early (just lifts the
  existing one) if `_popup_alive()`.
  - `do_done` = confirm: commits `mode`/`remaining` for the next phase (the timer
    starts NOW, on click), bumps the daily stand count, closes. In `preview=True`
    mode it only closes and changes nothing (used by the Settings test buttons).
  - `do_delete` = remove the shown quote from its list, persist, show another.
  - Bindings: left-click / `Esc` / `Space` / `Return` → done; right-click / `d` /
    `Delete` → delete. There is intentionally **no on-screen hint text**.
- **Persistence:** config and quotes live in `~/.standup_reminder/`
  (`CONFIG_DIR`). Defaults (`DEFAULT_CONFIG`, `DEFAULT_STAND_QUOTES`,
  `DEFAULT_SIT_QUOTES`) are written on first run. Helpers: `_read_json` /
  `_write_json`.
- **Auto-start:** ON by default (`DEFAULT_CONFIG["autostart"] = True`).
  `set_autostart(enable)` writes/removes `StandUpReminder.bat` in the per-user
  Startup folder (no admin, no registry). `__init__` self-heals: if the setting
  is on it re-creates the startup entry each launch; it never recreates it while
  off (turning it off in Settings removes it). `install.py` also enables it via
  `enable_autostart()` so it's on even before the first launch.
- **Window icon:** `_build_ui` calls `iconbitmap("standup.ico")` if present.
- **Auto-pause:** `_should_pause()` (checked every tick) returns a reason string
  when the timer should hold; `_tick` skips the decrement while it's set and the
  status shows "Paused — <reason>". Detectors (module-level, all stdlib, all
  Windows-only and fail-safe to False):
  - `_is_workstation_locked()` — `OpenInputDesktop` returns NULL when locked.
  - `_idle_seconds()` — `GetLastInputInfo`; `>= AWAY_IDLE_SECONDS` (120) = away /
    screen asleep.
  - `_in_call()` — reads `HKCU\...\CapabilityAccessManager\ConsentStore\
    {microphone,webcam}` (incl. `NonPackaged`); any app with `LastUsedTimeStop == 0`
    means the device is in use right now (covers Teams/Zoom/etc.).
  Toggles: `pause_when_away`, `pause_in_call` (both default True). Note: when the
  PC fully sleeps the process is suspended, so the timer pauses naturally.
- **Warm-up:** `startup_delay_minutes` (default 30). On launch `in_warmup` is set
  and `remaining` is the delay; when it elapses, `_tick` switches to a normal sit
  cycle WITHOUT a popup. `reset()`/`skip()` end the warm-up immediately.
- **Long-away restart:** `_tick` accumulates `away_seconds` while locked/away, and
  also adds large wall-clock gaps (`time.monotonic()` jumps > 90s) so full PC
  sleep counts even though the loop was frozen. When the user returns
  (`pause_reason` becomes None), if `away_seconds >= reset_after_away_minutes*60`
  (default 30) it calls `_restart_after_long_away()` → fresh sit cycle so the next
  popup is STAND UP. "In a call" pauses do NOT accrue away time.
- **Window placement:** `_place_bottom_right()` puts the control window and the
  Settings dialog in the lower-right corner (above the taskbar). The big STAND
  UP / SIT DOWN popup is still full-screen/centered.
- **Theme:** module-level `COL_*` palette + `FONT_UI`. `_mkbutton()` makes flat
  buttons with a hover highlight; reuse it for new buttons. Main window has a
  state-colored `accent_bar` and a status "card"; `_refresh_display` recolors them
  (blue=sitting, green=standing, peach=warm-up, muted=paused). ttk Combobox is
  themed via `clam` + `option_add` in `_build_ui`.
- **Tabbed main window:** `_build_ui` builds a `ttk.Notebook` (themed via `clam`)
  with three pages built by `_build_home_tab` (status card + Pause/Reset/Skip),
  `_build_timer_tab` (live `mm:ss` + `ttk.Progressbar` + detail line), and
  `_build_settings_tab` (the options form, formerly a Toplevel, now embedded; its
  Save shows a transient "Saved ✓"). `open_settings()` just selects the Settings
  tab (used by the menu). `_refresh_display` calls `_refresh_timer_tab(color)` each
  tick to update the countdown/progress/detail.
- **Single-instance dialog:** only Quotes is now a separate window, tracked in
  `self._quotes_win` with `_raise_if_open("_quotes_win")`; its `close()` clears the
  ref. (`self._settings_win` is vestigial — Settings is a tab now.)

## How to run & test

The app is a GUI, but you can validate logic headlessly (no window stays open):

```bash
cd StandUpReminder
python -c "
src=open('standup.py',encoding='utf-8').read(); g={}; exec(compile(src,'standup.py','exec'),g)
tk=g['tk']; root=tk.Tk(); app=g['StandUpApp'](root)
app.skip()                       # fire a real popup
print('popup_open:', app.popup_open)
app._show_popup('sit', preview=True)   # preview must NOT stack
print('one popup only:', app.active_popup is not None)
root.destroy(); print('OK')
"
```

Quick syntax check: `python -c "import ast; ast.parse(open('standup.py',encoding='utf-8').read())"`

To see it for real, restart the running copy:

```bash
# Windows (bash tool): find & kill, then relaunch
taskkill //IM pythonw.exe //F 2>/dev/null; (pythonw standup.py &)
```

When testing a popup interactively, use **Settings → Test popup** (preview mode)
so you don't disturb the real timer.

## Common change recipes

- **Add quotes:** append strings to `DEFAULT_STAND_QUOTES` /
  `DEFAULT_SIT_QUOTES` in `standup.py` (affects fresh installs). Existing users
  add via the in-app Quote Manager, or by editing
  `~/.standup_reminder/*_quotes.json`.
- **Change default times:** edit `DEFAULT_CONFIG["sit_minutes"]` /
  `["stand_minutes"]`. Note existing users keep their saved `config.json`.
- **Popup look:** colors `fg` and `panel_bg`, font tuple, and `rely` position in
  `_show_popup`.
- **Redesign the icon:** edit the drawing in `make_icon.py` (`_build_pixels`),
  then `python make_icon.py` to regenerate `standup.ico`, and commit it.

## Gotchas

- The transparent popup is **click-through on empty areas** (a side effect of
  `-transparentcolor`). The user dismisses by clicking the actual letters or
  pressing a key — this is intended. If you ever need click-anywhere, switch to a
  faint full-screen `-alpha` tint instead (loses the pure "floating words" look).
- The Desktop may be redirected by OneDrive; `install.py`'s `desktop_dir()`
  resolves the real path via `SHGetFolderPathW`.
- `make_icon.py` writes a PNG-backed `.ico` (Vista+). Fine for Win10/11.

## Publishing

Repo: https://github.com/johntsunami/StandUpReminder (branch `main`).

```bash
git add .
git commit -m "describe the change"
git push
```

Credentials are cached via Git Credential Manager on the user's machine.
