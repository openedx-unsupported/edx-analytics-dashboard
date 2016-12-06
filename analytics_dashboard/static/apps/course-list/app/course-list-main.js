require(['vendor/domReady!', 'jquery', 'load/init-page',
         'apps/course-list/app/app'], function(doc, $, page, CourseListApp) {
    'use strict';
    var modelData = page.models.courseModel,
        app = new CourseListApp({
            containerSelector: '.course-list-app-container',
            courseListJson: modelData.get('course_list_json'),
            courseListUrl: modelData.get('course_list_url'),
            courseListDownloadUrl: modelData.get('course_list_download_url')
        });

    app.start();
});
