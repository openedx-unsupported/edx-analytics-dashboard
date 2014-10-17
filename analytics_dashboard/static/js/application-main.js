/**
 * Load scripts needed across the application.
 */

require(['bootstrap', 'bootstrap_accessibility', 'vendor/domReady!', 'load/init-page', 'views/announcement-view'],
    function (bootstrap, bootstrap_accessibility, doc, page, AnnouncementView) {
        'use strict';

        // Instantiate the announcement view(s)
        $('[data-view=announcement]').each(function (index, element) {
            new AnnouncementView({el: element});
        });
    }
);
