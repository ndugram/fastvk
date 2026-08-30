from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

from .__meta__ import __version__

_MAIN_TEMPLATE = '''\
from fastvk import FastVK
from fastvk.filters import Command
from fastvk.types import Message

bot = FastVK(token="{token}")


@bot.message(Command("start"))
async def start(message: Message) -> None:
    await message.answer("Привет! Я FastVK бот.")


@bot.message()
async def echo(message: Message) -> None:
    await message.answer(message.text)


if __name__ == "__main__":
    bot.run_polling()
'''

_ENV_TEMPLATE = "VK_TOKEN=vk1.a.CHANGE_ME\n"

_GITIGNORE = "__pycache__/\n*.pyc\n.env\n.venv/\nbot.db\n"

_README = """\
# {name}

A VK bot built with [FastVK](https://github.com/ndugram/fastvk).

## Run

```bash
pip install fastvk
python -m {name}.main   # or: fastvk run {name}.main
```
"""


def _cmd_new(args: argparse.Namespace) -> int:
    target = Path(args.name)
    if target.exists() and any(target.iterdir()):
        print(f"error: {target}/ already exists and is not empty", file=sys.stderr)
        return 1
    pkg = target / target.name if args.package else target
    pkg.mkdir(parents=True, exist_ok=True)

    token = "vk1.a.YOUR_TOKEN"
    (pkg / "main.py").write_text(_MAIN_TEMPLATE.format(token=token), "utf-8")
    if args.package:
        (pkg / "__init__.py").write_text("", "utf-8")
    (target / ".env.example").write_text(_ENV_TEMPLATE, "utf-8")
    (target / ".gitignore").write_text(_GITIGNORE, "utf-8")
    (target / "README.md").write_text(_README.format(name=target.name), "utf-8")

    print(f"Created {target}/")
    entry = f"{target.name}.main" if args.package else str(pkg / "main.py")
    print(f"Next:\n  cd {target}\n  fastvk run {entry}")
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    from .app import FastVK

    sys.path.insert(0, str(Path.cwd()))
    spec = args.target
    if spec.endswith(".py"):
        spec = spec[:-3].replace("/", ".").replace("\\", ".")

    module_name, _, attr = spec.partition(":")
    module = importlib.import_module(module_name)

    app: FastVK | None = None
    if attr:
        app = getattr(module, attr, None)
    else:
        for value in vars(module).values():
            if isinstance(value, FastVK):
                app = value
                break
    if app is None:
        print(
            f"error: no FastVK instance found in {module_name!r} "
            f"(use module:attr to point at one)",
            file=sys.stderr,
        )
        return 1

    if args.webhook:
        host, _, port = args.webhook.partition(":")
        app.run_webhook(
            confirmation_token=args.confirmation or "",
            host=host or "0.0.0.0",
            port=int(port or 8080),
            path=args.path,
        )
    else:
        app.run_polling()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fastvk", description="FastVK command line")
    parser.add_argument("-V", "--version", action="version", version=f"fastvk {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new", help="scaffold a new bot project")
    p_new.add_argument("name", help="project directory name")
    p_new.add_argument(
        "--package",
        action="store_true",
        help="create an importable package (name/name/main.py)",
    )
    p_new.set_defaults(func=_cmd_new)

    p_run = sub.add_parser("run", help="run a bot module")
    p_run.add_argument("target", help="module path or module:attr or path/to/main.py")
    p_run.add_argument("--webhook", metavar="HOST:PORT", help="run in webhook mode")
    p_run.add_argument("--confirmation", help="webhook confirmation token")
    p_run.add_argument("--path", default="/", help="webhook path (default: /)")
    p_run.set_defaults(func=_cmd_run)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())
