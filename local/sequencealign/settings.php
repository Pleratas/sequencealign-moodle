<?php

defined('MOODLE_INTERNAL') || die();

if ($hassiteconfig) {
    $ADMIN->add(
        'localplugins',
        new admin_externalpage(
            'local_sequencealign',
            get_string('pluginname', 'local_sequencealign'),
            new moodle_url('/local/sequencealign/index.php')
        )
    );
}