# A logfile parser

A small CLI tool to regex parse and transform unstructured logfiles.

#### Usage
```
usage: logparser [-h] [-d <dest>] [-n <name> [<name> ...]] <regex> <src> [<src> ...]

Transforms unstructured log-files into structured ones.

positional arguments:
  <regex>               Regex to match lines in log file(s). Can be either a filepath or cli
                        argumet. Regex must match the whole line. The specified groups are
                        extraced.
  <src>                 One or multiple source log file(s).

options:
  -h                    Show this help message and exits.
  -d <dest>             Destination for parsed logs.Default creates a <src>.csv output for each
                        <src> file.If <dest> is a directory, saves all outputs as
                        dest/{src}.csv.The directory must exist.If <dest> is a file, all outputs
                        will be merged within.
  -n <name> [<name> ...]
                        List of regex group names used for the CSV header.
```
#### Install

```
python -m build && python -m pip install -e .
```

#### Example
...
