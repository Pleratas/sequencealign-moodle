"""
run_alignment.py

Command-line interface for the Sequence Alignment Moodle plugin.

This script receives input from the Moodle PHP layer through command-line
arguments, runs the selected sequence alignment algorithm, and returns the
result as JSON. The JSON output is decoded by the Moodle plugin and used to
display the score matrix, traceback matrix, aligned sequences, optimal score,
and traceback path.

Supported algorithms:
    - Needleman-Wunsch global alignment (--algorithm nw)
    - Smith-Waterman local alignment (--algorithm sw)

Author: Justinas Tomkevičius
Course paper: Interaktyvių bioinformatikos mokymosi modulių kūrimas Moodle mokymosi aplinkoje
Year: 2026
"""



import argparse
import json
import sys

from alignment import needleman_wunsch, smith_waterman


def main():
    parser = argparse.ArgumentParser(description="Run sequence alignment and return JSON.")

    parser.add_argument("--seq1", required=True)
    parser.add_argument("--seq2", required=True)
    parser.add_argument("--algorithm", required=True, choices=["nw", "sw"])
    parser.add_argument("--match", type=int, default=1)
    parser.add_argument("--mismatch", type=int, default=-1)
    parser.add_argument("--gap", type=int, default=-1)

    args = parser.parse_args()

    try:
        if args.algorithm == "nw":
            result = needleman_wunsch(
                args.seq1,
                args.seq2,
                match=args.match,
                mismatch=args.mismatch,
                gap=args.gap,
            )
        else:
            result = smith_waterman(
                args.seq1,
                args.seq2,
                match=args.match,
                mismatch=args.mismatch,
                gap=args.gap,
            )

        print(json.dumps({
            "success": True,
            "result": result.to_dict()
        }))

    except Exception as error:
        print(json.dumps({
            "success": False,
            "error": str(error)
        }))
        sys.exit(1)


if __name__ == "__main__":
    main()