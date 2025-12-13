<?php
/**
 * Requests for PHP
 *
 * A wrapper for the Requests library to be used in WordPress.
 */

if ( ! class_exists( 'Requests' ) ) {
	require_once __DIR__ . '/Requests/src/Autoload.php';
	WpOrg\Requests\Autoload::register();
	class_alias( 'WpOrg\Requests\Requests', 'Requests' );
    class_alias( 'WpOrg\Requests\Response', 'Requests_Response' );
    class_alias( 'WpOrg\Requests\Exception', 'Requests_Exception' );
    class_alias( 'WpOrg\Requests\Exception\HTTP', 'Requests_Exception_HTTP' );
    class_alias( 'WpOrg\Requests\Exception\Transport\cURL', 'Requests_Exception_Transport_cURL' );
    class_alias( 'WpOrg\Requests\Hooks', 'Requests_Hooks' );
    class_alias( 'WpOrg\Requests\Session', 'Requests_Session' );
    class_alias( 'WpOrg\Requests\Utility\CaseInsensitiveDictionary', 'Requests_Utility_CaseInsensitiveDictionary' );
}
?>
