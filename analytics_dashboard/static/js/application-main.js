/**
 * Load scripts needed across the application.
*/
import 'views/data-table-view';
import '@babel/polyfill'; // EDUCATOR-1184: this defines Promise for IE11
import 'sass/style-application.scss';
import 'bootstrap-sass/assets/javascripts/bootstrap';
import 'bootstrap-accessibility-plugin/plugins/js/bootstrap-accessibility';

// eslint-disable-next-line import/no-dynamic-require
require(process.env.THEME_SCSS);

define('views/announcement-view', AnnouncementView => {
  'use strict';

  // Instantiate the announcement view(s)
  $('[data-view=announcement]').each((index, element) => {
    const announcement = new AnnouncementView({ el: element });
    announcement.render();
  });
});
