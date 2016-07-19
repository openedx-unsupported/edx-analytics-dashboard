/**
 * Displays either a paginated table of learners or a message that there are
 * no learners to display.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Marionette = require('marionette'),

        AlertView = require('learners/common/views/alert-view'),
        LearnerTableView = require('learners/roster/views/table'),

        LearnerResultsView;

    LearnerResultsView = Marionette.LayoutView.extend({
        template: _.template('<div class="roster-main"></div>'),
        regions: {
            main: '.roster-main'
        },
        initialize: function(options) {
            this.options = options || {};
            this.listenTo(this.options.collection, 'sync', this.onLearnerCollectionUpdated);
        },
        onBeforeShow: function() {
            this.onLearnerCollectionUpdated(this.options.collection);
        },
        onLearnerCollectionUpdated: function(collection) {
            if (collection.length) {
                // Don't re-render the learner table view if one already exists.
                if (!(this.getRegion('main').currentView instanceof LearnerTableView)) {
                    this.showChildView('main', new LearnerTableView({
                        collection: collection,
                        courseMetadata: this.options.courseMetadata,
                        trackingModel: this.options.trackingModel
                    }));
                }
            } else {
                this.showChildView('main', this.createAlertView(collection));
            }
        },
        createAlertView: function(collection) {
            var hasSearch = collection.hasActiveSearch(),
                hasActiveFilter = !_.isEmpty(collection.getActiveFilterFields()),
                suggestions = [],
                noLearnersMessage,
                detailedMessage;
            if (hasSearch || hasActiveFilter) {
                noLearnersMessage = gettext('No learners matched your criteria.');
                if (hasSearch) {
                    suggestions.push(gettext('Try a different search.'));
                }
                if (hasActiveFilter) {
                    suggestions.push(gettext('Try clearing the filters.'));
                }
            } else {
                noLearnersMessage = gettext('No learner data is currently available for your course.');
                // eslint-disable-next-line max-len
                detailedMessage = gettext('No learners are enrolled, or course activity data has not yet been processed. Data is updated every day, so check back regularly for up-to-date metrics.');
            }

            return new AlertView({
                alertType: 'info',
                title: noLearnersMessage,
                body: detailedMessage,
                suggestions: suggestions
            });
        }
    });

    return LearnerResultsView;
});
