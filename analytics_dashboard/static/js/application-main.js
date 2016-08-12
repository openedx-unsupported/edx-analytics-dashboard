/**
 * Load scripts needed across the application.
 */

require(['bootstrap',
        'bootstrap_accessibility',
        'vendor/domReady!', 'load/init-page',
        'views/data-table-view',
        'views/announcement-view'],
    function(bootstrap, bootstrapAccessibility, doc, page, DataTableView, AnnouncementView) {
        'use strict';

        // Instantiate the announcement view(s)
        $('[data-view=announcement]').each(function(index, element) {
            var announcement = new AnnouncementView({el: element});
            announcement.render();
        });
    }
);
