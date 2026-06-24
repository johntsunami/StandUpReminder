#!/usr/bin/env python3
"""
StandUp Reminder
================
A tiny, dependency-free desktop reminder that nudges you to STAND UP after
sitting too long, then to SIT DOWN after a shorter standing break. Built for
people managing lumbar/sacral back pain who need to regularly unload the spine.

Runs on *any* machine that has Python (3.7+). Uses ONLY the Python standard
library (tkinter, winsound, json, datetime) so there is NOTHING to pip install --
ideal for locked-down corporate / Citrix / HIPAA computers that allow Python
scripts but block package installs.

Author: built for jcnurse
License: MIT
"""

import os
import sys
import json
import random
import platform
import datetime
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

# winsound is Windows-only and part of the stdlib; degrade gracefully elsewhere.
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

try:
    import winreg
    HAS_WINREG = True
except ImportError:
    HAS_WINREG = False


# --------------------------------------------------------------------------- #
# Paths & configuration
# --------------------------------------------------------------------------- #
APP_NAME = "StandUp Reminder"
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".standup_reminder")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
STAND_FILE = os.path.join(CONFIG_DIR, "stand_quotes.json")
SIT_FILE = os.path.join(CONFIG_DIR, "sit_quotes.json")

# --- UI palette (a soft dark "Catppuccin"-ish theme) ----------------------- #
FONT_UI = "Segoe UI"
COL_BG = "#1e1e2e"        # window background
COL_PANEL = "#181825"     # header strips
COL_CARD = "#2a2b3d"      # raised cards / inputs
COL_FG = "#cdd6f4"        # primary text
COL_MUTED = "#8c92b8"     # secondary text
COL_GREEN = "#a6e3a1"     # standing / save
COL_BLUE = "#89b4fa"      # sitting
COL_PEACH = "#fab387"     # warming up
COL_BTN = "#313244"       # button base
COL_BTN_HI = "#45475a"    # button hover

DEFAULT_CONFIG = {
    "sit_minutes": 45,        # how long you sit before STAND UP fires
    "stand_minutes": 5,       # how long you stand before SIT DOWN fires
    "snooze_minutes": 5,      # snooze button duration
    "sound_enabled": True,    # play a chime when a popup fires
    "transparency": 0.90,     # popup opacity 0.5 (very see-through) - 1.0 (solid)
    "autostart": True,        # launch automatically at login (default ON)
    "stay_on_top": False,     # keep the little control window above others
    "startup_delay_minutes": 30,  # grace period after launch before the cycle begins
    "pause_when_away": True,  # pause while locked / screen asleep / idle
    "pause_in_call": True,    # pause while a call is using the mic or camera
    "reset_after_away_minutes": 30,  # away/locked >= this -> restart cycle (next = STAND UP)
    "stats": {"date": "", "stands": 0},
}

# --------------------------------------------------------------------------- #
# Default quote libraries  (you can add/delete/import your own in the app)
# --------------------------------------------------------------------------- #
DEFAULT_STAND_QUOTES = [
    "STAND UP!!! Your spine just filed a formal complaint.",
    "STAND UP!!! Gravity would like a word with your lumbar.",
    "Up you get! Your chair is not your soulmate.",
    "STAND UP!!! Your back called -- it is not amused.",
    "Rise and shine, desk warrior!",
    "STAND UP!!! Even your office chair is tired of you.",
    "On your feet! Those vertebrae will not decompress themselves.",
    "STAND UP!!! Sitting is the new smoking, and you're chain-smoking.",
    "Hoist yourself, human! Your sacrum thanks you in advance.",
    "STAND UP!!! Time to remind your legs that they exist.",
    "Get up! Your lumbar disc is doing the limbo and it hurts.",
    "STAND UP!!! Your butt has officially fused with the seat.",
    "Vertical time! Let the blood flow where it belongs.",
    "STAND UP!!! Your physical therapist is watching (spiritually).",
    "Rise, noble sitter, and stretch toward greatness!",
    "STAND UP!!! Your back pain wants to renegotiate the lease.",
    "Up! Up! Your posture is currently a crime scene.",
    "STAND UP!!! Pretend the floor is lava and your chair is hotter.",
    "Stand and deliver... your spine from doom!",
    "STAND UP!!! Your skeleton is begging for a remodel.",
    "Elevate yourself -- literally. Get up!",
    "STAND UP!!! The chair has held you hostage long enough.",
    "Time to defy gravity for 30 seconds, hero.",
    "STAND UP!!! Your hips don't lie -- they're stiff.",
    "Up and at 'em! Lighten that lumbar load.",
    "STAND UP!!! Your discs want a coffee break too.",
    "Behold! The mighty stand-up of the desk dweller!",
    "STAND UP!!! Your 'Sitting Champion' title has been revoked.",
    "Stretch those legs before they unionize.",
    "STAND UP!!! Your back is writing a strongly worded letter.",
    "Pop up like toast! Your spine deserves it.",
    "STAND UP!!! No one ever fixed their posture sitting down.",
    "Get vertical, you magnificent procrastinator.",
    "STAND UP!!! Your lumbar-sacral region demands respect.",
    "Rise! The chair gremlin loosens its grip.",
    "STAND UP!!! Future-you with a healthy back says thanks.",
    "Up you pop -- decompress that backbone!",
    "STAND UP!!! Your tailbone is sending an SOS.",
    "Lift off! Houston, we have a posture problem.",
    "STAND UP!!! Be the upright citizen you were born to be.",
    "Your chair needs space. Give it some. STAND UP!",
    "STAND UP!!! Spinal fluid called, it wants to move around.",
    "Stand tall, sit less, live long.",
    "STAND UP!!! Your back is unimpressed by your loyalty to the chair.",
    "Get up before your legs forget their job.",
    "STAND UP!!! The seat has claimed enough victims today.",
    "Reach for the ceiling, escape the chair's gravity well!",
    "STAND UP!!! Your posture coach just fainted.",
    "Stand up -- your spine's warranty depends on it.",
    "STAND UP!!! Operation Decompress Lumbar is a go.",
    "Up! Even a houseplant moves more than you.",
    "STAND UP!!! Your vertebrae are stacking up complaints.",
    "Defeat the chair. Stand victorious.",
    "STAND UP!!! Your back-pain-therapist sense is tingling.",
    "Rise like the legend of good posture you are.",
    "STAND UP!!! Your sacrum just texted 'help'.",
    "Get those bones vertical, champ!",
    "STAND UP!!! Sitting any longer voids the back warranty.",
    "Time to stand -- your discs need some elbow room.",
    "STAND UP!!! Your lumbar curve misses the good old days.",
    "Up and out of that gravity trap!",
    "STAND UP!!! Be the upright hero this desk needs.",
    "Stretch now or regret it at 3pm.",
    "STAND UP!!! Your spine just rolled its eyes.",
    "Vertical mode: engaged. Get up!",
    "STAND UP!!! Don't make your physio cry.",
    "Stand and unstiffen, oh weary one.",
    "STAND UP!!! Your back is keeping score.",
    "Hop up! Your circulation booked a tour.",
    "STAND UP!!! The chair does not love you back.",
    "Rise -- your posture is currently a question mark.",
    "STAND UP!!! Decompress before you depress (the disc).",
    "Up! Your lumbar deserves a standing ovation.",
    "STAND UP!!! Your spine's group chat is blowing up.",
    "Stand, stretch, conquer.",
    "STAND UP!!! Even gravity is rooting for your back.",
    "Get up -- sitting trophies do not exist.",
    "STAND UP!!! Your tailbone filed for independence.",
    "Lift those glutes off the throne, your majesty.",
    "STAND UP!!! Your back muscles are napping. Wake them.",
    "Time to be tall and proud. Up you go!",
    "STAND UP!!! Your discs are doing yoga without you.",
    "Rise and reduce that sacral pressure!",
    "STAND UP!!! The seat cushion needs a breather.",
    "Up! Be the stretch you wish to see in the world.",
    "STAND UP!!! Your spine is not impressed by your stamina.",
    "Stand now; your future back will high-five you.",
    "STAND UP!!! Operation 'Save the Lumbar' is commencing.",
    "Get vertical or get achy. Your call. (Get vertical.)",
    "STAND UP!!! Your posture just hit rock bottom -- literally.",
    "Rise, stretch, repeat. Your back's favorite song.",
    "STAND UP!!! The chair's spell is broken!",
    "Up -- let those hip flexors off the hook.",
    "STAND UP!!! Your spinal column requests maintenance.",
    "Stand tall, you desk-dwelling marvel.",
    "STAND UP!!! Your back called in a favor.",
    "Elevate the body, liberate the spine!",
    "STAND UP!!! Your lumbar load is over the legal limit.",
    "Get up and shake out the chair gremlins.",
    "STAND UP!!! You've unlocked: Standing Achievement!",
    "Rise, hydrate, and conquer your spine goals.",
    "STAND UP!!! Your back is doing you a solid -- return the favor.",
    "Up you go -- the floor misses your feet.",
    "STAND UP!!! Less sitting, more living.",
    "Your spine is about to thank you. STAND UP!",
]

DEFAULT_SIT_QUOTES = [
    "SIT DOWN -- you stood your ground, now rest it.",
    "Take a seat, champion. Mission accomplished.",
    "SIT DOWN -- the standing tour has concluded.",
    "Park it. Your legs have earned a break.",
    "SIT DOWN -- gravity says you win this round.",
    "Rest those legs, you upright legend.",
    "SIT DOWN -- the chair has missed you dearly.",
    "Lower the landing gear. Time to sit.",
    "SIT DOWN -- you have reached peak vertical.",
    "Take a load off; you've earned the cushion.",
    "SIT DOWN -- your knees have filed for a recess.",
    "Descend gently to your throne, your majesty.",
    "SIT DOWN -- standing achievement complete!",
    "Plant yourself. The standing quota is met.",
    "SIT DOWN -- your feet just texted 'we're done'.",
    "Ease back into the seat of power.",
    "SIT DOWN -- you stood, you saw, you conquered.",
    "Rest mode: activated. Take a seat.",
    "SIT DOWN -- the chair forgives your absence.",
    "Lower yourself like the graceful swan you are.",
    "SIT DOWN -- well stood, soldier.",
    "Time to sit and let the back recalibrate.",
    "SIT DOWN -- your standing shift is over.",
    "Take five (sitting down).",
    "SIT DOWN -- gravity has called a truce.",
    "Sink into the seat. You did good.",
    "SIT DOWN -- legs off duty.",
    "Reclaim your chair, conquering hero.",
    "SIT DOWN -- the floor releases you.",
    "Rest the dogs -- you've stood enough.",
    "SIT DOWN -- recharge for the next round.",
    "Lower the mast, sailor. Time to sit.",
    "SIT DOWN -- your standing license has expired.",
    "Take a seat and bask in your good posture.",
    "SIT DOWN -- even superheroes sit sometimes.",
    "Settle in. The standing storm has passed.",
    "SIT DOWN -- your calves request asylum.",
    "Gracefully greet the chair once more.",
    "SIT DOWN -- well done, upright warrior.",
    "Time to perch. You've earned it.",
    "SIT DOWN -- the vertical chapter ends here.",
    "Rest your frame, you magnificent stander.",
    "SIT DOWN -- feet up, spirits high.",
    "Return to base; the chair awaits.",
    "SIT DOWN -- standing montage complete.",
    "Lower into comfort -- you've done your reps.",
    "SIT DOWN -- your legs deserve a (seated) standing ovation.",
    "Take the weight off, hero.",
    "SIT DOWN -- the throne grows cold without you.",
    "Ease down, breathe, reset.",
    "SIT DOWN -- you've out-stood the competition.",
    "Plop with pride. You earned this seat.",
    "SIT DOWN -- achievement unlocked, now relax.",
    "Reunite with your chair. It's been lonely.",
    "SIT DOWN -- your quota of vertical glory is met.",
    "Settle those bones; you did the work.",
    "SIT DOWN -- the standing dragon is slain.",
    "Recline, refuel, return stronger.",
    "SIT DOWN -- your feet have left the chat.",
    "Take your seat; intermission has arrived.",
    "SIT DOWN -- back to base camp, climber.",
    "Rest now; the next stand-up awaits.",
]


# --------------------------------------------------------------------------- #
# Small JSON helpers
# --------------------------------------------------------------------------- #
def _read_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return default


def _write_json(path, data):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        return True
    except Exception as exc:
        print("Could not write %s: %s" % (path, exc))
        return False


# --------------------------------------------------------------------------- #
# Main application
# --------------------------------------------------------------------------- #
class StandUpApp:
    def __init__(self, root):
        self.root = root

        # --- load persisted state -------------------------------------------
        os.makedirs(CONFIG_DIR, exist_ok=True)
        self.config = DEFAULT_CONFIG.copy()
        self.config.update(_read_json(CONFIG_FILE, {}))
        self.config.setdefault("stats", {"date": "", "stands": 0})

        # Auto-start defaults ON. Whenever it's enabled, make sure the per-user
        # startup entry actually exists (idempotent + self-healing). Turning it
        # off in Settings removes the entry; we never recreate it while off.
        if self.config.get("autostart") and platform.system() == "Windows":
            try:
                ok, _msg = set_autostart(True)
                self.config["autostart"] = bool(ok)
            except Exception:
                pass

        self.stand_quotes = _read_json(STAND_FILE, None) or list(DEFAULT_STAND_QUOTES)
        self.sit_quotes = _read_json(SIT_FILE, None) or list(DEFAULT_SIT_QUOTES)
        if not os.path.exists(STAND_FILE):
            _write_json(STAND_FILE, self.stand_quotes)
        if not os.path.exists(SIT_FILE):
            _write_json(SIT_FILE, self.sit_quotes)

        # --- timer state ----------------------------------------------------
        self.mode = "sit"                       # current posture: "sit" or "stand"
        delay = max(0, int(self.config.get("startup_delay_minutes", 0))) * 60
        self.in_warmup = delay > 0              # grace period right after launch
        self.remaining = delay if self.in_warmup else self.duration_for("sit")
        self.running = True                     # is the countdown active?
        self.popup_open = False                 # paused while a popup is showing
        self.pending_mode = None                # mode to switch to after popup
        self.active_popup = None
        self.pause_reason = None                # set when locked / away / in a call
        self.away_seconds = 0                   # how long we've been locked/away
        self.last_tick = time.monotonic()       # to detect PC sleep (big time gaps)
        self._settings_win = None               # single-instance dialogs
        self._quotes_win = None

        self._roll_stats_day()
        self._build_ui()
        self._apply_stay_on_top()
        self._tick()                            # start the 1-second heartbeat

    # ------------------------------------------------------------------ utils
    def duration_for(self, mode):
        mins = self.config["stand_minutes"] if mode == "stand" else self.config["sit_minutes"]
        return max(1, int(mins)) * 60

    def quotes_for(self, mode):
        return self.stand_quotes if mode == "stand" else self.sit_quotes

    def save_config(self):
        _write_json(CONFIG_FILE, self.config)

    def _roll_stats_day(self):
        today = datetime.date.today().isoformat()
        if self.config["stats"].get("date") != today:
            self.config["stats"] = {"date": today, "stands": 0}
            self.save_config()

    # -------------------------------------------------------------- UI build
    def _build_ui(self):
        self.root.title(APP_NAME)
        try:
            _ico = os.path.join(os.path.dirname(os.path.abspath(__file__)), "standup.ico")
            if os.path.exists(_ico):
                self.root.iconbitmap(_ico)
        except Exception:
            pass
        self.root.minsize(340, 360)
        self._place_bottom_right(self.root, 380, 560)
        self.root.configure(bg=COL_BG)

        # Dark theming for ttk widgets (the Quote Manager combo box).
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TCombobox", fieldbackground=COL_CARD, background=COL_BTN,
                        foreground=COL_FG, arrowcolor=COL_FG, bordercolor=COL_BTN,
                        lightcolor=COL_BTN, darkcolor=COL_BTN, relief="flat")
        style.map("TCombobox", fieldbackground=[("readonly", COL_CARD)],
                  foreground=[("readonly", COL_FG)])
        self.root.option_add("*TCombobox*Listbox.background", COL_CARD)
        self.root.option_add("*TCombobox*Listbox.foreground", COL_FG)
        self.root.option_add("*TCombobox*Listbox.selectBackground", COL_BTN_HI)
        style.configure("TNotebook", background=COL_BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=COL_PANEL, foreground=COL_MUTED,
                        padding=[14, 7], borderwidth=0, font=(FONT_UI, 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", COL_BG)],
                  foreground=[("selected", COL_FG)])
        style.configure("Stand.Horizontal.TProgressbar", troughcolor=COL_CARD,
                        background=COL_GREEN, borderwidth=0, thickness=14)

        # Menu bar
        menubar = tk.Menu(self.root)
        menubar.add_command(label="Settings", command=self.open_settings)
        menubar.add_command(label="Quotes", command=self.open_quotes_manager)
        menubar.add_command(label="Help", command=self.show_help)
        self.root.config(menu=menubar)

        self.status_var = tk.StringVar()
        self.stats_var = tk.StringVar()

        # Top accent strip -- recolors to match the current state.
        self.accent_bar = tk.Frame(self.root, bg=COL_BLUE, height=4)
        self.accent_bar.pack(fill="x", side="top")

        # Tabbed interface: Home / Timer / Settings
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)
        self.tab_home = tk.Frame(self.notebook, bg=COL_BG)
        self.tab_timer = tk.Frame(self.notebook, bg=COL_BG)
        self.tab_settings = tk.Frame(self.notebook, bg=COL_BG)
        self.notebook.add(self.tab_home, text="  Home  ")
        self.notebook.add(self.tab_timer, text="  Timer  ")
        self.notebook.add(self.tab_settings, text="  Settings  ")
        self._build_home_tab(self.tab_home)
        self._build_timer_tab(self.tab_timer)
        self._build_settings_tab(self.tab_settings)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self._refresh_display()

    def open_settings(self):
        """Settings now lives in a tab -- just bring it forward."""
        try:
            self.notebook.select(self.tab_settings)
        except Exception:
            pass

    # ---------------------------------------------------------------- tabs
    def _build_home_tab(self, parent):
        tk.Label(parent, text="🪑  StandUp Reminder", font=(FONT_UI, 10, "bold"),
                 fg=COL_MUTED, bg=COL_BG).pack(anchor="w", padx=16, pady=(14, 0))
        card = tk.Frame(parent, bg=COL_CARD)
        card.pack(fill="x", padx=16, pady=(10, 14))
        self.status_lbl = tk.Label(card, textvariable=self.status_var,
                                   font=(FONT_UI, 20, "bold"), fg=COL_BLUE, bg=COL_CARD)
        self.status_lbl.pack(pady=(16, 2))
        tk.Label(card, textvariable=self.stats_var, font=(FONT_UI, 9),
                 fg=COL_MUTED, bg=COL_CARD).pack(pady=(0, 14))
        btns = tk.Frame(parent, bg=COL_BG)
        btns.pack(fill="x", padx=16, pady=(0, 16))
        self.start_btn = self._mkbutton(btns, "Pause", self.toggle_running)
        self.start_btn.pack(side="left", expand=True, fill="x", padx=(0, 4))
        self._mkbutton(btns, "Reset", self.reset).pack(side="left", expand=True, fill="x", padx=4)
        self._mkbutton(btns, "Skip", self.skip).pack(side="left", expand=True, fill="x", padx=(4, 0))

    def _build_timer_tab(self, parent):
        self.timer_state_var = tk.StringVar()
        self.timer_value_var = tk.StringVar(value="00:00")
        self.timer_detail_var = tk.StringVar()

        tk.Label(parent, text="⏱  Live timer", font=(FONT_UI, 10, "bold"),
                 fg=COL_MUTED, bg=COL_BG).pack(anchor="w", padx=16, pady=(14, 0))
        card = tk.Frame(parent, bg=COL_CARD)
        card.pack(fill="both", expand=True, padx=16, pady=(10, 16))
        self.timer_state_lbl = tk.Label(card, textvariable=self.timer_state_var,
                                        font=(FONT_UI, 11), fg=COL_FG, bg=COL_CARD,
                                        wraplength=300)
        self.timer_state_lbl.pack(pady=(22, 4))
        self.timer_value_lbl = tk.Label(card, textvariable=self.timer_value_var,
                                        font=("Consolas", 46, "bold"), fg=COL_BLUE, bg=COL_CARD)
        self.timer_value_lbl.pack()
        self.timer_bar = ttk.Progressbar(card, style="Stand.Horizontal.TProgressbar",
                                         maximum=1000, length=250)
        self.timer_bar.pack(pady=(12, 8))
        self.timer_detail_lbl = tk.Label(card, textvariable=self.timer_detail_var,
                                         font=(FONT_UI, 9), fg=COL_MUTED, bg=COL_CARD,
                                         wraplength=300)
        self.timer_detail_lbl.pack(pady=(0, 20))

    def _mkbutton(self, parent, text, command, bg=COL_BTN, hover=COL_BTN_HI,
                  fg=COL_FG, width=8, font=None):
        """A flat, padded button with a hover highlight."""
        b = tk.Button(parent, text=text, command=command, width=width,
                      bg=bg, fg=fg, activebackground=hover, activeforeground=fg,
                      relief="flat", bd=0, highlightthickness=0, cursor="hand2",
                      font=font or (FONT_UI, 10, "bold"), padx=8, pady=7)
        b.bind("<Enter>", lambda e: b.config(bg=hover))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
        return b

    def _raise_if_open(self, attr):
        """If a tracked dialog is already open, surface it and return True."""
        w = getattr(self, attr, None)
        if w is not None:
            try:
                if w.winfo_exists():
                    w.deiconify()
                    w.lift()
                    w.focus_force()
                    return True
            except Exception:
                pass
        return False

    def _place_bottom_right(self, win, w, h, margin=24, taskbar=56):
        """Position a window in the lower-right corner, above the taskbar."""
        try:
            sw = win.winfo_screenwidth()
            sh = win.winfo_screenheight()
            x = max(0, sw - w - margin)
            y = max(0, sh - h - margin - taskbar)
            win.geometry("%dx%d+%d+%d" % (w, h, x, y))
        except Exception:
            win.geometry("%dx%d" % (w, h))

    def _apply_stay_on_top(self):
        try:
            self.root.attributes("-topmost", bool(self.config.get("stay_on_top")))
        except Exception:
            pass

    # ----------------------------------------------------------- timer loop
    def _popup_alive(self):
        """True while any popup (real or preview) is on screen."""
        try:
            return self.active_popup is not None and bool(self.active_popup.winfo_exists())
        except Exception:
            return False

    def _should_pause(self):
        """Return a short reason string if the timer should hold, else None."""
        if self.config.get("pause_when_away"):
            if _is_workstation_locked():
                return "screen locked"
            if _idle_seconds() >= AWAY_IDLE_SECONDS:
                return "away from desk"
        if self.config.get("pause_in_call"):
            if _in_call():
                return "in a call"
        return None

    def _restart_after_long_away(self):
        """A long lock/sleep counts as a movement break: start a fresh sit
        period so the very next prompt is STAND UP."""
        self.in_warmup = False
        self.mode = "sit"
        self.remaining = self.duration_for("sit")

    def _tick(self):
        # Detect a big wall-clock jump (the PC was asleep/suspended while our
        # 1-second loop was frozen) so that sleep also counts as "away" time.
        now = time.monotonic()
        gap = now - self.last_tick
        self.last_tick = now
        big_gap = int(gap) if gap > 90 else 0

        # The timer is frozen while a popup is showing, so nothing stacks up or
        # keeps firing if you've stepped away -- exactly one popup waits for you.
        if self.running and not self.popup_open and not self._popup_alive():
            self.pause_reason = self._should_pause()
            if big_gap:
                self.away_seconds += big_gap          # time spent suspended/asleep

            if self.pause_reason in ("screen locked", "away from desk"):
                self.away_seconds += 1                # keep holding; accrue away time
            elif self.pause_reason is None:
                # Back at the desk. If we were away/locked long enough, assume the
                # user was up and moving -> restart so the next popup is STAND UP.
                threshold = max(1, int(self.config.get("reset_after_away_minutes", 30))) * 60
                if self.away_seconds >= threshold:
                    self._restart_after_long_away()
                self.away_seconds = 0
                self.remaining -= 1
                if self.remaining <= 0:
                    if self.in_warmup:
                        # Grace period over -> begin the real sitting cycle.
                        self.in_warmup = False
                        self.mode = "sit"
                        self.remaining = self.duration_for("sit")
                    else:
                        nxt = "stand" if self.mode == "sit" else "sit"
                        self._fire_transition(nxt)
            # else ("in a call"): just hold, without accruing away time
        self._refresh_display()
        self.root.after(1000, self._tick)

    def _refresh_display(self):
        # No countdown is shown on purpose -- just the current state, in words.
        if not self.running:
            state, color = "Paused", COL_MUTED
        elif self.pause_reason:
            state, color = "Paused — %s" % self.pause_reason, COL_MUTED
        elif self.in_warmup:
            state, color = "Getting started…", COL_PEACH
        elif self.mode == "stand":
            state, color = "Standing", COL_GREEN
        else:
            state, color = "Sitting", COL_BLUE
        self.status_var.set(state)
        try:
            self.status_lbl.config(fg=color)
            self.accent_bar.config(bg=color)
        except Exception:
            pass
        self.start_btn.config(text="Start" if not self.running else "Pause")
        self.stats_var.set("✔  %d stand breaks today" % self.config["stats"].get("stands", 0))
        self._refresh_timer_tab(color)

    def _refresh_timer_tab(self, color):
        """Drive the live countdown shown on the Timer tab."""
        if not hasattr(self, "timer_value_var"):
            return
        mins, secs = divmod(max(0, self.remaining), 60)
        self.timer_value_var.set("%02d:%02d" % (mins, secs))

        if self.in_warmup:
            total = max(1, int(self.config.get("startup_delay_minutes", 1)) * 60)
            phase = "Warm-up — first reminder after this"
        elif self.mode == "stand":
            total = self.duration_for("stand")
            phase = "Standing — SIT DOWN when this ends"
        else:
            total = self.duration_for("sit")
            phase = "Sitting — STAND UP when this ends"
        frac = 1.0 - (self.remaining / total) if total else 0
        try:
            self.timer_bar["value"] = max(0, min(1000, int(frac * 1000)))
            self.timer_value_lbl.config(fg=color)
        except Exception:
            pass

        if not self.running:
            phase, detail = "Paused", "Press Start on the Home tab to resume."
        elif self.pause_reason:
            detail = "Auto-paused (%s) — resumes on its own." % self.pause_reason
        else:
            detail = "Counting down once per second — it's working."
        self.timer_state_var.set(phase)
        self.timer_detail_var.set(detail)

    # ----------------------------------------------------------- controls
    def toggle_running(self):
        self.running = not self.running
        self._refresh_display()

    def reset(self):
        self.in_warmup = False
        self.mode = "sit"
        self.remaining = self.duration_for("sit")
        self.running = True
        self.pause_reason = None
        self._refresh_display()

    def skip(self):
        """Skip ahead: end the warm-up, or fire the next popup now."""
        if self.popup_open:
            return
        if self.in_warmup:
            self.in_warmup = False
            self.mode = "sit"
            self.remaining = self.duration_for("sit")
            self._refresh_display()
            return
        nxt = "stand" if self.mode == "sit" else "sit"
        self._fire_transition(nxt)

    # ----------------------------------------------------------- transitions
    def _fire_transition(self, next_mode):
        # Only ever one popup at a time -- if one is already up, wait for it.
        if self._popup_alive():
            self.remaining = 1
            return
        self.popup_open = True
        self.pending_mode = next_mode
        self._play_sound()
        self._show_popup(next_mode)

    def _play_sound(self):
        if not self.config.get("sound_enabled"):
            return
        try:
            if HAS_WINSOUND:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            else:
                self.root.bell()
        except Exception:
            pass

    # ----------------------------------------------------------- the popup
    def _show_popup(self, target, preview=False):
        quotes = self.quotes_for(target)
        state = {"quote": random.choice(quotes) if quotes else (
            "STAND UP!!!" if target == "stand" else "SIT DOWN!!!")}

        fg = "#7CFF9B" if target == "stand" else "#8FB8FF"   # green=stand, blue=sit

        # Enforce a single popup on screen at any time -- ignore extra requests
        # (e.g. mashing the test button) and just surface the existing one.
        if self._popup_alive():
            try:
                self.active_popup.lift()
                self.active_popup.focus_force()
            except Exception:
                pass
            return

        top = tk.Toplevel(self.root)
        self.active_popup = top
        top.overrideredirect(True)               # no title bar / chrome at all
        sw = top.winfo_screenwidth()
        sh = top.winfo_screenheight()
        top.geometry("%dx%d+0+0" % (sw, sh))     # cover the whole screen
        try:
            top.attributes("-topmost", True)
        except Exception:
            pass

        # Make the background invisible so ONLY the words show on the screen
        # (true per-pixel transparency on Windows). Fall back to a faint dark
        # tint on platforms that don't support -transparentcolor.
        TRANSPARENT = "#FF00FF"
        top.configure(bg=TRANSPARENT)
        try:
            top.attributes("-transparentcolor", TRANSPARENT)
            panel_bg = TRANSPARENT
        except Exception:
            panel_bg = "#0e0e16"
            top.configure(bg=panel_bg)
            try:
                top.attributes("-alpha", 0.88)
            except Exception:
                pass

        wl = int(sw * 0.82)
        font = ("Segoe UI Black", 48, "bold")

        # Drop shadow (offset, dark) behind the bright text so the words stay
        # readable over any background.
        shadow = tk.Label(top, text=state["quote"], font=font, fg="#050505",
                          bg=panel_bg, wraplength=wl, justify="center")
        shadow.place(relx=0.5, rely=0.44, anchor="center", x=3, y=3)
        label = tk.Label(top, text=state["quote"], font=font, fg=fg,
                         bg=panel_bg, wraplength=wl, justify="center")
        label.place(relx=0.5, rely=0.44, anchor="center")

        def refresh_quote(event=None):
            q = self.quotes_for(target)
            nq = random.choice(q) if q else (
                "STAND UP!!!" if target == "stand" else "SIT DOWN!!!")
            state["quote"] = nq
            label.config(text=nq)
            shadow.config(text=nq)

        def close_popup():
            self.active_popup = None
            if not preview:
                self.popup_open = False
            try:
                top.destroy()
            except Exception:
                pass

        def do_done(event=None):
            # Closing IS the confirmation. The next phase's timer starts NOW --
            # when you click -- not when the popup first appeared. In preview
            # mode (the Settings test buttons) it just closes, changing nothing.
            if preview:
                close_popup()
                return
            self.mode = self.pending_mode
            self.remaining = self.duration_for(self.mode)
            if self.mode == "stand":
                self._roll_stats_day()
                self.config["stats"]["stands"] += 1
                self.save_config()
            close_popup()

        def do_delete(event=None):
            q = self.quotes_for(target)
            if state["quote"] in q:
                q.remove(state["quote"])
                _write_json(STAND_FILE if target == "stand" else SIT_FILE, q)
            refresh_quote()
            return "break"

        for widget in (top, label, shadow):
            widget.bind("<Button-1>", do_done)   # left-click a word = done
            widget.bind("<Button-3>", do_delete)  # right-click = skip this line
        top.bind("<Escape>", do_done)
        top.bind("<space>", do_done)
        top.bind("<Return>", do_done)
        top.bind("<Key-d>", do_delete)
        top.bind("<Delete>", do_delete)

        top.lift()
        top.after(30, top.focus_force)

    # ----------------------------------------------------------- settings tab
    def _build_settings_tab(self, parent):
        save_status = tk.StringVar()

        # Footer (packed first so it stays pinned to the bottom).
        foot = tk.Frame(parent, bg=COL_BG)
        foot.pack(side="bottom", fill="x", padx=16, pady=(0, 14))
        tk.Label(foot, textvariable=save_status, fg=COL_GREEN, bg=COL_BG,
                 font=(FONT_UI, 9, "bold")).pack(side="left")

        body = tk.Frame(parent, bg=COL_BG)
        body.pack(side="top", fill="both", expand=True, padx=16, pady=(12, 4))

        sit_v = tk.IntVar(value=self.config["sit_minutes"])
        stand_v = tk.IntVar(value=self.config["stand_minutes"])
        delay_v = tk.IntVar(value=self.config.get("startup_delay_minutes", 30))
        sound_v = tk.BooleanVar(value=self.config["sound_enabled"])
        away_v = tk.BooleanVar(value=self.config.get("pause_when_away", True))
        call_v = tk.BooleanVar(value=self.config.get("pause_in_call", True))
        reset_v = tk.IntVar(value=self.config.get("reset_after_away_minutes", 30))
        topmost_v = tk.BooleanVar(value=self.config["stay_on_top"])
        auto_v = tk.BooleanVar(value=self.config["autostart"])
        trans_v = tk.DoubleVar(value=self.config["transparency"])

        def row(r, text, widget):
            tk.Label(body, text=text, fg=COL_FG, bg=COL_BG, font=(FONT_UI, 10)).grid(
                row=r, column=0, sticky="w", padx=(0, 14), pady=5)
            widget.grid(row=r, column=1, sticky="e", pady=5)

        def spin(var, lo, hi):
            return tk.Spinbox(body, from_=lo, to=hi, textvariable=var, width=6,
                              bg=COL_CARD, fg=COL_FG, buttonbackground=COL_BTN,
                              insertbackground=COL_FG, relief="flat", justify="center",
                              highlightthickness=1, highlightbackground=COL_BTN,
                              highlightcolor=COL_BLUE)

        def check(var):
            return tk.Checkbutton(body, variable=var, bg=COL_BG, fg=COL_FG,
                                  activebackground=COL_BG, selectcolor=COL_CARD,
                                  highlightthickness=0, bd=0)

        row(0, "Sit time before STAND UP (min)", spin(sit_v, 1, 240))
        row(1, "Stand time before SIT DOWN (min)", spin(stand_v, 1, 120))
        row(2, "Start timer this long after launch (min)", spin(delay_v, 0, 240))
        row(3, "Restart cycle if away/locked over (min)", spin(reset_v, 1, 240))
        row(4, "Popup transparency",
            tk.Scale(body, from_=0.5, to=1.0, resolution=0.05, orient="horizontal",
                     variable=trans_v, length=140, bg=COL_BG, fg=COL_MUTED,
                     troughcolor=COL_CARD, activebackground=COL_GREEN,
                     highlightthickness=0, bd=0))
        row(5, "Play sound on popup", check(sound_v))
        row(6, "Pause when locked / screen asleep", check(away_v))
        row(7, "Pause during calls (mic or camera in use)", check(call_v))
        row(8, "Keep control window on top", check(topmost_v))
        row(9, "Start automatically at login", check(auto_v))
        body.grid_columnconfigure(0, weight=1)

        def save():
            self.config["sit_minutes"] = max(1, int(sit_v.get()))
            self.config["stand_minutes"] = max(1, int(stand_v.get()))
            self.config["startup_delay_minutes"] = max(0, int(delay_v.get()))
            self.config["sound_enabled"] = bool(sound_v.get())
            self.config["pause_when_away"] = bool(away_v.get())
            self.config["pause_in_call"] = bool(call_v.get())
            self.config["reset_after_away_minutes"] = max(1, int(reset_v.get()))
            self.config["stay_on_top"] = bool(topmost_v.get())
            self.config["transparency"] = float(trans_v.get())

            want_auto = bool(auto_v.get())
            if want_auto != self.config["autostart"]:
                ok, msg = set_autostart(want_auto)
                if ok:
                    self.config["autostart"] = want_auto
                else:
                    messagebox.showwarning(APP_NAME, msg, parent=self.root)

            self.save_config()
            self._apply_stay_on_top()
            # Apply new sit/stand durations to the current cycle right away.
            if not self.in_warmup:
                self.remaining = min(self.remaining, self.duration_for(self.mode))
            self._refresh_display()
            save_status.set("Saved ✓")
            self.root.after(2200, lambda: save_status.set(""))

        # Live preview: press as many times as you like to test popups.
        test = tk.Frame(body, bg=COL_BG)
        test.grid(row=10, column=0, columnspan=2, pady=(14, 0), sticky="w")
        tk.Label(test, text="Test popup:", fg=COL_MUTED, bg=COL_BG,
                 font=(FONT_UI, 10)).pack(side="left", padx=(0, 8))
        self._mkbutton(test, "STAND UP", lambda: self._show_popup("stand", preview=True),
                       bg="#2d4a36", hover="#3a5e45", width=10).pack(side="left", padx=3)
        self._mkbutton(test, "SIT DOWN", lambda: self._show_popup("sit", preview=True),
                       bg="#2c3a52", hover="#384a66", width=10).pack(side="left", padx=3)

        self._mkbutton(foot, "Save", save, bg=COL_GREEN, hover="#b6f0b0",
                       fg="#10331b", width=12).pack(side="right")

    # ----------------------------------------------------------- quotes mgr
    def open_quotes_manager(self):
        if self._raise_if_open("_quotes_win"):
            return
        win = tk.Toplevel(self.root)
        self._quotes_win = win
        win.title("Quote Manager")
        win.configure(bg=COL_BG)
        win.geometry("580x470")
        win.transient(self.root)

        def close():
            self._quotes_win = None
            win.destroy()
        win.protocol("WM_DELETE_WINDOW", close)

        head = tk.Frame(win, bg=COL_PANEL)
        head.pack(fill="x")
        tk.Label(head, text="💬  Quote Manager", font=(FONT_UI, 13, "bold"),
                 fg=COL_FG, bg=COL_PANEL).pack(anchor="w", padx=16, pady=10)
        tk.Frame(win, bg=COL_GREEN, height=3).pack(fill="x")

        top_bar = tk.Frame(win, bg=COL_BG)
        top_bar.pack(fill="x", padx=14, pady=10)
        tk.Label(top_bar, text="Editing:", fg=COL_FG, bg=COL_BG,
                 font=(FONT_UI, 10)).pack(side="left")
        which = tk.StringVar(value="STAND UP quotes")
        combo = ttk.Combobox(top_bar, textvariable=which, state="readonly", width=20,
                             values=["STAND UP quotes", "SIT DOWN quotes"])
        combo.pack(side="left", padx=8)

        count_var = tk.StringVar()
        tk.Label(top_bar, textvariable=count_var, fg=COL_MUTED, bg=COL_BG,
                 font=(FONT_UI, 9)).pack(side="right")

        list_frame = tk.Frame(win, bg=COL_BG)
        list_frame.pack(fill="both", expand=True, padx=14)
        scroll = tk.Scrollbar(list_frame)
        scroll.pack(side="right", fill="y")
        lb = tk.Listbox(list_frame, yscrollcommand=scroll.set, font=(FONT_UI, 10),
                        bg="#11111b", fg=COL_FG, selectbackground=COL_BTN_HI,
                        relief="flat", highlightthickness=1, highlightbackground=COL_BTN,
                        activestyle="none", bd=0)
        lb.pack(side="left", fill="both", expand=True)
        scroll.config(command=lb.yview)

        def target_key():
            return "stand" if which.get().startswith("STAND") else "sit"

        def target_file():
            return STAND_FILE if target_key() == "stand" else SIT_FILE

        def reload_list():
            lb.delete(0, "end")
            for q in self.quotes_for(target_key()):
                lb.insert("end", q)
            count_var.set("%d quotes" % lb.size())

        def persist():
            _write_json(target_file(), self.quotes_for(target_key()))
            reload_list()

        def add_quote():
            text = simpledialog.askstring("Add quote",
                                          "Enter a new %s line:" % target_key().upper(),
                                          parent=win)
            if text and text.strip():
                self.quotes_for(target_key()).append(text.strip())
                persist()

        def delete_selected():
            sel = list(lb.curselection())
            if not sel:
                return
            lst = self.quotes_for(target_key())
            for idx in reversed(sel):
                if 0 <= idx < len(lst):
                    del lst[idx]
            persist()

        def import_quotes():
            path = filedialog.askopenfilename(
                parent=win, title="Import quotes (one per line)",
                filetypes=[("Text/JSON", "*.txt *.json"), ("All files", "*.*")])
            if not path:
                return
            added = 0
            lst = self.quotes_for(target_key())
            try:
                if path.lower().endswith(".json"):
                    data = _read_json(path, [])
                    items = data if isinstance(data, list) else []
                else:
                    with open(path, "r", encoding="utf-8") as fh:
                        items = [ln.strip() for ln in fh]
                for it in items:
                    it = str(it).strip()
                    if it and it not in lst:
                        lst.append(it)
                        added += 1
                persist()
                messagebox.showinfo(APP_NAME, "Imported %d new quote(s)." % added, parent=win)
            except Exception as exc:
                messagebox.showerror(APP_NAME, "Import failed: %s" % exc, parent=win)

        def export_quotes():
            path = filedialog.asksaveasfilename(
                parent=win, title="Export quotes", defaultextension=".txt",
                filetypes=[("Text", "*.txt")])
            if not path:
                return
            try:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write("\n".join(self.quotes_for(target_key())))
                messagebox.showinfo(APP_NAME, "Exported to:\n%s" % path, parent=win)
            except Exception as exc:
                messagebox.showerror(APP_NAME, "Export failed: %s" % exc, parent=win)

        def restore_defaults():
            if messagebox.askyesno(APP_NAME,
                                   "Replace the current list with the built-in defaults?",
                                   parent=win):
                if target_key() == "stand":
                    self.stand_quotes = list(DEFAULT_STAND_QUOTES)
                else:
                    self.sit_quotes = list(DEFAULT_SIT_QUOTES)
                persist()

        btns = tk.Frame(win, bg=COL_BG)
        btns.pack(fill="x", padx=14, pady=12)
        self._mkbutton(btns, "Add", add_quote, bg=COL_GREEN, hover="#b6f0b0",
                       fg="#10331b", width=8).pack(side="left", padx=(0, 4))
        for txt, cmd in [("Delete", delete_selected), ("Import", import_quotes),
                         ("Export", export_quotes), ("Restore defaults", restore_defaults)]:
            self._mkbutton(btns, txt, cmd, width=12).pack(side="left", padx=4)
        self._mkbutton(btns, "Close", close, width=8).pack(side="right")

        combo.bind("<<ComboboxSelected>>", lambda e: reload_list())
        reload_list()

    # ----------------------------------------------------------- help/about
    def show_help(self):
        messagebox.showinfo(
            APP_NAME,
            "StandUp Reminder\n\n"
            "- The sit timer runs; when it ends, a STAND UP message floats on\n"
            "  screen. After your standing break, a SIT DOWN message appears.\n"
            "- On the popup: click the words or press Esc to confirm (this starts\n"
            "  the next timer). Right-click or press D to skip a quote you dislike.\n"
            "- The timer pauses while you're locked, away, or in a call, and\n"
            "  restarts with STAND UP if you were away a long time.\n\n"
            "Settings: sit/stand times, startup delay, pauses, sound, transparency,\n"
            "auto-start, and Test-popup buttons.\n"
            "Quotes: add, delete, import (.txt one per line / .json), or export.\n\n"
            "Quotes & settings are stored in:\n" + CONFIG_DIR,
            parent=self.root)

    def on_close(self):
        self.save_config()
        self.root.destroy()


# --------------------------------------------------------------------------- #
# Auto-start on login (Windows, per-user, no admin rights required)
# --------------------------------------------------------------------------- #
def _startup_bat_path():
    appdata = os.environ.get("APPDATA", "")
    return os.path.join(appdata, "Microsoft", "Windows", "Start Menu",
                        "Programs", "Startup", "StandUpReminder.bat")


def set_autostart(enable):
    """Enable/disable launch-at-login by dropping a .bat in the Startup folder."""
    if platform.system() != "Windows":
        return False, "Auto-start is only wired up for Windows right now."
    bat = _startup_bat_path()
    try:
        if enable:
            script = os.path.abspath(__file__)
            pyw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
            launcher = pyw if os.path.exists(pyw) else sys.executable
            os.makedirs(os.path.dirname(bat), exist_ok=True)
            with open(bat, "w", encoding="utf-8") as fh:
                fh.write('@echo off\r\nstart "" "%s" "%s"\r\n' % (launcher, script))
            return True, "Auto-start enabled."
        else:
            if os.path.exists(bat):
                os.remove(bat)
            return True, "Auto-start disabled."
    except Exception as exc:
        return False, "Could not change auto-start: %s" % exc


# --------------------------------------------------------------------------- #
# "Am I actually at my desk and working?" detectors (Windows, stdlib only).
# Each returns False on non-Windows / on any error, so the timer never pauses
# by mistake.
# --------------------------------------------------------------------------- #
AWAY_IDLE_SECONDS = 120          # treat this much no-input as "away / screen asleep"


def _is_workstation_locked():
    """True when the session is locked (or on the secure desktop)."""
    if platform.system() != "Windows":
        return False
    try:
        import ctypes
        user32 = ctypes.windll.user32
        user32.OpenInputDesktop.restype = ctypes.c_void_p
        user32.OpenInputDesktop.argtypes = [ctypes.c_uint, ctypes.c_int, ctypes.c_uint]
        DESKTOP_SWITCHDESKTOP = 0x0100
        h = user32.OpenInputDesktop(0, False, DESKTOP_SWITCHDESKTOP)
        if not h:
            return True          # can't open the input desktop -> locked
        user32.CloseDesktop.argtypes = [ctypes.c_void_p]
        user32.CloseDesktop(h)
        return False
    except Exception:
        return False


def _idle_seconds():
    """Seconds since the last keyboard/mouse input."""
    if platform.system() != "Windows":
        return 0.0
    try:
        import ctypes

        class LII(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

        lii = LII()
        lii.cbSize = ctypes.sizeof(LII)
        if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
            kernel32 = ctypes.windll.kernel32
            kernel32.GetTickCount.restype = ctypes.c_uint32
            tick = kernel32.GetTickCount()
            return ((tick - lii.dwTime) & 0xFFFFFFFF) / 1000.0
    except Exception:
        pass
    return 0.0


def _scan_consent_key(key):
    """Recursively look for any app whose LastUsedTimeStop == 0 (in use NOW)."""
    i = 0
    while True:
        try:
            sub = winreg.EnumKey(key, i)
        except OSError:
            break
        i += 1
        try:
            with winreg.OpenKey(key, sub) as sk:
                if sub.lower() == "nonpackaged":
                    if _scan_consent_key(sk):
                        return True
                else:
                    try:
                        val, _ = winreg.QueryValueEx(sk, "LastUsedTimeStop")
                        if val == 0:
                            return True
                    except OSError:
                        pass
        except OSError:
            pass
    return False


def _capability_in_use(capability):
    """True if any app is currently using the given device (microphone/webcam)."""
    if not HAS_WINREG or platform.system() != "Windows":
        return False
    base = (r"SOFTWARE\Microsoft\Windows\CurrentVersion"
            r"\CapabilityAccessManager\ConsentStore" + "\\" + capability)
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, base) as key:
            return _scan_consent_key(key)
    except OSError:
        return False


def _in_call():
    """A meeting/call is on if the mic or camera is actively in use."""
    return _capability_in_use("microphone") or _capability_in_use("webcam")


# --------------------------------------------------------------------------- #
def main():
    root = tk.Tk()
    StandUpApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
