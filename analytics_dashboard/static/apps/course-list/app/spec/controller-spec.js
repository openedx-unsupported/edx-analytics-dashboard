import CourseListCollection from 'course-list/common/collections/course-list';
import CourseListController from 'course-list/app/controller';
import RootView from 'components/root/views/root';
import PageModel from 'components/generic-list/common/models/page';
import TrackingModel from 'models/tracking-model';

describe('CourseListController', () => {
  let rootView;
  let course;
  let collection;
  let controller;

  // convenience method for asserting that we are on the course list page
  function expectCourseListPage(courseListController) {
    expect(courseListController.options.rootView.$('.course-list')).toBeInDOM();
    expect(courseListController.options.rootView.$('.course-list-header-region').html()).toContainText(
      'Course List',
    );
  }

  function fakeCourse(id, name) {
    const count = Math.floor(Math.random() * 150) + 50; // rand int from 50 - 200

    return {
      course_id: id,
      catalog_course_title: name,
      catalog_course: name,
      start_date: '2017-01-01',
      end_date: '2017-04-01',
      pacing_type: Math.random() > 0.5 ? 'instructor_paced' : 'self_paced',
      count,
      cumulative_count: Math.floor(count / 2) + count,
      passing_users: 0,
      enrollment_modes: {
        audit: {
          count: 0,
          cumulative_count: 0,
          count_change_7_days: 0,
        },
        credit: {
          count,
          cumulative_count: Math.floor(count / 2) + count,
          count_change_7_days: 5,
        },
        verified: {
          count: 0,
          cumulative_count: 0,
          count_change_7_days: 0,
        },
        honor: {
          count: 0,
          cumulative_count: 0,
          count_change_7_days: 0,
        },
        professional: {
          count: 0,
          cumulative_count: 0,
          count_change_7_days: 0,
        },
      },
      created: '',
      availability: 'unknown',
      count_change_7_days: 0,
      verified_enrollment: 0,
      program_ids: [],
    };
  }

  beforeEach(() => {
    const pageModel = new PageModel();

    setFixtures('<div class="root-view"><div class="main"></div></div>');
    rootView = new RootView({
      el: '.root-view',
      pageModel,
      appClass: 'course-list',
    });
    rootView.render();
    course = fakeCourse('course1', 'Course');
    collection = new CourseListCollection([course]);
    controller = new CourseListController({
      rootView,
      courseListCollection: collection,
      hasData: true,
      pageModel,
      trackingModel: new TrackingModel(),
    });
  });

  it('should show the course list page', () => {
    controller.showCourseListPage();
    expectCourseListPage(controller);
  });

  it('should show invalid parameters alert with invalid URL parameters', () => {
    controller.showCourseListPage('text_search=foo=');
    expect(controller.options.rootView.$('.course-list-alert-region').html()).toContainText(
      'Invalid Parameters',
    );
    expect(controller.options.rootView.$('.course-list-main-region').html()).toBe('');
  });

  it('should show the not found page', () => {
    controller.showNotFoundPage();
    // eslint-disable-next-line max-len
    expect(rootView.$el.html()).toContainText(
      "Sorry, we couldn't find the page you're looking for.",
    );
  });
  it('should sort the list with sort parameters', () => {
    const secondCourse = fakeCourse('course2', 'X Course');
    collection.add(secondCourse);
    controller.showCourseListPage('sortKey=catalog_course_title&order=desc');
    expect(collection.at(0).toJSON()).toEqual(secondCourse);
  });
});
