/**
 * Administration settings link for the Sequence Alignment Moodle plugin.
 *
 * This file registers the plugin page in Moodle site administration under
 * the local plugins section, allowing administrators to access the sequence
 * alignment module from the administration interface.
 *
 * @package    local_sequencealign
 * @author     Justinas Tomkevičius
 * @copyright  2026 Justinas Tomkevičius
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

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