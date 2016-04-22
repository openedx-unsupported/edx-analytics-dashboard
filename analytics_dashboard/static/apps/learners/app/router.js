define(function (require) {
    'use strict';

    var Marionette = require('marionette'),

        LearnersRouter;

    LearnersRouter = Marionette.AppRouter.extend({
        // Routes intended to show a page in the app should map to method names
        // beginning with "show", e.g. 'showLearnerRosterPage'.
        appRoutes: {
            // TODO: handle 'queryString' arguments in https://openedx.atlassian.net/browse/AN-6668
            '(/)(?*queryString)': 'showLearnerRosterPage',
            ':username(/)(?*queryString)': 'showLearnerDetailPage',
            '*notFound': 'showNotFoundPage'
        },

        onRoute: function (routeName) {
            if (routeName.indexOf('show') === 0) {
                this.options.controller.triggerMethod('showPage');
            }
        }
    });

    return LearnersRouter;
});
