define(function (require) {
    'use strict';

    var Marionette = require('marionette'),

        LearnersRouter;

    LearnersRouter = Marionette.AppRouter.extend({
        appRoutes: {
            // TODO: handle 'queryString' arguments in https://openedx.atlassian.net/browse/AN-6668
            '(/)(?*queryString)': 'showLearnerRosterPage',
            ':username(/)(?*queryString)': 'showLearnerDetailPage',
            '*notFound': 'showNotFoundPage'
        }
    });

    return LearnersRouter;
});
