import re
from re import Pattern
import argparse
from pathlib import Path
from typing import Optional

from logparser.logparselib import get_re_matcher, get_re_matching_strategy
from logparser.io import read_lines, write_to_csv


def val_parse_arg_srcs(p_srcs: list[Path]) -> list[Path]:
    srcs = []
    for p_src in p_srcs:
        if not p_src.exists():
            raise ValueError(f"Invalid src: '{p_src}', does not exists!")
        if not p_src.is_file():
            raise ValueError(f"src: '{p_src}' is not a file.")
        srcs.append(p_src)
    return srcs


def get_destinations(p_srcs: list[Path],
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


def is_valid_file(p_file: str) -> Path:
    p_file = Path(p_file)
    if not p_file.exists():
        raise ValueError(f"Invalid file path: '{p_file}', does not exists!")    
    if not p_file.is_file():
        raise ValueError(f"'{p_file}' is not a file.")
    return p_file


class SrcAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        values = [is_valid_file(val) for val in values]
        setattr(namespace, self.dest, values)


class DestAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        p_dest = values
        if not p_dest.exists():
            if not p_dest.parent.is_dir():
                raise ValueError(f"Parent dir '{p_dest}' does not exits")
        setattr(namespace, self.dest, p_dest)


class RegexAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        regex = values
        p_regex = Path(regex)
        if p_regex.exists():
            with open(p_regex, "r") as fd:
                regex = fd.read()
        try:
            regex = re.compile(regex)
        except re.error as e:
            raise TypeError(f"Invalid regex '{e.pattern}', at pos {e.pos}: {e.msg}")
        setattr(namespace, self.dest, regex)


def start():
    parser = argparse.ArgumentParser(
        prog="clparser",
        description=("Parses unstructured log-files"
                     "and transforms them into structured ones."),
        add_help=True
    )
    parser.add_argument(
        "regex", metavar="<regex>",
        action=RegexAction,
        type=str,
        help=("Regex to match lines in log file(s)."
              "Can be either a filepath or cli argumet."
              "The specified groups are extraced.")
    )
    parser.add_argument(
        "src", metavar="<src>",
        action=SrcAction,
        nargs="+",
        help="One or many source file(s)."
    )
    parser.add_argument(
        "-d", metavar="<dest>",
        type=Path,
        action=DestAction,
        help=("Destination for parsed logs."
              "Default creates a '<src>.csv' output for each <src> file."
              "If <dest> is a dir, saves all outputs as 'dest/{src}.csv.'"
              "The directory must exist."
              "If <dest> is a file, all outputs will be merged within."
              ),
    )
    parser.add_argument(
        "-s",
        choices=["match", "full", "search"],
        default="full",
        help=("The matching strategy"
              "See re documentation")
    )
    parser.add_argument(
        "-l", "--lazy",
        action='store_true',
        help=("If set skips log lines that can not be matched"
              "Otherwise exit with error in case a line cannot be matched")
    )
    parser.add_argument(
        "-n", metavar="<name>",
        nargs="+",
        default=[],
        help="List of regex group names used for the CSV header."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output to stdout."
    )
    args = parser.parse_args()

    re_pattern = args.regex
    p_srcs = args.src
    group_names = args.n
    lazy = args.lazy
    strategy = get_re_matching_strategy(args.s)
    p_dests = get_destinations(p_srcs, args.d)

    if args.verbose:
        print("regex:       {}".format(re_pattern))
        print("src:         {}".format([str(p) for p in p_srcs]))
        print("dest:        {}".format([str(p) for p in p_dests]))
        print("group names: {}".format(group_names))
        print("lazy:        {}".format(lazy))
        print("strategy:    {}".format(strategy.__name__))
        
    matcher = get_re_matcher(re_pattern, strategy, lazy)

    logs = [read_lines(p_src) for p_src in p_srcs]
    logs = [[matcher(l) for l in log] for log in logs]
    logs = [[l for l in log if l] for log in logs]

    if len(p_dests) == len(p_srcs):
        for p_dest, log in zip(p_dests, logs):
            write_to_csv(p_dest, log, group_names)
    else:
        logs = [l for log in logs for l in log]
        write_to_csv(p_dests[0], logs, group_names)


def main():
    try:
        start()
    except Exception as e:
        print("{} - {}".format(e.__class__.__name__, e))


if __name__ == "__main__":
    start()
