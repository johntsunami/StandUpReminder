#!/usr/bin/env python3
"""
StandUp Reminder -- desktop shortcut installer.

Run this ONCE on each computer (`python install.py`) to drop a clickable
"StandUp Reminder" icon on your Desktop so you can always start the app
yourself -- handy if auto-start is disabled on a managed/work machine.

Pure standard library: no pip installs. It tries three ways to create the
shortcut, falling back if a method is unavailable in a locked-down environment:
  1. Native Windows COM (IShellLink) via ctypes  -- best, real .lnk + icon.
  2. PowerShell WScript.Shell COM                 -- fallback.
  3. A plain .bat launcher copied to the Desktop  -- always works.
"""

import os
import sys
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "standup.py")
ICON = os.path.join(HERE, "standup.ico")
SHORTCUT_NAME = "StandUp Reminder"


def pythonw_path():
    """Prefer pythonw.exe (no console window); fall back to python.exe."""
    cand = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    return cand if os.path.exists(cand) else sys.executable


def desktop_dir():
    """Resolve the real Desktop folder (handles OneDrive redirection)."""
    try:
        import ctypes
        from ctypes import wintypes
        CSIDL_DESKTOPDIRECTORY = 0x10
        SHGFP_TYPE_CURRENT = 0
        buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(
            None, CSIDL_DESKTOPDIRECTORY, None, SHGFP_TYPE_CURRENT, buf)
        if buf.value and os.path.isdir(buf.value):
            return buf.value
    except Exception:
        pass
    return os.path.join(os.path.expanduser("~"), "Desktop")


def ensure_icon():
    if not os.path.exists(ICON):
        try:
            import make_icon
            make_icon.build_icon(ICON)
        except Exception:
            return None
    return ICON if os.path.exists(ICON) else None


# --------------------------------------------------------------------------- #
# Method 1: native COM via ctypes (no external tools required)
# --------------------------------------------------------------------------- #
def create_lnk_ctypes(lnk_path, target, args, workdir, icon):
    import ctypes
    from ctypes import POINTER, byref, c_void_p, c_wchar_p, c_int, HRESULT

    ole32 = ctypes.OleDLL("ole32")

    class GUID(ctypes.Structure):
        _fields_ = [("Data1", ctypes.c_ulong), ("Data2", ctypes.c_ushort),
                    ("Data3", ctypes.c_ushort), ("Data4", ctypes.c_ubyte * 8)]

    def guid(s):
        g = GUID()
        ole32.CLSIDFromString(c_wchar_p(s), byref(g))
        return g

    CLSID_ShellLink = "{00021401-0000-0000-C000-000000000046}"
    IID_IShellLinkW = "{000214F9-0000-0000-C000-000000000046}"
    IID_IPersistFile = "{0000010B-0000-0000-C000-000000000046}"
    CLSCTX_INPROC_SERVER = 1

    ole32.CoInitialize(None)
    try:
        ppv = c_void_p()
        hr = ole32.CoCreateInstance(byref(guid(CLSID_ShellLink)), None,
                                    CLSCTX_INPROC_SERVER,
                                    byref(guid(IID_IShellLinkW)), byref(ppv))
        if hr != 0 or not ppv.value:
            raise OSError("CoCreateInstance failed (0x%08x)" % (hr & 0xffffffff))

        def vtbl(this, count):
            addr = ctypes.cast(this, POINTER(c_void_p)).contents.value
            return ctypes.cast(addr, POINTER(c_void_p * count)).contents

        sl = vtbl(ppv, 21)

        def call(fn_addr, *types):
            return ctypes.WINFUNCTYPE(HRESULT, c_void_p, *types)(fn_addr)

        call(sl[20], c_wchar_p)(ppv, target)                 # SetPath
        if args:
            call(sl[11], c_wchar_p)(ppv, args)               # SetArguments
        if workdir:
            call(sl[9], c_wchar_p)(ppv, workdir)             # SetWorkingDirectory
        call(sl[7], c_wchar_p)(ppv, "Stand up / sit down reminder")  # SetDescription
        if icon:
            call(sl[17], c_wchar_p, c_int)(ppv, icon, 0)     # SetIconLocation

        # QueryInterface for IPersistFile, then Save.
        ppf = c_void_p()
        call(sl[0], c_void_p, POINTER(c_void_p))(ppv, byref(guid(IID_IPersistFile)),
                                                 byref(ppf))
        pf = vtbl(ppf, 7)
        hr = call(pf[6], c_wchar_p, c_int)(ppf, lnk_path, 1)  # Save(path, remember)
        if hr != 0:
            raise OSError("IPersistFile.Save failed (0x%08x)" % (hr & 0xffffffff))

        # Release.
        call(pf[2])(ppf)
        call(sl[2])(ppv)
    finally:
        ole32.CoUninitialize()
    return os.path.exists(lnk_path)


# --------------------------------------------------------------------------- #
# Method 2: PowerShell WScript.Shell COM
# --------------------------------------------------------------------------- #
def create_lnk_powershell(lnk_path, target, args, workdir, icon):
    ps = (
        "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%s');"
        "$s.TargetPath='%s';$s.Arguments='%s';$s.WorkingDirectory='%s';"
        "%s$s.Description='StandUp Reminder';$s.Save()"
    ) % (
        lnk_path, target, args, workdir,
        ("$s.IconLocation='%s';" % icon) if icon else "",
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
        check=True, capture_output=True, timeout=30)
    return os.path.exists(lnk_path)


# --------------------------------------------------------------------------- #
# Method 3: a plain .bat launcher on the Desktop (always works)
# --------------------------------------------------------------------------- #
def create_bat(desktop, target, script, workdir):
    bat = os.path.join(desktop, SHORTCUT_NAME + ".bat")
    with open(bat, "w", encoding="utf-8") as fh:
        fh.write('@echo off\r\ncd /d "%s"\r\nstart "" "%s" "%s"\r\n'
                 % (workdir, target, script))
    return bat


def main():
    if sys.platform != "win32":
        print("This installer creates a Windows desktop shortcut. On macOS/Linux,"
              " just run:  python standup.py")
        return 1

    if not os.path.exists(SCRIPT):
        print("ERROR: standup.py not found next to install.py.")
        return 1

    target = pythonw_path()
    args = '"%s"' % SCRIPT
    workdir = HERE
    icon = ensure_icon()
    desktop = desktop_dir()
    lnk = os.path.join(desktop, SHORTCUT_NAME + ".lnk")

    for name, fn in (("native COM", lambda: create_lnk_ctypes(lnk, target, args, workdir, icon)),
                     ("PowerShell", lambda: create_lnk_powershell(lnk, target, args, workdir, icon))):
        try:
            if fn():
                print("Created desktop shortcut via %s:\n  %s" % (name, lnk))
                return 0
        except Exception as exc:
            print("(%s method unavailable: %s)" % (name, exc))

    bat = create_bat(desktop, target, SCRIPT, workdir)
    print("Created a launcher on your Desktop:\n  %s" % bat)
    print("(Could not make a .lnk with a custom icon; the .bat works the same way.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
