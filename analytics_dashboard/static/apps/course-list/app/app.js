define(function(require) {
    'use strict';

    var $ = require('jquery'),
        Backbone = require('backbone'),
        Marionette = require('marionette'),
        _ = require('underscore'),

        initModels = require('load/init-page'),

        CourseListCollection = require('course-list/common/collections/course-list'),
        ProgramsCollection = require('course-list/common/collections/programs'),
        CourseListController = require('course-list/app/controller'),
        RootView = require('components/root/views/root'),
        CourseListRouter = require('course-list/app/router'),
        PageModel = require('components/generic-list/common/models/page'),
        SkipLinkView = require('components/skip-link/views/skip-link-view'),

        CourseListApp;

    CourseListApp = Marionette.Application.extend({
        /**
         * Initializes the course-list analytics app.
         */
        initialize: function(options) {
            this.options = options || {};
        },

        onStart: function() {
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
                programsCollection: programsCollection,
                passingUsersEnabled: this.options.passingUsersEnabled
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
    });

    return CourseListApp;
});
