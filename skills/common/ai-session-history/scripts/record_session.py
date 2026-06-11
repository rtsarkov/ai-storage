#!/usr/bin/env python3
"""Create or update a compact AI session history entry."""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
from pathlib import Path


ROOT = Path(".aisessions")
SESSIONS_DIR = ROOT / "sessions"
INDEX_FILE = ROOT / "sessions.json"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def normalize_hash(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("session hash is empty")
    normalized = re.sub(r"[^A-Za-z0-9_.-]+", "-", value)
    return normalized[:128]


def generate_hash(description: str) -> str:
    raw = "|".join([os.getcwd(), utc_now(), description])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def load_index() -> list:
    if not INDEX_FILE.exists():
        return []
    with INDEX_FILE.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("sessions"), list):
        return data["sessions"]
    raise ValueError(f"Unsupported index format: {INDEX_FILE}")


def save_index(entries: list) -> None:
    with INDEX_FILE.open("w", encoding="utf-8") as fh:
        json.dump(entries, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def list_block(items: list, fallback: str) -> list:
    values = [item.strip() for item in items if item.strip()]
    if not values:
        values = [fallback]

    return [f"- {item}" for item in values]


def default_summary(
    session_hash: str,
    description: str,
    status: str,
    touched_areas: list,
    key_decisions: list,
    checks: list,
    next_steps: list,
) -> str:
    lines = [
        f"# Сессия {session_hash}",
        "",
        "## Описание",
        description,
        "",
        "## Что делали",
        "- Краткая карточка сессии создана для восстановления контекста.",
        "",
        "## Ключевые решения",
    ]
    lines.extend(list_block(key_decisions, "Не указано."))
    lines.extend(["", "## Затронутые области"])
    lines.extend(list_block(touched_areas, "Не указано."))
    lines.extend(["", "## Проверки"])
    lines.extend(list_block(checks, "Не выполнялись."))
    lines.extend(["", "## Что продолжить"])
    lines.extend(list_block(next_steps, "Не требуется."))
    lines.extend(["", "## Статус", status, ""])
    return "\n".join(lines)


def unique(values: list) -> list:
    result = []
    seen = set()

    for value in values:
        item = value.strip()
        if not item or item in seen:
            continue
        seen.add(item)
        result.append(item)

    return result


def merge_list(existing: dict, key: str, values: list) -> list:
    return unique(list(existing.get(key, [])) + values)


def normalize_status(value: str) -> str:
    status = value.strip() if value else "done"
    allowed = {"done", "partial", "blocked", "needs-check"}
    return status if status in allowed else "partial"


def find_entry(entries: list, session_hash: str) -> dict:
    for entry in entries:
        if entry.get("session_hash") == session_hash:
            return entry

    return {}


def restore_session(session_hash: str) -> int:
    normalized_hash = normalize_hash(session_hash)

    if not INDEX_FILE.exists():
        print(
            json.dumps(
                {
                    "status": "not_found",
                    "session_hash": normalized_hash,
                    "index_file": str(INDEX_FILE),
                    "message": "Session index file does not exist.",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    entries = load_index()
    entry = find_entry(entries, normalized_hash)

    if not entry:
        print(
            json.dumps(
                {
                    "status": "not_found",
                    "session_hash": normalized_hash,
                    "index_file": str(INDEX_FILE),
                    "message": "Session hash not found.",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    summary_file = Path(entry.get("summary_file", ""))
    if not summary_file.exists():
        print(
            json.dumps(
                {
                    "status": "missing_summary",
                    "session_hash": normalized_hash,
                    "index_file": str(INDEX_FILE),
                    "summary_file": str(summary_file),
                    "entry": entry,
                    "message": "Session index entry exists, but summary file is missing.",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    print(
        json.dumps(
            {
                "status": "restored",
                "session_hash": normalized_hash,
                "index_file": str(INDEX_FILE),
                "summary_file": str(summary_file),
                "entry": entry,
                "summary": summary_file.read_text(encoding="utf-8"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record an AI session history entry.")
    parser.add_argument("--restore", dest="restore_hash", default="")
    parser.add_argument("--hash", dest="session_hash", default="")
    parser.add_argument("--description", default="")
    parser.add_argument("--summary", default="")
    parser.add_argument("--status", default="done")
    parser.add_argument("--tag", dest="tags", action="append", default=[])
    parser.add_argument("--touched", dest="touched_areas", action="append", default=[])
    parser.add_argument("--decision", dest="key_decisions", action="append", default=[])
    parser.add_argument("--check", dest="checks", action="append", default=[])
    parser.add_argument("--next", dest="next_steps", action="append", default=[])
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.restore_hash:
        return restore_session(args.restore_hash)

    if not args.description:
        raise ValueError("--description is required when not using --restore")

    ROOT.mkdir(exist_ok=True)
    SESSIONS_DIR.mkdir(exist_ok=True)

    session_hash = normalize_hash(args.session_hash) if args.session_hash else generate_hash(args.description)
    summary_path = SESSIONS_DIR / f"{session_hash}.md"
    now = utc_now()
    entries = load_index()
    status_value = normalize_status(args.status)
    tags = unique(args.tags)
    touched_areas = unique(args.touched_areas)
    key_decisions = unique(args.key_decisions)
    checks = unique(args.checks)
    next_steps = unique(args.next_steps)

    existing = None
    for entry in entries:
        if entry.get("session_hash") == session_hash:
            existing = entry
            break

    summary = args.summary.strip() or default_summary(
        session_hash,
        args.description,
        status_value,
        touched_areas,
        key_decisions,
        checks,
        next_steps,
    )
    summary_path.write_text(summary.rstrip() + "\n", encoding="utf-8")

    if existing:
        existing["description"] = args.description
        existing["summary_file"] = str(summary_path)
        existing["status"] = status_value
        existing["tags"] = merge_list(existing, "tags", tags)
        existing["touched_areas"] = merge_list(existing, "touched_areas", touched_areas)
        existing["key_decisions"] = merge_list(existing, "key_decisions", key_decisions)
        existing["checks"] = merge_list(existing, "checks", checks)
        existing["next_steps"] = merge_list(existing, "next_steps", next_steps)
        existing["updated_at"] = now
        status = "exists"
    else:
        entries.append(
            {
                "session_hash": session_hash,
                "description": args.description,
                "summary_file": str(summary_path),
                "status": status_value,
                "tags": tags,
                "touched_areas": touched_areas,
                "key_decisions": key_decisions,
                "checks": checks,
                "next_steps": next_steps,
                "created_at": now,
                "updated_at": now,
            }
        )
        status = "created"

    save_index(entries)

    print(
        json.dumps(
            {
                "status": status,
                "session_hash": session_hash,
                "index_file": str(INDEX_FILE),
                "summary_file": str(summary_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
