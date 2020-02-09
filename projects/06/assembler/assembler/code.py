import pathlib
from typing import Dict
from typing import Union

from assembler import parser


class HackAssembler:
    """Assemble a Hack assembly program."""
    def __init__(self, asm_path: Union[str, pathlib.Path]):
        self.asm_path = pathlib.Path(asm_path)   # ensure is pathlib.Path
        self.hack_path = self.asm_path.with_suffix(".hack")
        self.symbols = self._built_in_symbols()
        self._next_var_address = 16

    def __call__(self) -> pathlib.Path:
        commands = list(parser.Parser(self.asm_path))

        # 1st pass: populate symbol table with labels
        n_commands = 0
        for command in commands:
            if isinstance(command, parser.Label):
                self.symbols[command.symbol] = n_commands
            else:
                n_commands += 1

        # 2nd pass: translate commands + populate symbol table with variables
        with self.hack_path.open("w") as f:
            for command in commands:
                if isinstance(command, parser.Address):
                    f.write(self._address(command) + "\n")
                    continue

                if isinstance(command, parser.Compute):
                    f.write(self._compute(command) + "\n")
                    continue

        return self.hack_path

    @staticmethod
    def _built_in_symbols() -> Dict[str, int]:
        symbols = {"SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4}
        for i in range(16):
            symbols[f"R{i}"] = i
        symbols.update({"SCREEN": 16384, "KBD": 24576})
        return symbols

    def _address(self, address: parser.Address) -> str:
        r"""Returns a string representing the binary encoding of `address`."""
        if isinstance(address.item, int):
            # Address item already an integer
            value = address.item
        else:
            # Address item is symbol
            if address.item in self.symbols:
                # symbol exists in symbol table so use value
                value = self.symbols[address.item]
            else:
                # symbol does not exist in symbol table, make new variable
                self.symbols[address.item] = self._next_var_address
                value = self._next_var_address
                self._next_var_address += 1

        if not (0 <= value < 2**15):
            raise ValueError(f"{address} item must be in [0, 2**15)")

        return f"0{value:015b}"

    def _compute(self, compute: parser.Compute) -> str:
        r"""Returns a string representing the binary encoding of `compute`."""
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
