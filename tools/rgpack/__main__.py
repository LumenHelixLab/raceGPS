"""CLI: python -m rgpack export-overpass | validate

Workshop writer only. Race must not call Overpass.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow `python -m rgpack` when tools/ is on sys.path or cwd is tools/.
_TOOLS = Path(__file__).resolve().parents[1]
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from rgpack.io import validate_pack_dir  # noqa: E402
from rgpack.overpass_export import (  # noqa: E402
    export_overpass_to_pack,
    fetch_overpass_bbox,
    load_overpass_json,
)
from rgpack.schema import RgpackValidationError  # noqa: E402


def _default_fixture() -> Path:
    root = Path(__file__).resolve().parents[2]
    return root / "tests" / "fixtures" / "rgpack" / "overpass_burke_tiny" / "overpass.json"


def _parse_bbox_csv(raw: str) -> list[float]:
    # Leading '-' in CSV confuses argparse unless passed as --bbox=...; still parse here.
    parts = [float(x.strip()) for x in raw.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("bbox needs west,south,east,north")
    return parts


def cmd_export(args: argparse.Namespace) -> int:
    bbox = None
    retrieved_note = None
    try:
        if args.fixture is not None:
            src = Path(args.fixture) if args.fixture is not True else _default_fixture()
            if not src.is_file():
                print(f"FAIL  offline fixture missing: {src}", file=sys.stderr)
                return 1
            overpass = load_overpass_json(src)
            attribution = (
                "© OpenStreetMap contributors (offline fixture overpass_burke_tiny)"
            )
            retrieved_note = "offline-fixture"
            print(f"INPUT  offline fixture: {src}")
        elif args.input:
            src = Path(args.input)
            overpass = load_overpass_json(src)
            attribution = "© OpenStreetMap contributors (Overpass JSON file)"
            retrieved_note = f"file:{src.name}"
            print(f"INPUT  overpass json: {src}")
        elif args.west is not None:
            west, south, east, north = args.west, args.south, args.east, args.north
            if None in (south, east, north):
                print(
                    "FAIL  live mode needs --west --south --east --north",
                    file=sys.stderr,
                )
                return 2
            bbox = [west, south, east, north]
            print(f"INPUT  live Overpass bbox={bbox} (tiny; fail-closed on network)")
            overpass = fetch_overpass_bbox(
                west, south, east, north, timeout_s=args.timeout
            )
            attribution = "© OpenStreetMap contributors (Overpass API)"
            retrieved_note = "live-overpass"
        elif args.bbox:
            west, south, east, north = args.bbox
            bbox = [west, south, east, north]
            print(f"INPUT  live Overpass bbox={bbox} (tiny; fail-closed on network)")
            overpass = fetch_overpass_bbox(
                west, south, east, north, timeout_s=args.timeout
            )
            attribution = "© OpenStreetMap contributors (Overpass API)"
            retrieved_note = "live-overpass"
        else:
            print(
                "FAIL  provide --fixture, --input PATH, or live bbox "
                "(--west/--south/--east/--north or --bbox=w,s,e,n)",
                file=sys.stderr,
            )
            return 2

        n_el = len(overpass.get("elements") or [])
        print(f"ELEMENTS  {n_el}")
        out = Path(args.out)
        pack_id = args.pack_id
        display = args.display_name or pack_id
        notes = (
            "Workshop Overpass→rgpack export proof; provisional. "
            "Not a citypack XODR adapter. Race must not call Overpass."
        )
        if retrieved_note:
            notes = f"{notes} source={retrieved_note}"

        m = export_overpass_to_pack(
            overpass,
            out,
            pack_id=pack_id,
            display_name=display,
            attribution=attribution,
            bbox=bbox,
            certification_notes=notes,
            environment_preset=args.preset,
        )
        ok = validate_pack_dir(out)
        print(f"PACK    {out.resolve()}")
        print(f"packId  {m.pack_id}")
        print(f"hash    {m.content_hash}")
        print(f"RESULT  {'PASS' if ok else 'FAIL'}")
        return 0 if ok else 1
    except RgpackValidationError as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 1
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 1


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        ok = validate_pack_dir(Path(args.pack_dir))
        from rgpack.io import load_pack

        m = load_pack(Path(args.pack_dir))
        print(f"PACK    {Path(args.pack_dir).resolve()}")
        print(f"packId  {m.pack_id}")
        print(f"hash    {m.content_hash}")
        print(f"RESULT  {'PASS' if ok else 'FAIL'}")
        return 0 if ok else 1
    except RgpackValidationError as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="python -m rgpack",
        description="rgpack v1 Workshop tools (Overpass→rgpack export + validate)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser(
        "export-overpass", help="Overpass JSON / fixture / tiny bbox → rgpack"
    )
    e.add_argument(
        "--fixture",
        nargs="?",
        const=True,
        default=None,
        help="Use offline Burke tiny fixture (or PATH to one)",
    )
    e.add_argument("--input", "-i", help="Overpass JSON file path")
    e.add_argument(
        "--bbox",
        type=_parse_bbox_csv,
        default=None,
        help="Live Overpass CSV west,south,east,north — pass as --bbox=w,s,e,n "
        "(leading minus breaks space-separated form)",
    )
    e.add_argument("--west", type=float, default=None, help="Live Overpass west lon")
    e.add_argument("--south", type=float, default=None, help="Live Overpass south lat")
    e.add_argument("--east", type=float, default=None, help="Live Overpass east lon")
    e.add_argument("--north", type=float, default=None, help="Live Overpass north lat")
    e.add_argument("--out", "-o", required=True, help="Output pack directory")
    e.add_argument("--pack-id", default="burke_overpass_proof_v1")
    e.add_argument("--display-name", default="Burke Lakefront Overpass Proof")
    e.add_argument(
        "--preset",
        default="Sunset",
        choices=("Sunset", "Twilight", "Midnight"),
    )
    e.add_argument(
        "--timeout", type=int, default=45, help="Live Overpass timeout seconds"
    )
    e.set_defaults(func=cmd_export)

    v = sub.add_parser("validate", help="validate_pack_dir fail-closed")
    v.add_argument("pack_dir")
    v.set_defaults(func=cmd_validate)

    args = p.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
