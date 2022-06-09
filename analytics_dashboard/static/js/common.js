require('sass/style-application.scss');
require('sass/themes/open-edx.scss');
require('underscore');
require('backbone');
require('bootstrap-sass');
require('bootstrap-accessibility-plugin');
require('load/init-page');
require('js/application-main');

require('jquery', $ => {
  'use strict';

  // Prevent XSS attack in jQuery 2.X: https://github.com/jquery/jquery/issues/2432#issuecomment-140038536
  $.ajaxSetup({
    contents: {
      javascript: false,
    },
  });
});
