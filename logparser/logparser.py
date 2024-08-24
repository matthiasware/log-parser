from pathlib import Path
import re
from re import Pattern
import csv
import json
import argparse
from typing import Optional


def read_log_lines(p_file: Path) -> list[list[str]]:
    with open(p_file, "r") as fd:
        return fd.readlines()


def parse(logs: list[str], regex: Pattern) -> list[list[str]]:
    results = []
    for log in logs:
        r = regex.fullmatch(log)
        if r is None:
            raise ValueError(f"Regex does not match {log}")
        results.append(r.groups())
    return results


def write_to_csv(p_out: Path, logs: list[str], header: Optional[list[str]] = None) -> None:
    if header and logs:
        if not len(header) == len(logs[0]):
            raise ValueError(f"Insufficient header length. Expected {len(logs[0])}, got {len(header)}")
    with open(p_out, "w") as fd:
        writer = csv.writer(fd)
        if header:
            writer.writerow(header)
        writer.writerows(logs)


def write_to_json(p_out: Path, logs: list[list[str]], attributes=list[str]) -> None:
    json_data = [{attr: val for attr, val in zip(attributes, line)} for line in logs]
    with open(p_out, "w") as fd:
        json.dump({"logs": json_data}, fd, indent=4)


def val_parse_arg_srcs(p_srcs: list[Path]) -> list[Path]:
    srcs = []
    for p_src in p_srcs:
        if not p_src.exists():
            raise ValueError(f"Invalid src: '{p_src}', does not exists!")
        if not p_src.is_file():
            raise ValueError(f"src: '{p_src}' is not a file.")
        srcs.append(p_src)
    return srcs


def val_parse_arg_dest(p_srcs: list[Path],
                       p_dest: Optional[Path]) -> list[Path]:
    dests = []

    if p_dest is None:
        dests = [p_src.parent / (p_src.name + ".csv") for p_src in p_srcs]
    elif p_dest.is_dir():
        dests = [p_dest / (p_src.name + ".csv") for p_src in p_srcs]
    elif p_dest.is_file() or p_dest.parent.is_dir():
        dests = [p_dest]
    else:
        raise ValueError(f"Destination '{p_dest}' is neither a file, nor a directory.")
    return dests


def val_parse_arg_regex(regex: str) -> Pattern:
    p_regex = Path(regex)
    if p_regex.exists():
        with open(p_regex, "r") as fd:
            regex = fd.read()
    try:
        regex = re.compile(regex)
    except re.error as e:
        raise TypeError(f"Invalid regex '{e.pattern}', at pos {e.pos}: {e.msg}")
    return regex


def _main(args):

    regex = val_parse_arg_regex(args.regex)
    p_srcs = val_parse_arg_srcs(args.src)
    p_dests = val_parse_arg_dest(p_srcs, args.dest)
    group_names = args.names

    logs = [read_log_lines(p_src) for p_src in p_srcs]
    logs = [parse(log, regex) for log in logs]

    if len(p_dests) == len(p_srcs):
        for p_dest, log in zip(p_dests, logs):
            write_to_csv(p_dest, log, group_names)
    else:
        logs = [l for log in logs for l in log]
        write_to_csv(p_dests[0], logs, group_names)


def main():
    parser = argparse.ArgumentParser(
        prog="logparser",
        description="Transforms unstructured log-files into structured ones.",
        add_help=False
    )
    parser.add_argument('-h', action='help', default=argparse.SUPPRESS,
                        help='Show this help message and exits.')
    parser.add_argument("Regex", metavar="<regex>", type=str, help="Regex to match lines in log file(s). Can be either a filepath or cli argumet. Regex must match the whole line. The specified groups are extraced.")
    parser.add_argument(
        "src", metavar="<src>", type=Path, nargs="+", help="One or multiple source log file(s)."
    )
    parser.add_argument(
        "-d",
        metavar="<dest>",
        type=Path,
        default=None,
        help=("Destination for parsed logs."
              "Default creates a <src>.csv output for each <src> file."
              "If <dest> is a directory, saves all outputs as dest/{src}.csv."
              "The directory must exist."
              "If <dest> is a file, all outputs will be merged within."
              ""
              ),
    )
    parser.add_argument(
        "-n", nargs="+", default=[], metavar="<name>", help="List of regex group names used for the CSV header."
    )
    args = parser.parse_args()

    try:
        _main(args)
    except Exception as e:
        print("{} - {}".format(e.__class__.__name__, e))


if __name__ == "__main__":
    main()