import $ from 'jquery';
import Backbone from 'backbone';
import Marionette from 'marionette';
import _ from 'underscore';

import initModels from 'load/init-page';

import CourseListCollection from 'course-list/common/collections/course-list';
import ProgramsCollection from 'course-list/common/collections/programs';
import CourseListController from 'course-list/app/controller';
import RootView from 'components/root/views/root';
import CourseListRouter from 'course-list/app/router';
import PageModel from 'components/generic-list/common/models/page';
import SkipLinkView from 'components/skip-link/views/skip-link-view';

export default class CourseListApp extends Marionette.Application {
  /**
   * Initializes the course-list analytics app.
   */
  constructor(options) {
    super();
    this.options = options || {};
  }

  onStart() {
    const pageModel = new PageModel();

    new SkipLinkView({
      el: 'body',
    }).render();

    const programsCollection = new ProgramsCollection(this.options.programsJson);

    const courseListCollection = new CourseListCollection(this.options.courseListJson, {
      downloadUrl: this.options.courseListDownloadUrl,
      filterNameToDisplay: {
        pacing_type: {
          instructor_paced: gettext('Instructor-Paced'),
          self_paced: gettext('Self-Paced'),
        },
        availability: {
          Upcoming: gettext('Upcoming'),
          Current: gettext('Current'),
          Archived: gettext('Archived'),
          unknown: gettext('Unknown'),
        },
        // Will be filled in dynamically by the initialize() function from the
        // programsCollection models:
        program_ids: {},
      },
      programsCollection,
      passingUsersEnabled: this.options.passingUsersEnabled,
    });

    const rootView = new RootView({
      el: $(this.options.containerSelector),
      pageModel,
      appClass: 'course-list',
      displayHeader: false,
    }).render();

    // eslint-disable-next-line no-new
    new CourseListRouter({
      controller: new CourseListController({
        courseListCollection,
        hasData: _.isObject(this.options.courseListJson),
        pageModel,
        rootView,
        trackingModel: initModels.models.trackingModel,
        filteringEnabled: this.options.filteringEnabled,
      }),
    });

    Backbone.history.start();
  }
}
