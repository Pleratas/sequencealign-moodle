"""
alignment.py
============
Educational implementation of two classic sequence alignment algorithms:
  - Needleman-Wunsch  (global alignment, 1970)
  - Smith-Waterman    (local alignment,  1981)

Both algorithms use dynamic programming (DP).
Every intermediate step is stored and returned so that a Moodle plugin
(or any front-end) can later visualise the matrix fill-in and the traceback.

Allowed nucleotide symbols
--------------------------
A, C, G, T  – standard DNA bases
U           – uracil (RNA); accepted so that textbook examples such as
              "GCATGCU" can be used without extra pre-processing.
Sequences are case-insensitive; they are uppercased internally.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional


# ---------------------------------------------------------------------------
# Constants – traceback direction codes
# These are stored in the traceback matrix so the path can be reconstructed
# and also serialised to JSON later.
# ---------------------------------------------------------------------------
DIAG  = "D"   # came from the diagonal  → match or mismatch
UP    = "U"   # came from the cell above → gap in sequence 2
LEFT  = "L"   # came from the cell to the left → gap in sequence 1
STOP  = "S"   # Smith-Waterman: cell value is 0, traceback stops here
START = "O"   # origin cell (top-left); no predecessor


# Nucleotides accepted by the validator
VALID_BASES = set("ACGTU")


# ---------------------------------------------------------------------------
# AlignmentResult
# ---------------------------------------------------------------------------
@dataclass
class AlignmentResult:
    """
    Holds every artefact produced by one alignment run.

    Attributes
    ----------
    algorithm       : "needleman_wunsch" or "smith_waterman"
    seq1, seq2      : original (uppercased) input sequences
    score_matrix    : 2-D list[list[int|float]] – the filled DP table.
                      Row 0 / col 0 are the gap-initialisation row/column.
    traceback_matrix: 2-D list[list[str]] – direction codes (D/U/L/S/O).
    optimal_score   : the best alignment score found.
    aligned_seq1    : seq1 with gap characters ('-') inserted.
    aligned_seq2    : seq2 with gap characters ('-') inserted.
    traceback_path  : list of (row, col) tuples from start → end of path.
                      Suitable for highlighting cells in a visualisation.
    match, mismatch, gap : scoring parameters used (for display purposes).
    """
    algorithm       : str
    seq1            : str
    seq2            : str
    score_matrix    : List[List[int]]
    traceback_matrix: List[List[str]]
    optimal_score   : int
    aligned_seq1    : str
    aligned_seq2    : str
    traceback_path  : List[Tuple[int, int]]
    match           : int = 1
    mismatch        : int = -1
    gap             : int = -1

    def to_dict(self) -> dict:
        """
        Convert the result to a plain Python dict.
        This makes it trivial to serialise to JSON for a Moodle REST endpoint.

        Example usage
        -------------
        import json
        result = needleman_wunsch("GATTACA", "GCATGCU")
        payload = json.dumps(result.to_dict())
        """
        return {
            "algorithm"        : self.algorithm,
            "seq1"             : self.seq1,
            "seq2"             : self.seq2,
            "score_matrix"     : self.score_matrix,
            "traceback_matrix" : self.traceback_matrix,
            "optimal_score"    : self.optimal_score,
            "aligned_seq1"     : self.aligned_seq1,
            "aligned_seq2"     : self.aligned_seq2,
            "traceback_path"   : [list(p) for p in self.traceback_path],
            "scoring"          : {
                "match"    : self.match,
                "mismatch" : self.mismatch,
                "gap"      : self.gap,
            },
        }


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------
def validate_sequence(seq: str, name: str = "sequence") -> str:
    """
    Validate and normalise a nucleotide sequence.

    Rules
    -----
    1. Must be a non-empty string.
    2. After uppercasing, every character must be in VALID_BASES (A C G T U).

    Returns the uppercased sequence on success.
    Raises ValueError with a descriptive message on failure.
    """
    if not isinstance(seq, str):
        raise TypeError(f"{name} must be a string, got {type(seq).__name__}.")
    seq = seq.strip().upper()
    if len(seq) == 0:
        raise ValueError(f"{name} must not be empty.")
    invalid = set(seq) - VALID_BASES
    if invalid:
        sorted_invalid = sorted(invalid)
        raise ValueError(
            f"{name} contains invalid character(s): {sorted_invalid}. "
            f"Only DNA/RNA bases are accepted: {sorted(VALID_BASES)}."
        )
    return seq


# ---------------------------------------------------------------------------
# Scoring helper
# ---------------------------------------------------------------------------
def _score(a: str, b: str, match: int, mismatch: int) -> int:
    """Return match score if a == b, else mismatch penalty."""
    return match if a == b else mismatch


# ---------------------------------------------------------------------------
# Needleman-Wunsch – global alignment
# ---------------------------------------------------------------------------
def needleman_wunsch(
    seq1    : str,
    seq2    : str,
    match   : int = 1,
    mismatch: int = -1,
    gap     : int = -1,
) -> AlignmentResult:
    """
    Needleman-Wunsch global sequence alignment.

    Algorithm overview
    ------------------
    Global alignment means we align the *entire* length of both sequences,
    inserting gaps wherever needed.

    Step 1 – Initialisation
        Create an (m+1) × (n+1) matrix where m = len(seq1), n = len(seq2).
        Row 0 and column 0 are filled with multiples of the gap penalty
        (0, gap, 2*gap, 3*gap, …) because reaching any cell in the first
        row/column requires only gap operations.

    Step 2 – Matrix fill (bottom-up DP)
        For each cell (i, j) choose the maximum of three options:
          a) diagonal: score_matrix[i-1][j-1] + match/mismatch(seq1[i-1], seq2[j-1])
          b) up:       score_matrix[i-1][j]   + gap   (gap in seq2)
          c) left:     score_matrix[i][j-1]   + gap   (gap in seq1)
        Record which direction gave the maximum in traceback_matrix[i][j].

    Step 3 – Traceback (bottom-right → top-left)
        Start at cell (m, n) and follow the traceback arrows back to (0, 0).
          DIAG → both sequences advance (match or mismatch)
          UP   → seq1 advances, insert '-' in aligned_seq2
          LEFT → seq2 advances, insert '-' in aligned_seq1
        Because we build the alignment backwards, reverse the strings at end.

    Parameters
    ----------
    seq1, seq2 : nucleotide sequences (DNA/RNA, case-insensitive)
    match      : score added for a matching pair        (default  +1)
    mismatch   : penalty added for a mismatching pair   (default  -1)
    gap        : penalty added for each gap inserted    (default  -1)

    Returns
    -------
    AlignmentResult containing the full DP table, traceback matrix,
    aligned sequences, optimal score, and traceback path coordinates.
    """
    seq1 = validate_sequence(seq1, "seq1")
    seq2 = validate_sequence(seq2, "seq2")

    m = len(seq1)
    n = len(seq2)

    # ------------------------------------------------------------------
    # Step 1 – Initialise matrices
    # ------------------------------------------------------------------
    # score_matrix[i][j] will hold the best alignment score for
    # seq1[0..i-1] vs seq2[0..j-1].
    score_matrix    : List[List[int]] = [[0] * (n + 1) for _ in range(m + 1)]
    traceback_matrix: List[List[str]] = [[START] * (n + 1) for _ in range(m + 1)]

    # First column: aligning seq1[0..i-1] against an empty string
    # requires i gap insertions → score = i * gap
    for i in range(1, m + 1):
        score_matrix[i][0]    = i * gap
        traceback_matrix[i][0] = UP       # to reach here we always came from above

    # First row: aligning an empty string against seq2[0..j-1]
    # requires j gap insertions → score = j * gap
    for j in range(1, n + 1):
        score_matrix[0][j]    = j * gap
        traceback_matrix[0][j] = LEFT     # to reach here we always came from the left

    # ------------------------------------------------------------------
    # Step 2 – Fill the DP matrix row by row, left to right
    # ------------------------------------------------------------------
    for i in range(1, m + 1):
        for j in range(1, n + 1):

            # Option A – diagonal move: align seq1[i-1] with seq2[j-1]
            diag_score = score_matrix[i - 1][j - 1] + _score(seq1[i - 1], seq2[j - 1], match, mismatch)

            # Option B – upward move: seq1[i-1] aligned against a gap in seq2
            up_score   = score_matrix[i - 1][j] + gap

            # Option C – leftward move: seq2[j-1] aligned against a gap in seq1
            left_score = score_matrix[i][j - 1] + gap

            # Choose the best option (ties broken: diagonal > up > left)
            best = max(diag_score, up_score, left_score)
            score_matrix[i][j] = best

            # Record which direction produced the best score
            if best == diag_score:
                traceback_matrix[i][j] = DIAG
            elif best == up_score:
                traceback_matrix[i][j] = UP
            else:
                traceback_matrix[i][j] = LEFT

    # The optimal global alignment score is always in the bottom-right cell
    optimal_score = score_matrix[m][n]

    # ------------------------------------------------------------------
    # Step 3 – Traceback from (m, n) back to (0, 0)
    # ------------------------------------------------------------------
    aligned_seq1: List[str] = []
    aligned_seq2: List[str] = []
    path        : List[Tuple[int, int]] = []

    i, j = m, n   # start at bottom-right

    while i > 0 or j > 0:
        path.append((i, j))
        direction = traceback_matrix[i][j]

        if direction == DIAG:
            # Both sequences contribute one character (match or mismatch)
            aligned_seq1.append(seq1[i - 1])
            aligned_seq2.append(seq2[j - 1])
            i -= 1
            j -= 1

        elif direction == UP:
            # seq1 contributes a character; seq2 gets a gap
            aligned_seq1.append(seq1[i - 1])
            aligned_seq2.append("-")
            i -= 1

        else:  # LEFT
            # seq2 contributes a character; seq1 gets a gap
            aligned_seq1.append("-")
            aligned_seq2.append(seq2[j - 1])
            j -= 1

    # Include the origin cell in the path
    path.append((0, 0))

    # The alignment was built right-to-left; reverse to get left-to-right
    aligned_seq1.reverse()
    aligned_seq2.reverse()
    path.reverse()

    return AlignmentResult(
        algorithm        = "needleman_wunsch",
        seq1             = seq1,
        seq2             = seq2,
        score_matrix     = score_matrix,
        traceback_matrix = traceback_matrix,
        optimal_score    = optimal_score,
        aligned_seq1     = "".join(aligned_seq1),
        aligned_seq2     = "".join(aligned_seq2),
        traceback_path   = path,
        match            = match,
        mismatch         = mismatch,
        gap              = gap,
    )


# ---------------------------------------------------------------------------
# Smith-Waterman – local alignment
# ---------------------------------------------------------------------------
def smith_waterman(
    seq1    : str,
    seq2    : str,
    match   : int = 2,
    mismatch: int = -1,
    gap     : int = -1,
) -> AlignmentResult:
    """
    Smith-Waterman local sequence alignment.

    Algorithm overview
    ------------------
    Local alignment finds the *best-scoring contiguous sub-region* shared
    by the two sequences, ignoring poorly matching flanks.

    The key difference from Needleman-Wunsch is the **zero-reset rule**:
    whenever the score would go negative, it is set to 0 instead.
    This allows the algorithm to "forget" bad-scoring regions and start a
    fresh alignment anywhere in the matrix.

    Step 1 – Initialisation
        The entire first row and first column are 0 (unlike Needleman-Wunsch).
        A local alignment can start anywhere, so no pre-loaded gap penalties.

    Step 2 – Matrix fill
        For each cell (i, j) choose the maximum of FOUR options:
          a) 0              – reset: start a new alignment here
          b) diagonal + s   – extend an existing alignment (match/mismatch)
          c) up    + gap    – extend with a gap in seq2
          d) left  + gap    – extend with a gap in seq1
        Track the position of the global maximum (best_score, best_pos).

    Step 3 – Traceback (best_pos → first 0 cell)
        Start at the highest-scoring cell and follow arrows until a cell
        with value 0 is reached (direction code STOP).

    Parameters
    ----------
    seq1, seq2 : nucleotide sequences (DNA/RNA, case-insensitive)
    match      : score added for a matching pair        (default  +2)
    mismatch   : penalty added for a mismatching pair   (default  -1)
    gap        : penalty added for each gap inserted    (default  -1)

    Returns
    -------
    AlignmentResult (same structure as Needleman-Wunsch for easy comparison).
    """
    seq1 = validate_sequence(seq1, "seq1")
    seq2 = validate_sequence(seq2, "seq2")

    m = len(seq1)
    n = len(seq2)

    # ------------------------------------------------------------------
    # Step 1 – Initialise: first row and column are all 0
    # ------------------------------------------------------------------
    score_matrix    : List[List[int]] = [[0] * (n + 1) for _ in range(m + 1)]
    traceback_matrix: List[List[str]] = [[STOP] * (n + 1) for _ in range(m + 1)]

    # We will track where the highest score lives so we know where to
    # start the traceback.
    best_score = 0
    best_pos   = (0, 0)

    # ------------------------------------------------------------------
    # Step 2 – Fill the DP matrix
    # ------------------------------------------------------------------
    for i in range(1, m + 1):
        for j in range(1, n + 1):

            # Option A – diagonal: align seq1[i-1] with seq2[j-1]
            diag_score = score_matrix[i - 1][j - 1] + _score(seq1[i - 1], seq2[j - 1], match, mismatch)

            # Option B – upward: seq1[i-1] vs gap in seq2
            up_score   = score_matrix[i - 1][j] + gap

            # Option C – leftward: gap in seq1 vs seq2[j-1]
            left_score = score_matrix[i][j - 1] + gap

            # Zero-reset rule: never let the score go below 0
            best = max(0, diag_score, up_score, left_score)
            score_matrix[i][j] = best

            # Record direction (or STOP if score reset to 0)
            if best == 0:
                traceback_matrix[i][j] = STOP
            elif best == diag_score:
                traceback_matrix[i][j] = DIAG
            elif best == up_score:
                traceback_matrix[i][j] = UP
            else:
                traceback_matrix[i][j] = LEFT

            # Track global maximum — this is where the best local alignment ends
            if best > best_score:
                best_score = best
                best_pos   = (i, j)

    optimal_score = best_score

    # ------------------------------------------------------------------
    # Step 3 – Traceback from best_pos until we hit a STOP (score == 0)
    # ------------------------------------------------------------------
    aligned_seq1: List[str] = []
    aligned_seq2: List[str] = []
    path        : List[Tuple[int, int]] = []

    i, j = best_pos

    while traceback_matrix[i][j] != STOP:
        path.append((i, j))
        direction = traceback_matrix[i][j]

        if direction == DIAG:
            aligned_seq1.append(seq1[i - 1])
            aligned_seq2.append(seq2[j - 1])
            i -= 1
            j -= 1

        elif direction == UP:
            aligned_seq1.append(seq1[i - 1])
            aligned_seq2.append("-")
            i -= 1

        else:  # LEFT
            aligned_seq1.append("-")
            aligned_seq2.append(seq2[j - 1])
            j -= 1

    # Mark the final STOP cell as part of the path
    path.append((i, j))

    # Reverse: traceback builds alignment right-to-left
    aligned_seq1.reverse()
    aligned_seq2.reverse()
    path.reverse()

    return AlignmentResult(
        algorithm        = "smith_waterman",
        seq1             = seq1,
        seq2             = seq2,
        score_matrix     = score_matrix,
        traceback_matrix = traceback_matrix,
        optimal_score    = optimal_score,
        aligned_seq1     = "".join(aligned_seq1),
        aligned_seq2     = "".join(aligned_seq2),
        traceback_path   = path,
        match            = match,
        mismatch         = mismatch,
        gap              = gap,
    )
