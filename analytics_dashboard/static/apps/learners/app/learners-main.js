require('backgrid-paginator/backgrid-paginator.min.css');
require('nprogress/nprogress.css');

require(['vendor/domReady', 'jquery', 'load/init-page', 'apps/learners/app/app'], function(doc, $, page, LearnersApp) {
    'use strict';
    var modelData = page.models.courseModel,
        app = new LearnersApp({
            courseId: modelData.get('courseId'),
            containerSelector: '.learners-app-container',
            learnerListJson: modelData.get('learner_list_json'),
            learnerListUrl: modelData.get('learner_list_url'),
            learnerListDownloadUrl: modelData.get('learner_list_download_url'),
            courseLearnerMetadataJson: modelData.get('course_learner_metadata_json'),
            courseLearnerMetadataUrl: modelData.get('course_learner_metadata_url'),
            learnerEngagementTimelineUrl: modelData.get('learner_engagement_timeline_url')
        });

    app.start();
});
