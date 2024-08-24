# A logfile parser

A small CLI tool to regex parse and transform unstructured logfiles.

#### Usage
```
usage: clparser [-h] [-d <dest>] [-s {match,full,search}] [-l] [-n <name> [<name> ...]] [-v]
                <regex> <src> [<src> ...]

Parses unstructured log-filesand transforms them into structured ones.

positional arguments:
  <regex>               Regex to match lines in log file(s).Can be either a filepath or cli
                        argumet.The specified groups are extraced.
  <src>                 One or many source file(s).

options:
  -h, --help            show this help message and exit
  -d <dest>             Destination for parsed logs.Default creates a '<src>.csv' output for each
                        <src> file.If <dest> is a dir, saves all outputs as 'dest/{src}.csv.'The
                        directory must exist.If <dest> is a file, all outputs will be merged
                        within.
  -s {match,full,search}
                        The matching strategySee re documentation
  -l, --lazy            If set skips log lines that can not be matchedOtherwise exit with error in
                        case a line cannot be matched
  -n <name> [<name> ...]
                        List of regex group names used for the CSV header.
  -v, --verbose         Verbose output to stdout.
```
#### Install

```
python -m build && python -m pip install -e .
```

#### Example

Parses logfile data/log1.txt with the regex specified in data/log.regex and writes results to logs.csv
```
logparser data/log.regex data/log1.txt -d logs.csv
```

Parses all logfiles in data and merges the results in logs.csv:
```
logparser data/log.regex data/*.txt -d logs.csv
```

Grouop names can be specified that will then be used as header in the csv result file:
````
logparser data/log.regex data/*.txt -d logs.csv -n timestamp level msg file func kind
```

