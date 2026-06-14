<?php

namespace local_sequencealign\form;

defined('MOODLE_INTERNAL') || die();

require_once($CFG->libdir . '/formslib.php');

class alignment_form extends \moodleform {

    public function definition() {

        $mform = $this->_form;

        // Sequence 1
        $mform->addElement(
            'textarea',
            'seq1',
            get_string('sequence1', 'local_sequencealign'),
            'rows="4" cols="60"'
        );

        $mform->setType('seq1', PARAM_TEXT);

        // Sequence 2
        $mform->addElement(
            'textarea',
            'seq2',
            get_string('sequence2', 'local_sequencealign'),
            'rows="4" cols="60"'
        );

        $mform->setType('seq2', PARAM_TEXT);

        // Algorithm selector
        $algorithms = [
            'nw' => get_string('needlemanwunsch', 'local_sequencealign'),
            'sw' => get_string('smithwaterman', 'local_sequencealign'),
        ];

        $mform->addElement(
            'select',
            'algorithm',
            get_string('algorithm', 'local_sequencealign'),
            $algorithms
        );

        // Match score
        $mform->addElement(
            'text',
            'match',
            get_string('matchscore', 'local_sequencealign')
        );

        $mform->setType('match', PARAM_INT);
        $mform->setDefault('match', 1);

        // Mismatch penalty
        $mform->addElement(
            'text',
            'mismatch',
            get_string('mismatchpenalty', 'local_sequencealign')
        );

        $mform->setType('mismatch', PARAM_INT);
        $mform->setDefault('mismatch', -1);

        // Gap penalty
        $mform->addElement(
            'text',
            'gap',
            get_string('gappenalty', 'local_sequencealign')
        );

        $mform->setType('gap', PARAM_INT);
        $mform->setDefault('gap', -1);

        // Submit button
        $this->add_action_buttons(
            false,
            get_string('submitbutton', 'local_sequencealign')
        );
    }
}