import Backbone from 'backbone';
import CourseListCollection from 'course-list/common/collections/course-list';
import CourseListController from 'course-list/app/controller';
import CourseListRouter from 'course-list/app/router';
import PageModel from 'components/generic-list/common/models/page';

describe('CourseListRouter', () => {
  let course;
  let collection;
  let controller;
  let router;
  let server;

  beforeEach(() => {
    // Safeguard if history hasn't been stopped
    Backbone.history.stop();
    Backbone.history.start({ silent: true });
    server = sinon.fakeServer.create();
    course = {
      last_updated: new Date(2016, 1, 28),
    };
    collection = new CourseListCollection([course], { url: 'http://example.com' });
    controller = new CourseListController({
      courseListCollection: collection,
      pageModel: new PageModel(),
    });
    spyOn(controller, 'showCourseListPage').and.stub();
    spyOn(controller, 'showNotFoundPage').and.stub();
    spyOn(controller, 'onShowPage').and.stub();
    router = new CourseListRouter({
      controller,
    });
  });

  afterEach(() => {
    // Clear previous route
    router.navigate('');
    Backbone.history.stop();
    server.restore();
  });

  it('triggers a showPage event for pages beginning with "show"', () => {
    router.navigate('foo', { trigger: true });
    expect(controller.onShowPage).toHaveBeenCalled();
    router.navigate('/', { trigger: true });
    expect(controller.onShowPage).toHaveBeenCalled();
  });

  describe('showCourseListPage', () => {
    beforeEach(() => {
      // Backbone won't trigger a route unless we were on a previous url
      router.navigate('initial-fragment', { trigger: false });
    });

    it('should trigger on an empty URL fragment', () => {
      router.navigate('', { trigger: true });
      expect(controller.showCourseListPage).toHaveBeenCalled();
    });

    it('should trigger on a single forward slash', () => {
      router.navigate('/', { trigger: true });
      expect(controller.showCourseListPage).toHaveBeenCalled();
    });

    it('should trigger on a URL fragment with a querystring', () => {
      const querystring = 'text_search=some_course';
      router.navigate(`?${querystring}`, { trigger: true });
      expect(controller.showCourseListPage).toHaveBeenCalledWith(querystring, null);
    });
  });

  describe('showNotFoundPage', () => {
    it('should trigger on unmatched URLs', () => {
      router.navigate('this/does/not/match', { trigger: true });
      expect(controller.showNotFoundPage).toHaveBeenCalledWith('this/does/not/match', null);
    });
  });

  it('URL fragment is updated on CourseListCollection sync', (done) => {
    collection.state.currentPage = 2;
    collection.fetch({ reset: true });
    collection.once('sync', () => {
      expect(Backbone.history.getFragment()).toBe('?sortKey=catalog_course_title&order=asc&page=2');
      done();
    });
    server.requests[0].respond(200, {}, JSON.stringify([course]));
  });
});
