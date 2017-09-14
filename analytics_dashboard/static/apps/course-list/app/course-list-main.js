import 'backgrid-paginator/backgrid-paginator.min.css';

Promise.all([
  import('load/init-page'),
  import('apps/course-list/app/app'),
]).then(([page, { default: CourseListApp }]) => {
  const modelData = page.models.courseModel;
  const app = new CourseListApp({
    containerSelector: '.course-list-app-container',
    courseListJson: modelData.get('course_list_json'),
    programsJson: modelData.get('programs_json'),
    courseListDownloadUrl: modelData.get('course_list_download_url'),
    filteringEnabled: modelData.get('enable_course_filters'),
    passingUsersEnabled: modelData.get('enable_passing_users'),
  });

  app.start();
});
