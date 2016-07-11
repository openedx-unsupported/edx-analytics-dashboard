/**
 * Controller object for the learners application.  Handles business
 * logic of showing different 'pages' of the application.
 *
 * Requires the following values in the options hash:
 * - learnerCollection: A `LearnerCollection` instance.
 * - rootView: A `LearnersRootView` instance.
 */
define(function (require) {
    'use strict';

    var Backbone = require('backbone'),
        Marionette = require('marionette'),
        NProgress = require('nprogress'),

        EngagementTimelineModel = require('learners/common/models/engagement-timeline'),
        LearnerDetailView = require('learners/detail/views/learner-detail'),
        LearnerModel = require('learners/common/models/learner'),
        LearnerRosterView = require('learners/roster/views/roster'),
        ReturnLinkView = require('learners/detail/views/learner-return'),
        Utils = require('utils/utils'),
        LoadingView = require('learners/common/views/loading-view'),
        AlertView = require('learners/common/views/alert-view'),

        rosterLoadingTemplate = require('text!learners/roster/templates/roster-loading.underscore'),

        LearnersController;

    LearnersController = Marionette.Object.extend({
        initialize: function (options) {
            this.options = options || {};
            this.listenTo(this.options.learnerCollection, 'sync', this.onLearnerCollectionUpdated);
            this.onLearnerCollectionUpdated(this.options.learnerCollection);
        },

        /**
         * Event handler for the 'showPage' event.  Called by the
         * router whenever a route method beginning with "show" has
         * been triggered.
         */
        onShowPage: function () {
            // Show a loading bar
            NProgress.done(true);
            // Clear any existing alert
            this.options.rootView.triggerMethod('clearError');
        },

        onLearnerCollectionUpdated: function (collection) {
            // Note that we currently assume that all the learners in
            // the roster were last updated at the same time.
            if (collection.length) {
                this.options.pageModel.set('lastUpdated', collection.at(0).get('last_updated'));
            }
        },

        showLearnerRosterPage: function (queryString) {
            var rosterView = new LearnerRosterView({
                collection: this.options.learnerCollection,
                courseMetadata: this.options.courseMetadata,
                trackingModel: this.options.trackingModel,
            });

            try {
                var fetchNeeded = this.setCollectionState(queryString, this.options.learnerCollection);
                if (fetchNeeded) {
                    // Show a loading spinner while we fetch new collection data
                    var loadingView = new LoadingView({
                        model: this.options.learnerCollection,
                        template: _.template(rosterLoadingTemplate),
                        successView: rosterView
                    });
                    this.options.rootView.showChildView('main', loadingView);

                    var fetch = this.options.learnerCollection.fetch({reset: true});
                    if (fetch) {
                        fetch.complete(function (response) {
                            // fetch doesn't empty the collection on 404 by default
                            if (response && response.status === 404) {
                                this.options.learnerCollection.reset();
                            }
                        });
                    }
                } else {
                    // Immediately show the roster with the currently loaded collection data
                    this.options.rootView.showChildView('main', rosterView);
                }
            } catch (e) {
                if (e instanceof RangeError || e instanceof TypeError) {
                    this.showInvalidParametersPage();
                } else {
                    throw e;
                }
            }

            this.options.rootView.getRegion('navigation').empty();

            this.options.pageModel.set('title', gettext('Learners'));
            this.onLearnerCollectionUpdated(this.options.learnerCollection);

            // track the "page" view
            this.options.trackingModel.set('page', 'learner_roster');
            this.options.trackingModel.trigger('segment:page');

            return rosterView;
        },

        /**
         * Render the learner detail page assuming the learner model fetch
         * succeeds.
         */
        showLearnerDetailPage: function (username) {
            this.options.rootView.showChildView('navigation', new ReturnLinkView({
                queryString: this.options.learnerCollection.getQueryString()
            }));
            var engagementTimelineModel = new EngagementTimelineModel({}, {
                    url: this.options.learnerEngagementTimelineUrl.replace('temporary_username', username),
                    courseId: this.options.courseId
                }),
                learnerModel = this.options.learnerCollection.get(username) || new LearnerModel(),
                detailView;

            this.options.pageModel.set({
                title: gettext('Learner Details')
            });

            detailView = new LearnerDetailView({
                learnerModel: learnerModel,
                engagementTimelineModel: engagementTimelineModel
            });
            this.options.rootView.showChildView('main', detailView);

            // fetch data is the model is empty
            if (!learnerModel.hasData()) {
                learnerModel.on('change:last_updated', function () {
                    this.options.pageModel.set('lastUpdated', learnerModel.get('last_updated'));
                }, this);
                learnerModel.urlRoot = this.options.learnerListUrl;
                learnerModel.set({
                    course_id: this.options.courseId,
                    username: username
                })
                .fetch();
            }

            engagementTimelineModel.fetch();

            // track the "page" view
            this.options.trackingModel.set('page', 'learner_details');
            this.options.trackingModel.trigger('segment:page');

            return detailView;
        },

        showNotFoundPage: function () {
            // TODO: Implement this page in https://openedx.atlassian.net/browse/AN-6697
            var message = gettext("Sorry, we couldn't find the page you're looking for."),  // jshint ignore:line
                notFoundView;

            notFoundView = new (Backbone.View.extend({
                render: function () {
                    this.$el.text(message);
                    return this;
                }
            }))();
            this.options.rootView.showChildView('main', notFoundView);

            // track the "page" view
            this.options.trackingModel.set('page', 'learner_not_found');
            this.options.trackingModel.trigger('segment:page');

        },

        showInvalidParametersPage: function () {
            this.options.rootView.showChildView('main', new AlertView({
                alertType: 'error',
                title: gettext('Invalid Parameters'),
                body: gettext('Sorry, we couldn\'t find any learners who matched that query.'),
                link: {url: '#', text: gettext('Return to the Learners page.')}
            }));

            // track the "page" view
            this.options.trackingModel.set('page', 'learner_invalid_params');
            this.options.trackingModel.trigger('segment:page');

        },

        // Sets the learnerCollection state based on the query params. Returns a boolean stating whether the new state
        // differs from the old state (so the caller knows that the collection is stale and needs to do a fetch).
        setCollectionState: function (queryString, collection) {
            var params = Utils.parseQueryString(queryString),
                order = -1,
                order_name = 'ascending',
                fetchNeeded = false,
                page, sortKey;

            _.mapObject(params, function (val, key) {
                if (key === 'page') {
                    page = parseInt(val, 10);
                    if (page !== collection.state.currentPage) {
                        fetchNeeded = true;
                    }
                    collection.state.currentPage = page;
                } else if (key === 'sortKey') {
                    sortKey = val;
                } else if (key === 'order') {
                    order = val === 'desc' ? 1 : -1;
                    order_name = val === 'desc' ?  'descending' : 'ascending';
                } else {
                    if (key in collection.filterableFields || key === 'text_search') {
                        if (val !== collection.getFilterFieldValue(key)) {
                            fetchNeeded = true;
                        }
                        collection.setFilterField(key, val);
                    }
                }
            });

            // Set the sort state if sortKey or order from the queryString are different from the current state
            if (sortKey && sortKey in collection.sortableFields) {
                if (sortKey !== collection.state.sortKey || order !== collection.state.order) {
                    fetchNeeded = true;
                    collection.setSorting(sortKey, order);
                }
            }

            return fetchNeeded;
        }
    });

    return LearnersController;
});
