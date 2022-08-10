/**
 * Load scripts needed across the application.
*/
require('views/data-table-view');
require('@babel/polyfill'); // EDUCATOR-1184: this defines Promise for IE11
require('sass/style-application.scss');
require('bootstrap-sass/assets/javascripts/bootstrap');
require('bootstrap-accessibility-plugin/plugins/js/bootstrap-accessibility');

// eslint-disable-next-line import/no-dynamic-require
require(process.env.THEME_SCSS);

require(['views/announcement-view'], AnnouncementView => {
  'use strict';

  // Instantiate the announcement view(s)
  $('[data-view=announcement]').each((index, element) => {
    const announcement = new AnnouncementView({ el: element });
    announcement.render();
  });
});
