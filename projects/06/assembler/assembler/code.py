r"""
    Examples:

        >>> # MaxL.asm
        >>> import tempfile
        >>> with tempfile.NamedTemporaryFile(mode="w", suffix=".asm") as f:
        ...     _ = f.write('''
        ... // This file is part of www.nand2tetris.org
        ... // and the book "The Elements of Computing Systems"
        ... // by Nisan and Schocken, MIT Press.
        ... // File name: projects/06/max/MaxL.asm
        ...
        ... // Symbol-less version of the Max.asm program.
        ...
        ... @0
        ... D=M
        ... @1
        ... D=D-M
        ... @10
        ... D;JGT
        ... @1
        ... D=M
        ... @12
        ... 0;JMP
        ... @0
        ... D=M
        ... @2
        ... M=D
        ... @14
        ... 0;JMP
        ... ''')
        ...     _ = f.seek(0)
        ...     assembler = HackAssembler()
        ...     hack_path = assembler(asm_path=f.name)
        ...     print(hack_path.open("r").read())
        0000000000000000
        1111110000010000
        0000000000000001
        1111010011010000
        0000000000001010
        1110001100000001
        0000000000000001
        1111110000010000
        0000000000001100
        1110101010000111
        0000000000000000
        1111110000010000
        0000000000000010
        1110001100001000
        0000000000001110
        1110101010000111
        <BLANKLINE>


        >>> # RectL.asm
        >>> import tempfile
        >>> with tempfile.NamedTemporaryFile(mode="w", suffix=".asm") as f:
        ...     _ = f.write('''
        ... // This file is part of www.nand2tetris.org
        ... // and the book "The Elements of Computing Systems"
        ... // by Nisan and Schocken, MIT Press.
        ... // File name: projects/06/rect/RectL.asm
        ...
        ... // Symbol-less version of the Rect.asm program.
        ...
        ... @0
        ... D=M
        ... @23
        ... D;JLE
        ... @16
        ... M=D
        ... @16384
        ... D=A
        ... @17
        ... M=D
        ... @17
        ... A=M
        ... M=-1
        ... @17
        ... D=M
        ... @32
        ... D=D+A
        ... @17
        ... M=D
        ... @16
        ... MD=M-1
        ... @10
        ... D;JGT
        ... @23
        ... 0;JMP
        ... ''')
        ...     _ = f.seek(0)
        ...     assembler = HackAssembler()
        ...     hack_path = assembler(asm_path=f.name)
        ...     print(hack_path.open("r").read())
        0000000000000000
        1111110000010000
        0000000000010111
        1110001100000110
        0000000000010000
        1110001100001000
        0100000000000000
        1110110000010000
        0000000000010001
        1110001100001000
        0000000000010001
        1111110000100000
        1110111010001000
        0000000000010001
        1111110000010000
        0000000000100000
        1110000010010000
        0000000000010001
        1110001100001000
        0000000000010000
        1111110010011000
        0000000000001010
        1110001100000001
        0000000000010111
        1110101010000111
        <BLANKLINE>
"""
import pathlib
from typing import Union

from assembler import parser


class HackAssembler:
    """Assemble a Hack assembly program."""
    def __call__(self, asm_path: Union[str, pathlib.Path]) -> pathlib.Path:
        asm_path = pathlib.Path(asm_path)   # ensure is pathlib.Path
        hack_path = asm_path.with_suffix(".hack")

        commands = list(parser.Parser(asm_path))

        with hack_path.open("w") as f:
            for command in commands:
                if isinstance(command, parser.Address):
                    f.write(self._address(command) + "\n")
                    continue

                if isinstance(command, parser.Compute):
                    f.write(self._compute(command) + "\n")
                    continue

                raise ValueError(f"unknown command {command}")

        return hack_path

    @staticmethod
    def _address(address: parser.Address) -> str:
        r"""Returns a string representing the binary encoding of `address`.

        Examples:

            >>> address = parser.Address(item="5")
            >>> HackAssembler._address(address)
            '0000000000000101'

            >>> address = parser.Address(item=str(2**15 - 1))
            >>> HackAssembler._address(address)
            '0111111111111111'

            >>> address = parser.Address(item="-1")
            >>> HackAssembler._address(address)
            Traceback (most recent call last):
                ...
            ValueError: Address(item='-1') item must be in [0, 2**15)

            >>> address = parser.Address(item=str(2**15))
            >>> HackAssembler._address(address)
            Traceback (most recent call last):
                ...
            ValueError: Address(item='32768') item must be in [0, 2**15)
        """
        value = int(address.item)
        if not (0 <= value < 2**15):
            raise ValueError(f"{address} item must be in [0, 2**15)")
        return f"0{value:015b}"

    @staticmethod
    def _compute(compute: parser.Compute) -> str:
        r"""Returns a string representing the binary encoding of `compute`.

        Examples:

            >>> compute = parser.Compute(comp="D+A")
            >>> HackAssembler._compute(compute)
            '1110000010000000'

            >>> compute = parser.Compute(comp="-M", dest="AMD", jump="JMP")
            >>> HackAssembler._compute(compute)
            '1111110011111111'
        """
        comp_map = {
            "0":   "0101010", "1":   "0111111", "-1":  "0111010",
            "D":   "0001100", "A":   "0110000", "!D":  "0001101",
            "!A":  "0110001", "-D":  "0001111", "-A":  "0110011",
            "D+1": "0011111", "A+1": "0110111", "D-1": "0001110",
            "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
            "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
            "M":   "1110000", "!M":  "1110001", "-M":  "1110011",
            "M+1": "1110111", "M-1": "1110010", "D+M": "1000010",
            "D-M": "1010011", "M-D": "1000111", "D&M": "1000000",
            "D|M": "1010101"
        }
        comp_bin = comp_map[compute.comp]

        dest_bin = ["0", "0", "0"]
        if compute.dest:
            if "M" in compute.dest:
                dest_bin[2] = "1"
            if "D" in compute.dest:
                dest_bin[1] = "1"
            if "A" in compute.dest:
                dest_bin[0] = "1"
        dest_bin = "".join(dest_bin)

        jump_map = {
            None:  "000", "JGT": "001", "JEQ": "010", "JGE": "011",
            "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"
        }
        jump_bin = jump_map[compute.jump]

        return "111" + comp_bin + dest_bin + jump_bin



if __name__ == "__main__":
    import doctest
    doctest.testmod()
