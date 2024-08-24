import re
from re import Pattern, Match
from typing import Callable



def get_re_matcher(pattern: Pattern,
                   strategy: Callable[[Pattern, str], Match],
                   lazy: bool) -> Callable[[str], list[str]]:
    def matching_fn(string: str) -> tuple[str]:
        m = strategy(pattern, string)
        if m is None:
            if lazy:
                return ()
            else:
                raise ValueError(f"Regex does not match '{string}'")
        return m.groups()
    return matching_fn


def get_re_matching_strategy(strategy: str) -> Callable[[str], list[str]]:
    match strategy:
        case "match":
            strategy = re.match
        case "full":
            strategy = re.fullmatch
        case "search":
            strategy = re.search
        case _:
            raise NotImplementedError(f"Strategy: {strategy}")
    return strategy
