<?php

require_once(__DIR__ . '/../../config.php');
require_once(__DIR__ . '/classes/form/alignment_form.php');

use local_sequencealign\form\alignment_form;

require_login();

$PAGE->set_url(new moodle_url('/local/sequencealign/index.php'));
$PAGE->set_context(context_system::instance());
$PAGE->set_title(get_string('pluginname', 'local_sequencealign'));
$PAGE->set_heading(get_string('pluginname', 'local_sequencealign'));

echo $OUTPUT->header();

echo html_writer::start_tag('div', ['class' => 'sequencealign-layout']);

$mform = new alignment_form();

if ($formdata = $mform->get_data()) {

    $seq1 = trim($formdata->seq1);
    $seq2 = trim($formdata->seq2);
    $algorithm = $formdata->algorithm;
    $match = (int)$formdata->match;
    $mismatch = (int)$formdata->mismatch;
    $gap = (int)$formdata->gap;

    $python = 'python';
    $script = __DIR__ . DIRECTORY_SEPARATOR . 'python' . DIRECTORY_SEPARATOR . 'run_alignment.py';

    $command =
        escapeshellcmd($python) . ' ' .
        escapeshellarg($script) . ' ' .
        '--seq1 ' . escapeshellarg($seq1) . ' ' .
        '--seq2 ' . escapeshellarg($seq2) . ' ' .
        '--algorithm ' . escapeshellarg($algorithm) . ' ' .
        '--match ' . escapeshellarg($match) . ' ' .
        '--mismatch ' . escapeshellarg($mismatch) . ' ' .
        '--gap ' . escapeshellarg($gap);

    $output = shell_exec($command);
    $json = json_decode($output, true);

    if (!$json || empty($json['success'])) {
        echo $OUTPUT->notification('Alignment failed: ' . s($json['error'] ?? 'Unknown error'), 'notifyproblem');
    } else {
        $result = $json['result'];

        echo html_writer::start_tag('div', ['class' => 'alignment-card']);

        echo html_writer::tag('h3', get_string('results', 'local_sequencealign'));

        $algorithmname = '';

$algorithmdescription = '';

if ($result['algorithm'] === 'needleman_wunsch') {

    $algorithmname = 'Needleman–Wunsch Algorithm';

    $algorithmdescription =
        'This algorithm performs global sequence alignment. '
        . 'It aligns the entire length of both sequences and uses dynamic programming '
        . 'to calculate the optimal alignment path.';
}
else {

    $algorithmname = 'Smith–Waterman Algorithm';

    $algorithmdescription =
        'This algorithm performs local sequence alignment. '
        . 'It searches for the most similar regions between two sequences '
        . 'using dynamic programming.';
}

echo html_writer::start_tag('div', ['class' => 'algorithm-explanation']);

echo html_writer::tag(
    'h4',
    $algorithmname
);

echo html_writer::tag(
    'p',
    $algorithmdescription
);

echo html_writer::tag(
    'p',
    'Green cells indicate the traceback path used to reconstruct the final alignment.'
);

echo html_writer::end_tag('div');

echo html_writer::start_tag('div', ['class' => 'result-summary']);

echo html_writer::tag(
    'div',
    html_writer::tag('div', 'Algorithm', ['class' => 'summary-label']) .
    html_writer::tag('div', s($result['algorithm']), ['class' => 'summary-value']),
    ['class' => 'summary-box']
);

echo html_writer::tag(
    'div',
    html_writer::tag('div', get_string('optimalscore', 'local_sequencealign'), ['class' => 'summary-label']) .
    html_writer::tag('div', s($result['optimal_score']), ['class' => 'summary-value']),
    ['class' => 'summary-box']
);

echo html_writer::end_tag('div');

echo html_writer::start_tag('div', ['class' => 'scoring-explanation']);

echo html_writer::tag('strong', 'Scoring parameters: ');

echo html_writer::tag(
    'span',
    'Match score rewards identical nucleotides. Mismatch penalty penalizes substitutions. Gap penalty penalizes insertions or deletions.'
);

echo html_writer::end_tag('div');

        $aligned1 = $result['aligned_seq1'];
$aligned2 = $result['aligned_seq2'];

$comparison = '';

for ($i = 0; $i < strlen($aligned1); $i++) {

    $char1 = $aligned1[$i];
    $char2 = $aligned2[$i];

    if ($char1 === $char2 && $char1 !== '-') {
        $comparison .= '|';
    }
    else if ($char1 === '-' || $char2 === '-') {
        $comparison .= ' ';
    }
    else {
        $comparison .= '.';
    }
}

echo html_writer::tag('h4', 'Alignment');

echo html_writer::start_tag('div', ['class' => 'alignment-display']);

echo html_writer::tag(
    'pre',
    s($aligned1),
    ['class' => 'alignment-sequence']
);

echo html_writer::tag(
    'pre',
    s($comparison),
    ['class' => 'alignment-comparison']
);

echo html_writer::tag(
    'pre',
    s($aligned2),
    ['class' => 'alignment-sequence']
);

echo html_writer::end_tag('div');
echo html_writer::tag('h4', get_string('scorematrix', 'local_sequencealign'));

$pathcells = [];
foreach ($result['traceback_path'] as $cell) {
    $pathcells[$cell[0] . ',' . $cell[1]] = true;
}

$seq1chars = str_split($result['seq1']);
$seq2chars = str_split($result['seq2']);

$arrowmap = [
    'D' => '↖',
    'U' => '↑',
    'L' => '←',
    'S' => '■',
    'O' => '●'
];

echo html_writer::start_tag('div', ['class' => 'alignment-matrix-wrapper']);
echo html_writer::start_tag('table', ['class' => 'alignment-matrix']);

// Header row.
echo html_writer::start_tag('tr');
echo html_writer::tag('th', '');
echo html_writer::tag('th', '-');

foreach ($seq2chars as $char) {
    echo html_writer::tag('th', s($char), ['class' => 'base base-' . strtolower($char)]);
}

echo html_writer::end_tag('tr');

// Matrix rows.
foreach ($result['score_matrix'] as $i => $row) {
    echo html_writer::start_tag('tr');

    $rowlabel = ($i === 0) ? '-' : $seq1chars[$i - 1];
    echo html_writer::tag('th', s($rowlabel), ['class' => 'base base-' . strtolower($rowlabel)]);

    foreach ($row as $j => $score) {
        $key = $i . ',' . $j;
$classes = ['matrix-cell'];

$attributes = [
    'class' => ''
];

if (isset($pathcells[$key])) {
    $classes[] = 'traceback-cell';
    $classes[] = 'traceback-hidden';

    $traceindex = array_search([$i, $j], $result['traceback_path']);
    if ($traceindex !== false) {
        $attributes['data-trace-index'] = $traceindex;
    }
}

$attributes['class'] = implode(' ', $classes);
        $direction = $result['traceback_matrix'][$i][$j] ?? '';
        $arrow = $arrowmap[$direction] ?? '';

        if (!isset($pathcells[$key])) {
            $arrow = '';
        }

        $cellcontent =
            html_writer::tag('div', s($score), ['class' => 'matrix-score']) .
            html_writer::tag('div', s($arrow), ['class' => 'matrix-arrow']);

echo html_writer::tag('td', $cellcontent, $attributes);    }

    echo html_writer::end_tag('tr');
}

echo html_writer::end_tag('table');
echo html_writer::end_tag('div');

echo html_writer::start_tag('div', ['class' => 'matrix-legend']);

echo html_writer::tag('span', '↖ diagonal move', ['class' => 'legend-item']);
echo html_writer::tag('span', '↑ gap in sequence 2', ['class' => 'legend-item']);
echo html_writer::tag('span', '← gap in sequence 1', ['class' => 'legend-item']);
echo html_writer::tag('span', 'Green cells = traceback path', ['class' => 'legend-item traceback-legend']);

echo html_writer::end_tag('div');
echo html_writer::start_tag('div', ['class' => 'traceback-controls']);

echo html_writer::tag('button', 'Previous step', [
    'type' => 'button',
    'id' => 'traceback-prev',
    'class' => 'btn btn-secondary'
]);

echo html_writer::tag('button', 'Next traceback step', [
    'type' => 'button',
    'id' => 'traceback-next',
    'class' => 'btn btn-primary'
]);

echo html_writer::tag('button', 'Play animation', [
    'type' => 'button',
    'id' => 'traceback-play',
    'class' => 'btn btn-success'
]);

echo html_writer::tag('button', 'Reset', [
    'type' => 'button',
    'id' => 'traceback-reset',
    'class' => 'btn btn-secondary'
]);

echo html_writer::tag('div', 'Traceback step: 0 / 0', [
    'id' => 'traceback-counter',
    'class' => 'traceback-counter'
]);

echo html_writer::end_tag('div');

       $formattedpath = [];

foreach ($result['traceback_path'] as $cell) {
    $formattedpath[] = '(' . $cell[0] . ',' . $cell[1] . ')';
}

$tracebackstring = implode(' → ', $formattedpath);

echo html_writer::tag(
    'h4',
    get_string('tracebackpath', 'local_sequencealign')
);

echo html_writer::tag(
    'div',
    $tracebackstring,
    ['class' => 'traceback-display']
);
        echo html_writer::end_tag('div');
    }
}

echo html_writer::start_tag('div', ['class' => 'alignment-card input-card']);
echo html_writer::tag('h3', 'Input Data');
$mform->display();
echo html_writer::end_tag('div');

echo html_writer::end_tag('div');

echo html_writer::script("
document.addEventListener('DOMContentLoaded', function () {
    let currentStep = -1;
    let playInterval = null;

    const cells = Array.from(document.querySelectorAll('[data-trace-index]'));
    const nextButton = document.getElementById('traceback-next');
    const prevButton = document.getElementById('traceback-prev');
    const resetButton = document.getElementById('traceback-reset');
    const playButton = document.getElementById('traceback-play');
    const counter = document.getElementById('traceback-counter');

    function updateCells() {
        cells.forEach(function(cell) {
            const index = parseInt(cell.getAttribute('data-trace-index'), 10);

            if (index <= currentStep) {
                cell.classList.remove('traceback-hidden');
                cell.classList.add('traceback-visible');
            } else {
                cell.classList.add('traceback-hidden');
                cell.classList.remove('traceback-visible');
            }
        });

        if (counter) {
            counter.textContent = 'Traceback step: ' + Math.max(currentStep + 1, 0) + ' / ' + cells.length;
        }
    }

    if (nextButton) {
        nextButton.addEventListener('click', function () {
            if (currentStep < cells.length - 1) {
                currentStep++;
                updateCells();
            }
        });
    }

    if (prevButton) {
        prevButton.addEventListener('click', function () {
            if (currentStep > -1) {
                currentStep--;
                updateCells();
            }
        });
    }

    if (resetButton) {
        resetButton.addEventListener('click', function () {
            currentStep = -1;
            clearInterval(playInterval);
            playInterval = null;
            if (playButton) {
                playButton.textContent = 'Play animation';
            }
            updateCells();
        });
    }

    if (playButton) {
        playButton.addEventListener('click', function () {
            if (playInterval) {
                clearInterval(playInterval);
                playInterval = null;
                playButton.textContent = 'Play animation';
                return;
            }

            playButton.textContent = 'Pause animation';

            playInterval = setInterval(function () {
                if (currentStep < cells.length - 1) {
                    currentStep++;
                    updateCells();
                } else {
                    clearInterval(playInterval);
                    playInterval = null;
                    playButton.textContent = 'Play animation';
                }
            }, 600);
        });
    }

    updateCells();
});
");

echo $OUTPUT->footer();