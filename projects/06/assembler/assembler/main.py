import argparse

from assembler.code import HackAssembler


def main():
    parser = argparse.ArgumentParser(description="Hack Assembler")
    parser.add_argument("infile", type=str, help="Hack assembly language file")
    args = parser.parse_args()

    assembler = HackAssembler()
    assembler(asm_path=args.infile)
