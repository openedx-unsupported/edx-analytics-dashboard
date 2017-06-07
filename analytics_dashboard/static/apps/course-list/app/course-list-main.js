require(['vendor/domReady!', 'jquery', 'load/init-page',
         'apps/course-list/app/app'], function(doc, $, page, CourseListApp) {
    'use strict';
    var modelData = page.models.courseModel,
        app = new CourseListApp({
            containerSelector: '.course-list-app-container',
            courseListJson: modelData.get('course_list_json'),
            programsJson: modelData.get('programs_json'),
            courseListDownloadUrl: modelData.get('course_list_download_url'),
            filteringEnabled: modelData.get('enable_course_filters'),
            passingUsersEnabled: modelData.get('enable_passing_users')
        });

    app.start();
});
