from pathlib import Path
import csv
import json
from typing import Optional


def read_lines(p_file: Path) -> list[list[str]]:
    with open(p_file, "r") as fd:
        return fd.readlines()


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