define([
    'collections/learner-collection',
    'jquery',
    'marionette',
    'models/learner-model',
    'underscore'
], function (LearnerCollection, $, Marionette, LearnerModel, _) {
    'use strict';

    var LearnersApp = Marionette.Application.extend({
        /**
         * Initializes the learner analytics app.
         *
         * @param options specifies the following values:
         * - courseId (string) required - the course id for this
         *   learner app
         * - containerSelector (string) required - the CSS selector
         *   for the HTML element that this app should attach to
         * - learnerListJson (Object) optional - an Object
         *   representing an initial server response from the Learner
         *   List endpoint used for pre-populating the app's
         *   LearnerCollection.  If not provided, the data is fetched
         *   asynchronously before app initialization.
         */
        initialize: function (options) {
            this.options = options || {};
        },

        onBeforeStart: function () {
            this.learnerCollection = new LearnerCollection(this.options.learnerListJson, {
                url: this.options.learnerListUrl,
                courseId: this.options.courseId,
                parse: this.options.learnerListJson ? true : false
            });
            if (!this.options.learnerListJson) {
                this.learnerCollection.setPage(1);
            }
        },

        onStart: function () {
            // TODO: remove this temporary UI with AN-6205.
            var LearnerView = Marionette.ItemView.extend({
                template: _.template(
                    '<div>' +
                        '| <%- name %> | ' +
                        '<%- username %> |' +
                        '</div>'
                )
            }), LearnersView = Marionette.CollectionView.extend({
                childView: LearnerView
            });

            new LearnersView({
                collection: this.learnerCollection,
                el: $(this.options.containerSelector)
            }).render();
        }
    });

    return LearnersApp;
});
