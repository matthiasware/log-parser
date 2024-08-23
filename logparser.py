from pathlib import Path
import re
import csv
import json
import argparse
from typing import Optional
import sys

re_timestamp = r'time="([^"]+)"'
re_level = r"level=(info|warning|error)"
re_msg = r'msg="([^"]+)"'
re_file = r'file="([^"]*)"'
re_func = r"func=([^\s]*)"
re_kind = r"kind=([^\s]*)"

re_total = (
    re_timestamp
    + "\\s"
    + re_level
    + "\\s"
    + re_msg
    + "\\s"
    + re_file
    + "\\s"
    + re_func
    + "\\s"
    + re_kind
    + "\\s?"
)

regex = re.compile(re_total)



def parse(p_file: Path) -> list[list[str]]:
    assert p_file.exists()
    results = []
    with open(p_file, "r") as fd:
        while line := fd.readline():
            r = regex.fullmatch(line)
            if r is None:
                print(f"Regex does not match {line}")
                continue
            results.append(r.groups())
    return results


def write_to_csv(
    p_out: Path, logs: list[str], header: Optional[list[str]] = None
) -> None:
    print(header)
    with open(p_out, "w") as fd:
        writer = csv.writer(fd)
        if header:
            writer.writerow(header)
        writer.writerows(logs)


def write_to_json(p_out: Path, logs: list[list[str]], attributes=list[str]) -> None:
    json_data = [{attr: val for attr, val in zip(attributes, line)} for line in logs]
    with open(p_out, "w") as fd:
        json.dump({"logs": json_data}, fd, indent=4)


def main(p_in: Path, p_out: Path, out_format: str, **export_kargs) -> None:
    logs = parse(p_in)

    match out_format:
        case "json":
            write_to_json(p_out, logs, **export_kargs)
        case "csv":
            write_to_csv(p_out, logs, **export_kargs)
        case _:
            raise NotImplementedError(f"file format {out_format}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Logparser",
        description=(
            "Transforms unstructured log-files into structured ones."
            "Extracts regex groups from raw log-files."
        ),
    )
    parser.add_argument("p_in", metavar="src", type=Path, help="Source log file.")
    parser.add_argument(
        "-o",
        "--out",
        metavar="dest",
        type=Path,
        default=None,
        help="Destination log file.",
    )
    parser.add_argument(
        "--header", nargs="+", default=[], metavar="h", help="List of CSV header names."
    )
    parser.add_argument("-r", "--regex", default=None, type=str, description="regex")

    args = parser.parse_args()
    print(args)
    out_format = "csv"

    # parse p_in
    p_in = args.p_in
    if not p_in.exists():
        print(f"Invalid src: '{p_in}', does not exists!")
        sys.exit(1)
    if not p_in.is_file():
        print(f"src: '{p_in}' is not a file.")
        sys.exit(1)

    # parse p_out
    p_out = args.out
    if p_out is None:
        p_out = p_in.parent / (p_in.name + ".csv")
    if p_out.is_dir():
        print(f'Output desitionation "{p_out}" is a directory, expected file.')
        sys.exit(1)
    if p_out.is_file() and p_out.exists():
        print(f"Warning: Output file {p_out} already exists!")

    main(p_in, p_out, out_format="csv", header=args.header)
