define(function(require) {
    'use strict';

    var $ = require('jquery'),
        Backbone = require('backbone'),
        Marionette = require('marionette'),
        NProgress = require('nprogress'),
        _ = require('underscore'),

        initModels = require('load/init-page'),

        Collection = require('generic-list/common/collections/collection'),
        Controller = require('generic-list/app/controller'),
        RootView = require('generic-list/app/views/root'),
        Router = require('generic-list/app/router'),
        PageModel = require('generic-list/common/models/page'),

        ListApp;

    ListApp = Marionette.Application.extend({
        /**
         * Initializes the list app.
         *
         * @param options are passed to children
         */
        initialize: function(options) {
            this.options = options || {};
            this.listJson = this.options.listJson;
            this.listUrl = this.options.listUrl;
            this.listDownloadUrl = this.options.listDownloadUrl;
            this.mode = 'server';
        },

        onStart: function() {
            var pageModel = new PageModel(),
                collection,
                rootView;

            collection = new Collection(this.listJson, {
                url: this.listUrl,
                downloadUrl: this.listDownloadUrl
            });

            rootView = new RootView({
                el: $(this.options.containerSelector),
                pageModel: pageModel
            }).render();

            new Router({ // eslint-disable-line no-new
                controller: new Controller({
                    collection: collection,
                    hasData: _.isObject(this.listJson),
                    pageModel: pageModel,
                    rootView: rootView,
                    listUrl: this.listUrl,
                    trackingModel: initModels.models.trackingModel
                })
            });

            // If we haven't been provided with any data, fetch it now
            // from the server.
            if (!this.listJson) {
                collection.setPage(1);
            }

            Backbone.history.start();

            // Loading progress bar via nprogress
            NProgress.configure({showSpinner: false});
            $(document).ajaxStart(function() { NProgress.start(); });
            $(document).ajaxStop(function() { NProgress.done(); });
        }
    });

    return ListApp;
});
