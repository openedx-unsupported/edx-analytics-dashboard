require('sass/style-application.scss');
require('sass/themes/open-edx.scss');

require([
    'jquery',
    'underscore',
    'backbone',
    'bootstrap-sass',
    'bootstrap-accessibility-plugin',
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
