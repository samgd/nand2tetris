"""

TODO: invalid should err

"""
import pathlib
import re
from dataclasses import dataclass
from typing import Optional
from typing import Union


@dataclass
class Address:
    """
    """
    item: Union[int, str]


@dataclass
class Compute:
    """
    """
    dest: Optional[str]
    comp: str
    jump: Optional[str]


@dataclass
class Label:
    """
    """
    label: str


class Parser:
    """Parses Hack assembly commands from a file.

    Args:

    """
    def __init__(self, path: Union[str, pathlib.Path]):
        self.path = pathlib.Path(path)

        # compile and assign to self regular expression for command parsing
        constant = "\d+"
        symbol = "[a-zA-Z_.$:][a-zA-Z\d_.$:]*"
        # leading whitespace
        prefix = "^\s*"
        # trailing whitespace and/or comment with optional line break/new line
        suffix = "\s*(?://.*)*$(?:\n|\r\n)?"

        # A instruction: @constant or @symbol
        a_pattern = f"{prefix}@(?P<item>{constant}|{symbol}){suffix}"

        # C instruction: dest=comp;jump
        # note:
        #   "|" is greedy and matches are tried left->right
        #   "+" is a special character and requires escaping
        dest = "(?:(?P<dest>AMD|AD|AM|MD|A|M|D)=)?"
        comp = "|".join([
            "A\+1", "D-1", "D\+1", "A-1", "D\+A", "D-A", "A-D", "D&A", "D\|A",
             "!M",  "-M",  "M\+1", "M-1", "D\+M", "D-M", "M-D", "D&M", "D\|M",
             "0",    "1",  "-1",   "!D",  "!A",   "-D",  "-A",  "M",   "D",
             "A"
        ])
        comp = "(?P<comp>" + comp + ")"
        jump = "(?:;(?P<jump>JGT|JEQ|JGE|JLT|JNE|JLE|JMP))?"
        c_pattern = f"{prefix}{dest}{comp}{jump}{suffix}"

        # label: (symbol)
        l_pattern = f"{prefix}\((?P<label_symbol>{symbol})\){suffix}"

        # whitespace or comments
        ws_pattern = f"^\s*$(?:\n|\r\n)?"
        cmt_pattern = f"^\s*//.*$(?:\n|\r\n)?"

        self._command_pattern = re.compile(
            f"(?P<a_instruct>{a_pattern})|"
            f"(?P<c_instruct>{c_pattern})|"
            f"(?P<label>{l_pattern})|"
            f"(?P<whitespace>{ws_pattern})|"
            f"(?P<comment>{cmt_pattern})"
        )
        self._cmt_pattern = cmt_pattern

    def __iter__(self):
        def command_gen(path):
            with self.path.open(mode='r') as f:
                for line in f:
                    command = self._parse(line)
                    if command:
                        yield command

        return command_gen(self.path)

    def _parse(self, line: str) -> Union[None, Address, Compute, Label]:
        """"""
        match = self._command_pattern.fullmatch(line)

        if match is None:
            raise ValueError(repr(line))

        if match["whitespace"] or match["comment"]:
            return

        if match["a_instruct"]:
            item = match["item"]
            if item[0].isdigit():
                return Address(item=int(item))
            return Address(item=item)

        if match["c_instruct"]:
            dest = match["dest"]
            comp = match["comp"]
            jump = match["jump"]
            return Compute(dest=dest, comp=comp, jump=jump)

        if match["label"]:
            return Label(label=match["label_symbol"])

        raise ValueError("unexpected match for line {line}")


    def __repr__(self):
        return f'{self.__class__.__name__}(path="{self.path.absolute()}")'
