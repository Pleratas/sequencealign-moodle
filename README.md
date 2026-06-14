# Sequence Alignment Moodle Plugin

This repository contains a Moodle local plugin for interactive visualization of biological sequence alignment algorithms.

The plugin was developed as part of the course paper:

**Interaktyvių bioinformatikos mokymosi modulių kūrimas Moodle mokymosi aplinkoje**

## Project description

The project implements an interactive Moodle learning module for two classical dynamic programming algorithms used in bioinformatics:

* Needleman-Wunsch global sequence alignment
* Smith-Waterman local sequence alignment

The user can enter two nucleotide sequences, select an alignment algorithm, change scoring parameters, and view the resulting alignment, score matrix, traceback path, and step-by-step traceback animation.

The purpose of the plugin is educational. It is designed to help students understand how sequence alignment algorithms fill the dynamic programming matrix and reconstruct the final alignment through traceback.

## Main features

* Moodle local plugin: `local_sequencealign`
* Input form for two nucleotide sequences
* Needleman-Wunsch global alignment
* Smith-Waterman local alignment
* Adjustable scoring parameters:

  * match score
  * mismatch penalty
  * gap penalty
* Python backend for sequence alignment calculations
* PHP-to-Python execution from Moodle
* JSON-based communication between Python and PHP
* Score matrix visualization
* Traceback matrix/path visualization
* Step-by-step traceback animation
* Previous, next, play, pause, and reset animation controls
* Nucleotide coloring
* Responsive two-column Moodle interface
* Docker-based Moodle environment for reproducible deployment

## Tested environment

The project was tested in a Docker-based environment with:

* Moodle 5.0.1
* PHP 8.2.29
* Python 3.11.2
* MariaDB 10.11
* Docker Desktop / Docker Engine
* Docker Compose

## Repository structure

```text
sequencealign-moodle/
├── Dockerfile
├── docker-compose.yml
├── README.md
├── .gitignore
└── local/
    └── sequencealign/
        ├── index.php
        ├── version.php
        ├── settings.php
        ├── styles.css
        ├── classes/
        │   └── form/
        │       └── alignment_form.php
        ├── lang/
        │   └── en/
        │       └── local_sequencealign.php
        └── python/
            ├── alignment.py
            └── run_alignment.py
```

## Requirements

To run the project, install:

* Docker
* Docker Compose

On Windows, Docker Desktop with WSL 2 backend is recommended.

## Running the project

From the repository root, run:

```bash
docker compose up -d --build
```

The first launch may take several minutes because Moodle and MariaDB need to be initialized.

After the containers start, open Moodle in a browser:

```text
http://localhost:8080
```

Default Moodle login:

```text
Username: admin
Password: Admin123!
```

The sequence alignment plugin page is available at:

```text
http://localhost:8080/local/sequencealign/index.php
```

## Stopping the project

To stop the containers without deleting Moodle data:

```bash
docker compose down
```

To fully reset Moodle and the database:

```bash
docker compose down -v
```

After a full reset, the next run will reinstall Moodle and the plugin from the beginning.

## Example test input

Needleman-Wunsch test:

```text
Sequence 1: ATGCA
Sequence 2: ATGGA
Algorithm: Needleman-Wunsch
Match: 1
Mismatch: -1
Gap: -1
```

Smith-Waterman test:

```text
Sequence 1: ATGCA
Sequence 2: ATGGA
Algorithm: Smith-Waterman
Match: 1
Mismatch: -1
Gap: -1
```

Longer sequence test:

```text
Sequence 1: ATGCGTACGTA
Sequence 2: ATGCTA
Match: 1
Mismatch: -1
Gap: -1
```

## Testing the Python backend directly

The Python backend can also be tested directly inside the running Moodle container.

Needleman-Wunsch:

```bash
docker exec -it sequencealign-moodle python /opt/bitnami/moodle/local/sequencealign/python/run_alignment.py --seq1 ATGCA --seq2 ATGGA --algorithm nw --match 1 --mismatch -1 --gap -1
```

Smith-Waterman:

```bash
docker exec -it sequencealign-moodle python /opt/bitnami/moodle/local/sequencealign/python/run_alignment.py --seq1 ATGCA --seq2 ATGGA --algorithm sw --match 1 --mismatch -1 --gap -1
```

A successful response returns JSON containing:

* `success`
* `algorithm`
* `score_matrix`
* `traceback_matrix`
* `optimal_score`
* `aligned_seq1`
* `aligned_seq2`
* `traceback_path`
* `scoring`

## Accepted input symbols

The current implementation accepts nucleotide symbols:

```text
A, C, G, T, U
```

Sequences are normalized internally by removing surrounding whitespace and converting letters to uppercase.

Protein sequence alignment is not implemented in this version.

## Implementation overview

The system follows this data flow:

```text
Moodle user interface
→ PHP local plugin
→ Python command-line backend
→ sequence alignment algorithm
→ JSON result
→ Moodle visualization layer
```

The Python backend implements the algorithmic logic and returns the computed result as JSON. The Moodle plugin receives this result and displays the alignment output, score matrix, traceback path, and interactive animation.

## Notes

This project is intended for educational use. It focuses on clarity, visualization, and explanation of the sequence alignment process rather than high-performance biological sequence analysis.

The Docker setup is included to make the project easier to reproduce on another computer without manually installing Moodle, PHP, Python, and MariaDB.

## Author

Justinas Tomkevičius

Vilnius University
Bioinformatics course paper project
2026
