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
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

# winsound is Windows-only and part of the stdlib; degrade gracefully elsewhere.
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False


# --------------------------------------------------------------------------- #
# Paths & configuration
# --------------------------------------------------------------------------- #
APP_NAME = "StandUp Reminder"
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".standup_reminder")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
STAND_FILE = os.path.join(CONFIG_DIR, "stand_quotes.json")
SIT_FILE = os.path.join(CONFIG_DIR, "sit_quotes.json")

DEFAULT_CONFIG = {
    "sit_minutes": 45,        # how long you sit before STAND UP fires
    "stand_minutes": 5,       # how long you stand before SIT DOWN fires
    "snooze_minutes": 5,      # snooze button duration
    "sound_enabled": True,    # play a chime when a popup fires
    "transparency": 0.90,     # popup opacity 0.5 (very see-through) - 1.0 (solid)
    "autostart": False,       # launch automatically when Windows starts
    "stay_on_top": False,     # keep the little control window above others
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

        self.stand_quotes = _read_json(STAND_FILE, None) or list(DEFAULT_STAND_QUOTES)
        self.sit_quotes = _read_json(SIT_FILE, None) or list(DEFAULT_SIT_QUOTES)
        if not os.path.exists(STAND_FILE):
            _write_json(STAND_FILE, self.stand_quotes)
        if not os.path.exists(SIT_FILE):
            _write_json(SIT_FILE, self.sit_quotes)

        # --- timer state ----------------------------------------------------
        self.mode = "sit"                       # current posture: "sit" or "stand"
        self.remaining = self.duration_for("sit")
        self.running = True                     # is the countdown active?
        self.popup_open = False                 # paused while a popup is showing
        self.pending_mode = None                # mode to switch to after popup
        self.active_popup = None

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
        self.root.geometry("300x150")
        self.root.minsize(280, 140)
        self.root.configure(bg="#1e1e2e")

        # Menu bar
        menubar = tk.Menu(self.root)
        menubar.add_command(label="Settings", command=self.open_settings)
        menubar.add_command(label="Quotes", command=self.open_quotes_manager)
        menubar.add_command(label="Help", command=self.show_help)
        self.root.config(menu=menubar)

        wrap = tk.Frame(self.root, bg="#1e1e2e")
        wrap.pack(fill="both", expand=True, padx=12, pady=10)

        self.status_var = tk.StringVar()
        self.stats_var = tk.StringVar()

        tk.Label(wrap, textvariable=self.status_var, font=("Segoe UI", 15, "bold"),
                 fg="#cdd6f4", bg="#1e1e2e").pack(pady=(8, 10))

        btns = tk.Frame(wrap, bg="#1e1e2e")
        btns.pack()
        self.start_btn = tk.Button(btns, text="Pause", width=8, command=self.toggle_running)
        self.start_btn.grid(row=0, column=0, padx=3)
        tk.Button(btns, text="Reset", width=8, command=self.reset).grid(row=0, column=1, padx=3)
        tk.Button(btns, text="Skip", width=8, command=self.skip).grid(row=0, column=2, padx=3)

        tk.Label(wrap, textvariable=self.stats_var, font=("Segoe UI", 9),
                 fg="#9399b2", bg="#1e1e2e").pack(pady=(8, 0))

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self._refresh_display()

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

    def _tick(self):
        # The timer is frozen while a popup is showing, so nothing stacks up or
        # keeps firing if you've stepped away -- exactly one popup waits for you.
        if self.running and not self.popup_open and not self._popup_alive():
            self.remaining -= 1
            if self.remaining <= 0:
                nxt = "stand" if self.mode == "sit" else "sit"
                self._fire_transition(nxt)
        self._refresh_display()
        self.root.after(1000, self._tick)

    def _refresh_display(self):
        # No countdown is shown on purpose -- just the current posture.
        self.status_var.set("Standing" if self.mode == "stand" else "Sitting")
        self.start_btn.config(text="Start" if not self.running else "Pause")
        self.stats_var.set("Stand breaks today: %d" % self.config["stats"].get("stands", 0))

    # ----------------------------------------------------------- controls
    def toggle_running(self):
        self.running = not self.running
        self._refresh_display()

    def reset(self):
        self.mode = "sit"
        self.remaining = self.duration_for("sit")
        self.running = True
        self._refresh_display()

    def skip(self):
        """Immediately fire the next transition (handy for testing)."""
        if self.popup_open:
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

    # ----------------------------------------------------------- settings
    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.configure(bg="#1e1e2e")
        win.resizable(False, False)
        win.transient(self.root)

        pad = {"padx": 10, "pady": 6}
        sit_v = tk.IntVar(value=self.config["sit_minutes"])
        stand_v = tk.IntVar(value=self.config["stand_minutes"])
        snooze_v = tk.IntVar(value=self.config["snooze_minutes"])
        sound_v = tk.BooleanVar(value=self.config["sound_enabled"])
        topmost_v = tk.BooleanVar(value=self.config["stay_on_top"])
        auto_v = tk.BooleanVar(value=self.config["autostart"])
        trans_v = tk.DoubleVar(value=self.config["transparency"])

        def row(r, text, widget):
            tk.Label(win, text=text, fg="#cdd6f4", bg="#1e1e2e",
                     font=("Segoe UI", 10)).grid(row=r, column=0, sticky="w", **pad)
            widget.grid(row=r, column=1, sticky="w", **pad)

        row(0, "Sit time before STAND UP (min)",
            tk.Spinbox(win, from_=1, to=240, textvariable=sit_v, width=6))
        row(1, "Stand time before SIT DOWN (min)",
            tk.Spinbox(win, from_=1, to=120, textvariable=stand_v, width=6))
        row(2, "Snooze length (min)",
            tk.Spinbox(win, from_=1, to=60, textvariable=snooze_v, width=6))
        row(3, "Popup transparency",
            tk.Scale(win, from_=0.5, to=1.0, resolution=0.05, orient="horizontal",
                     variable=trans_v, length=150, bg="#1e1e2e", fg="#cdd6f4",
                     highlightthickness=0))
        row(4, "Play sound on popup",
            tk.Checkbutton(win, variable=sound_v, bg="#1e1e2e",
                           activebackground="#1e1e2e"))
        row(5, "Keep control window on top",
            tk.Checkbutton(win, variable=topmost_v, bg="#1e1e2e",
                           activebackground="#1e1e2e"))
        row(6, "Start automatically at login",
            tk.Checkbutton(win, variable=auto_v, bg="#1e1e2e",
                           activebackground="#1e1e2e"))

        def save():
            self.config["sit_minutes"] = max(1, int(sit_v.get()))
            self.config["stand_minutes"] = max(1, int(stand_v.get()))
            self.config["snooze_minutes"] = max(1, int(snooze_v.get()))
            self.config["sound_enabled"] = bool(sound_v.get())
            self.config["stay_on_top"] = bool(topmost_v.get())
            self.config["transparency"] = float(trans_v.get())

            want_auto = bool(auto_v.get())
            if want_auto != self.config["autostart"]:
                ok, msg = set_autostart(want_auto)
                if ok:
                    self.config["autostart"] = want_auto
                else:
                    messagebox.showwarning(APP_NAME, msg, parent=win)

            self.save_config()
            self._apply_stay_on_top()
            # Apply new durations to the current cycle immediately.
            self.remaining = min(self.remaining, self.duration_for(self.mode))
            self._refresh_display()
            win.destroy()

        # --- live preview: press as many times as you like to test popups ----
        test = tk.Frame(win, bg="#1e1e2e")
        test.grid(row=7, column=0, columnspan=2, pady=(12, 0))
        tk.Label(test, text="Test popup:", fg="#cdd6f4", bg="#1e1e2e",
                 font=("Segoe UI", 10)).pack(side="left", padx=(0, 8))
        tk.Button(test, text="STAND UP", width=11,
                  command=lambda: self._show_popup("stand", preview=True)).pack(side="left", padx=3)
        tk.Button(test, text="SIT DOWN", width=11,
                  command=lambda: self._show_popup("sit", preview=True)).pack(side="left", padx=3)

        tk.Button(win, text="Save", width=12, command=save).grid(
            row=8, column=0, columnspan=2, pady=12)

    # ----------------------------------------------------------- quotes mgr
    def open_quotes_manager(self):
        win = tk.Toplevel(self.root)
        win.title("Quote Manager")
        win.configure(bg="#1e1e2e")
        win.geometry("560x440")
        win.transient(self.root)

        top_bar = tk.Frame(win, bg="#1e1e2e")
        top_bar.pack(fill="x", padx=10, pady=8)
        tk.Label(top_bar, text="Editing:", fg="#cdd6f4", bg="#1e1e2e",
                 font=("Segoe UI", 10)).pack(side="left")
        which = tk.StringVar(value="STAND UP quotes")
        combo = ttk.Combobox(top_bar, textvariable=which, state="readonly", width=20,
                             values=["STAND UP quotes", "SIT DOWN quotes"])
        combo.pack(side="left", padx=8)

        count_var = tk.StringVar()
        tk.Label(top_bar, textvariable=count_var, fg="#9399b2", bg="#1e1e2e",
                 font=("Segoe UI", 9)).pack(side="right")

        list_frame = tk.Frame(win, bg="#1e1e2e")
        list_frame.pack(fill="both", expand=True, padx=10)
        scroll = tk.Scrollbar(list_frame)
        scroll.pack(side="right", fill="y")
        lb = tk.Listbox(list_frame, yscrollcommand=scroll.set, font=("Segoe UI", 10),
                        bg="#11111b", fg="#cdd6f4", selectbackground="#585b70",
                        activestyle="none")
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

        btns = tk.Frame(win, bg="#1e1e2e")
        btns.pack(fill="x", padx=10, pady=10)
        for txt, cmd in [("Add", add_quote), ("Delete", delete_selected),
                         ("Import", import_quotes), ("Export", export_quotes),
                         ("Restore defaults", restore_defaults)]:
            tk.Button(btns, text=txt, command=cmd, width=14).pack(side="left", padx=3)

        combo.bind("<<ComboboxSelected>>", lambda e: reload_list())
        reload_list()

    # ----------------------------------------------------------- help/about
    def show_help(self):
        messagebox.showinfo(
            APP_NAME,
            "StandUp Reminder\n\n"
            "- Sit timer counts down; when it hits zero a STAND UP popup appears.\n"
            "- After your standing break, a SIT DOWN popup appears.\n"
            "- Click 'I'm Standing/Sitting' to start the next phase, or Snooze.\n"
            "- 'Delete quote' removes the shown line; 'New quote' shuffles it.\n\n"
            "Settings: adjust sit/stand/snooze times, sound, transparency, autostart.\n"
            "Quotes: add, delete, import (.txt one per line), or export your own.\n\n"
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
def main():
    root = tk.Tk()
    StandUpApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
