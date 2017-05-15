/**
 * Load scripts needed across the application.
 */
require('sass/style-application.scss');
require('sass/themes/open-edx.scss');

require(['views/data-table-view',
         'views/announcement-view'],
    function(DataTableView, AnnouncementView) {
        'use strict';

        // Instantiate the announcement view(s)
        $('[data-view=announcement]').each(function(index, element) {
            var announcement = new AnnouncementView({el: element});
            announcement.render();
        });
    }
);
