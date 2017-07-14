import Backbone from 'backbone';
import CourseListCollection from 'course-list/common/collections/course-list';
import CourseListController from 'course-list/app/controller';
import CourseListRouter from 'course-list/app/router';
import PageModel from 'components/generic-list/common/models/page';

describe('CourseListRouter', () => {
  beforeEach(() => {
    Backbone.history.start({ silent: true });
    this.course = {
      last_updated: new Date(2016, 1, 28),
    };
    this.collection = new CourseListCollection([this.course]);
    this.controller = new CourseListController({
      courseListCollection: this.collection,
      pageModel: new PageModel(),
    });
    spyOn(this.controller, 'showCourseListPage').and.stub();
    spyOn(this.controller, 'showNotFoundPage').and.stub();
    spyOn(this.controller, 'onShowPage').and.stub();
    this.router = new CourseListRouter({
      controller: this.controller,
    });
  });

  afterEach(() => {
    // Clear previous route
    this.router.navigate('');
    Backbone.history.stop();
  });

  it('triggers a showPage event for pages beginning with "show"', () => {
    this.router.navigate('foo', { trigger: true });
    expect(this.controller.onShowPage).toHaveBeenCalled();
    this.router.navigate('/', { trigger: true });
    expect(this.controller.onShowPage).toHaveBeenCalled();
  });

  describe('showCourseListPage', () => {
    beforeEach(() => {
      // Backbone won't trigger a route unless we were on a previous url
      this.router.navigate('initial-fragment', { trigger: false });
    });

    it('should trigger on an empty URL fragment', () => {
      this.router.navigate('', { trigger: true });
      expect(this.controller.showCourseListPage).toHaveBeenCalled();
    });

    it('should trigger on a single forward slash', () => {
      this.router.navigate('/', { trigger: true });
      expect(this.controller.showCourseListPage).toHaveBeenCalled();
    });

    it('should trigger on a URL fragment with a querystring', () => {
      const querystring = 'text_search=some_course';
      this.router.navigate(`?${querystring}`, { trigger: true });
      expect(this.controller.showCourseListPage).toHaveBeenCalledWith(querystring, null);
    });
  });

  describe('showNotFoundPage', () => {
    it('should trigger on unmatched URLs', () => {
      this.router.navigate('this/does/not/match', { trigger: true });
      expect(this.controller.showNotFoundPage).toHaveBeenCalledWith('this/does/not/match', null);
    });
  });

  it('URL fragment is updated on CourseListCollection loaded', (done) => {
    this.collection.state.currentPage = 2;
    this.collection.once('loaded', () => {
      expect(Backbone.history.getFragment()).toBe('?sortKey=catalog_course_title&order=asc&page=2');
      done();
    });
    this.collection.trigger('loaded');
  });

  it('URL fragment is updated on CourseListCollection refresh', (done) => {
    this.collection.state.currentPage = 2;
    this.collection.once('backgrid:refresh', () => {
      expect(Backbone.history.getFragment()).toBe('?sortKey=catalog_course_title&order=asc&page=2');
      done();
    });
    this.collection.trigger('backgrid:refresh');
  });
});
