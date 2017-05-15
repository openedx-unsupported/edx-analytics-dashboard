define(function(require) {
    'use strict';

    var Marionette = require('marionette'),

        LearnersRouter;

    LearnersRouter = Marionette.AppRouter.extend({
        // Routes intended to show a page in the app should map to method names
        // beginning with "show", e.g. 'showLearnerRosterPage'.
        appRoutes: {
            '(/)(?*queryString)': 'showLearnerRosterPage',
            ':username(/)(?*queryString)': 'showLearnerDetailPage',
            '*notFound': 'showNotFoundPage'
        },

        initialize: function(options) {
            this.options = options || {};
            this.learnerCollection = options.controller.options.learnerCollection;
            this.listenTo(this.learnerCollection, 'sync', this.updateUrl);
            Marionette.AppRouter.prototype.initialize.call(this, options);
        },

        // Called on LearnerCollection update. Converts the state of the collection (including any filters, searchers,
        // sorts, or page numbers) into a url and then navigates the router to that url.
        updateUrl: function() {
            this.navigate(this.learnerCollection.getQueryString(), {replace: true});
        }
    });

    return LearnersRouter;
});
