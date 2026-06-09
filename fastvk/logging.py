from __future__ import annotations

import logging
import os
import sys


R = "\033[0m"
BOLD = "\033[1m"
DIM  = "\033[2m"

_FG = {
    "black":   "\033[30m", "red":     "\033[31m", "green":  "\033[32m",
    "yellow":  "\033[33m", "blue":    "\033[34m", "magenta":"\033[35m",
    "cyan":    "\033[36m", "white":   "\033[37m",
    "br_black":"\033[90m", "br_red":  "\033[91m", "br_green":"\033[92m",
    "br_yellow":"\033[93m","br_blue": "\033[94m", "br_magenta":"\033[95m",
    "br_cyan": "\033[96m", "br_white":"\033[97m",
    "teal":    "\033[38;5;30m",
}

def _c(code: str, text: str) -> str:
    return f"{code}{text}{R}"

def _supports_color() -> bool:
    if os.environ.get("NO_COLOR") or os.environ.get("FASTVK_NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    stream = sys.stderr
    return hasattr(stream, "isatty") and stream.isatty()



_LEVELS: dict[int, tuple[str, str]] = {
    logging.DEBUG:    ("DEBUG   ", _FG["br_cyan"]),
    logging.INFO:     ("INFO    ", _FG["br_green"]),
    logging.WARNING:  ("WARNING ", _FG["br_yellow"]),
    logging.ERROR:    ("ERROR   ", _FG["br_red"]),
    logging.CRITICAL: ("CRITICAL", BOLD + _FG["br_red"]),
}


_LOGGER_COLORS: dict[str, str] = {
    "fastvk":            _FG["teal"],
    "fastvk.polling":    _FG["br_cyan"],
    "fastvk.webhook":    _FG["br_magenta"],
    "fastvk.dashboard":  _FG["br_blue"],
    "fastvk.router":     _FG["br_cyan"],
    "fastvk.middleware": _FG["br_yellow"],
    "fastvk.fsm":        _FG["br_cyan"],
}


_EVT_COLORS: dict[str, str] = {
    "message_new":   _FG["br_blue"],
    "message_event": _FG["br_green"],
    "group_join":    _FG["br_magenta"],
    "group_leave":   _FG["br_yellow"],
    "wall_post_new": _FG["br_cyan"],
}


def _color_message(msg: str, colored: bool) -> str:
    if not colored:
        return msg

    if msg.startswith("← "):
        parts = msg[2:].split(None, 1)
        evt = parts[0]
        rest = "  " + parts[1] if len(parts) > 1 else ""
        c = _EVT_COLORS.get(evt, _FG["br_white"])
        arrow = _c(_FG["br_black"], "←")
        return f"{arrow} {_c(c, evt)}{_c(DIM, rest) if rest else ''}"
    return msg


class ColorFormatter(logging.Formatter):
    """
    Colored log formatter for fastvk.

    Output (color terminal):

        10:35:42  INFO     fastvk  ← message_new
        10:35:42  WARNING  fastvk  some warning

    Falls back to plain text when NO_COLOR is set or stdout is not a tty.
    """

    def __init__(self) -> None:
        super().__init__()
        self._colored = _supports_color()

    def format(self, record: logging.LogRecord) -> str:
        ts = self.formatTime(record, "%H:%M:%S")
        lvl_str, lvl_color = _LEVELS.get(record.levelno, ("?" * 8, ""))
        name = record.name
        msg = record.getMessage()

        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        if self._colored:
            ts_s   = _c(DIM, ts)
            lvl_s  = _c(lvl_color, lvl_str)
            name_c = _LOGGER_COLORS.get(name, _FG["br_white"])
            name_s = _c(name_c, f"{name:<22}")
            msg_s  = _color_message(msg, colored=True)
            line   = f"{ts_s}  {lvl_s}  {name_s}  {msg_s}"
        else:
            line = f"{ts}  {lvl_str}  {name:<22}  {msg}"

        if record.exc_text:
            exc = record.exc_text
            if self._colored:
                exc = _c(_FG["br_red"], exc)
            line = f"{line}\n{exc}"

        return line


def setup_logging(level: int = logging.INFO) -> None:
    """
    Install ColorFormatter on the root logger.
    Call once before ``run_polling()`` / ``run_webhook()`` if you want
    full control over log level or format.

    Example::

        from fastvk.logging import setup_logging
        setup_logging()
    """
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(ColorFormatter())
    root = logging.getLogger()
    root.setLevel(level)
    if not root.handlers:
        root.addHandler(handler)
    else:


        root.handlers = [handler]
