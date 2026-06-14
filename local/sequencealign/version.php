/**
 * Version metadata for the Sequence Alignment Moodle plugin.
 *
 * This file defines the plugin component name, version number, required
 * Moodle version, maturity level, and release identifier used by Moodle
 * during plugin installation and upgrade checks.
 *
 * @package    local_sequencealign
 * @author     Justinas Tomkevičius
 * @copyright  2026 Justinas Tomkevičius
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

<?php

defined('MOODLE_INTERNAL') || die();

$plugin->component = 'local_sequencealign';
$plugin->version   = 2026052701;
$plugin->requires  = 2022112800;
$plugin->maturity  = MATURITY_ALPHA;
$plugin->release   = '0.1';