from pathlib import Path
import re
import csv
import json

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


def write_to_csv(p_file: Path, data: list[str], header: list[str] = None) -> None:
    with open(p_out, "w") as fd:
        writer = csv.writer(fd)
        if header:
            writer.writerow(header)
        writer.writerows(data)


def write_to_json(p_file: Path, data: list[list[str]], attributes=list[str]) -> None:
    json_data = [{attr: val for attr, val in zip(attributes, line)} for line in data]
    with open(p_file, "w") as fd:
        json.dump({"logs": json_data}, fd, indent=4)


if __name__ == "__main__":
    p_file = Path("data/log1.txt")
    results = parse(p_file)
    file_format = "csv"
    if file_format == "csv":
        header = ["time", "level", "msg", "file", "func", "kind"]
        p_out = Path("logs.csv")
        write_to_csv(p_out, results, header)
    elif file_format == "json":
        attributes = ["time", "level", "msg", "file", "func", "kind"]
        p_out = Path("logs.json")
        write_to_json(p_out, results, attributes)
