import 'backgrid-paginator/backgrid-paginator.min.css';
import 'nprogress/nprogress.css';

require('jquery');
const page = require('load/init-page');

require(['apps/learners/app/app'], LearnersApp => {
  'use strict';

  const modelData = page.models.courseModel;
  const app = new LearnersApp({
    courseId: modelData.get('courseId'),
    containerSelector: '.learners-app-container',
    learnerListJson: modelData.get('learner_list_json'),
    learnerListUrl: modelData.get('learner_list_url'),
    learnerListDownloadUrl: modelData.get('learner_list_download_url'),
    courseLearnerMetadataJson: modelData.get('course_learner_metadata_json'),
    courseLearnerMetadataUrl: modelData.get('course_learner_metadata_url'),
    learnerEngagementTimelineUrl: modelData.get('learner_engagement_timeline_url'),
  });

  app.start();
});
