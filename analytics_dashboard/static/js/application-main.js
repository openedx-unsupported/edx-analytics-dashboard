/**
 * Load scripts needed across the application.
 */
require('babel-polyfill');  // EDUCATOR-1184: this defines Promise for IE11
require('sass/style-application.scss');
require(process.env.THEME_SCSS);

require(['views/data-table-view',
    'views/announcement-view',
    'bootstrap-sass/assets/javascripts/bootstrap.js',
    'bootstrap-accessibility-plugin/plugins/js/bootstrap-accessibility'],
    function(DataTableView, AnnouncementView) {
        'use strict';

        // Instantiate the announcement view(s)
        $('[data-view=announcement]').each(function(index, element) {
            var announcement = new AnnouncementView({el: element});
            announcement.render();
        });
    }
);
