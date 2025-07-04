import logging
import os
import sys
import subprocess
import shutil
from selenium.webdriver.remote.webdriver import WebDriver

DEFAULTS = {
    "browser_width_px":    1750,
    "browser_height_px":   950,
    "browser_pos_x":       0,
    "browser_pos_y":       0,
    "tricoma_zoom_pct":    100,
    "term_width_px":       640,
    "term_height_px":      480,
    "term_pos_x":          1750,
    "term_pos_y":          0
}


def _resize_and_position_terminal(px_w: int, px_h: int,
                                  pos_x: int, pos_y: int) -> None:
    """
    Sets the position and size of the physical terminal window.
    Supports Windows (WinAPI), macOS (AppleScript), and Linux/X11 (wmctrl).
    """
    try:
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            buf = ctypes.create_unicode_buffer(512)
            kernel32.GetConsoleTitleW(buf, ctypes.sizeof(buf))
            target = buf.value
            EnumWindows = user32.EnumWindows
            EnumProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
            GetText = user32.GetWindowTextW
            GetLen = user32.GetWindowTextLengthW
            IsVis = user32.IsWindowVisible
            hwnds = []
            def enum_win(hwnd, lparam):
                if not IsVis(hwnd): return True
                length = GetLen(hwnd)
                if length == 0: return True
                buf2 = ctypes.create_unicode_buffer(length+1)
                GetText(hwnd, buf2, length+1)
                if buf2.value == target:
                    hwnds.append(hwnd)
                    return False
                return True
            EnumWindows(EnumProc(enum_win), 0)
            hwnd = hwnds[0] if hwnds else kernel32.GetConsoleWindow()
            if hwnd:
                user32.MoveWindow(hwnd, pos_x, pos_y, px_w, px_h, True)
                logging.info("Terminal set to %dx%d @(%d,%d)", px_w, px_h, pos_x, pos_y)
            else:
                logging.warning("Terminal window not found.")
        elif sys.platform == "darwin":
            applescript = (
                'tell application "System Events" to tell (first process whose frontmost is true) '
                f'set position of front window to {{{pos_x}, {pos_y}}} '
                f'set size of front window to {{{px_w}, {px_h}}}'
            )
            subprocess.run(["osascript", "-e", applescript], check=False)
        else:
            if shutil.which("wmctrl"):
                geom = f"0,{pos_x},{pos_y},{px_w},{px_h}"
                subprocess.run(["wmctrl", "-r", ":ACTIVE:", "-e", geom], check=False)
            else:
                logging.warning("wmctrl not found – terminal not adjusted.")
    except Exception as e:
        logging.warning("Error adjusting terminal window: %s", e)


def setup_layout(driver: WebDriver, cfg: dict | None = None) -> None:
    """
    Configures browser and terminal windows according to values in config.json.
    """
    cfg = {**DEFAULTS, **(cfg or {})}

    bw = cfg.get("browser_width_px")
    bh = cfg.get("browser_height_px")
    bx = cfg.get("browser_pos_x")
    by = cfg.get("browser_pos_y")
    driver.set_window_position(bx, by)
    driver.set_window_size(bw, bh)
    logging.info("Browser set to %dx%d @(%d,%d)", bw, bh, bx, by)

    zoom_pct = cfg.get("tricoma_zoom_pct", 100)
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        try:
            url = driver.current_url
        except Exception:
            url = ""
        if "tricoma" in url:
            driver.execute_script("document.body.style.zoom = arguments[0] + '%';", zoom_pct)
            logging.info("Applied Tricoma zoom: %s%% (URL: %s)", zoom_pct, url)
            break
    driver.switch_to.window(driver.window_handles[0])

    tw = cfg.get("term_width_px")
    th = cfg.get("term_height_px")
    tx = cfg.get("term_pos_x")
    ty = cfg.get("term_pos_y")
    _resize_and_position_terminal(tw, th, tx, ty)
