require([
    'jquery',
    'underscore',
    'backbone',
    'bootstrap',
    'bootstrap_accessibility',
    'vendor/domReady!',
    'load/init-page',
    'js/application-main'
], function($) {
    'use strict';

    // Prevent XSS attack in jQuery 2.X: https://github.com/jquery/jquery/issues/2432#issuecomment-140038536
    $.ajaxSetup({
        contents: {
            javascript: false
        }
    });
});
