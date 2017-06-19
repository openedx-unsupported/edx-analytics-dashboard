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


export class CourseListApp extends Marionette.Application {
    /**
     * Initializes the course-list analytics app.
     */
    constructor(options) {
        super();
        this.options = options || {};
    }

    onStart() {
        var pageModel = new PageModel(),
            courseListCollection,
            programsCollection,
            rootView;

        new SkipLinkView({
            el: 'body'
        }).render();

        programsCollection = new ProgramsCollection(this.options.programsJson);

        courseListCollection = new CourseListCollection(this.options.courseListJson, {
            downloadUrl: this.options.courseListDownloadUrl,
            filterNameToDisplay: {
                pacing_type: {
                    instructor_paced: gettext('Instructor-Paced'),
                    self_paced: gettext('Self-Paced')
                },
                availability: {
                    Upcoming: gettext('Upcoming'),
                    Current: gettext('Current'),
                    Archived: gettext('Archived'),
                    unknown: gettext('Unknown')
                },
                // Will be filled in dynamically by the initialize() function from the programsCollection models:
                program_ids: {}
            },
            programsCollection: programsCollection
        });

        rootView = new RootView({
            el: $(this.options.containerSelector),
            pageModel: pageModel,
            appClass: 'course-list',
            displayHeader: false
        }).render();

        new CourseListRouter({ // eslint-disable-line no-new
            controller: new CourseListController({
                courseListCollection: courseListCollection,
                hasData: _.isObject(this.options.courseListJson),
                pageModel: pageModel,
                rootView: rootView,
                trackingModel: initModels.models.trackingModel,
                filteringEnabled: this.options.filteringEnabled
            })
        });

        Backbone.history.start();
    }
};
