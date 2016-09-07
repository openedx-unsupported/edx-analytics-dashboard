define(function(require) {
    'use strict';

    var $ = require('jquery'),
        _ = require('underscore'),
        Marionette = require('marionette'),

        Utils = require('utils/utils'),
        downloadDataTemplate = require('text!learners/common/templates/download-data.underscore'),
        DownloadDataView;

    DownloadDataView = Marionette.ItemView.extend({
        template: _.template(downloadDataTemplate),

        ui: {
            dataDownloadForm: 'form.download-data',
            dataDownloadButton: 'button.download-data'
        },

        events: {
            'click button.download-data': 'onDownload'
        },

        defaults: {
            trackCategory: 'download_file',
            downloadDataTitle: gettext('Download CSV'),
            downloadDataMessage: gettext('Download search results to CSV')
        },

        initialize: function(options) {
            var splitUrl, splitParams;
            this.options = _.extend({}, this.defaults, options);

            // Parse the downloadUrl, if given, into URL and query params
            if (this.options.collection && !_.isEmpty(this.options.collection.downloadUrl)) {
                splitUrl = this.options.collection.downloadUrl.split('?', 2);
                this.downloadBaseUrl = splitUrl[0];

                // Store an ordered list of download query string parameters, ready to feed to Util.toQueryString
                splitParams = Utils.parseQueryString(splitUrl[1]);
                splitParams.course_id = this.options.collection.courseId;
                this.downloadParams = Object.keys(splitParams).sort().map(function(key) {
                    return {key: key, val: splitParams[key]};
                });
            }

            // Update the action on the download button's action when the collection changes.
            this.listenTo(this.options.collection, 'sync', this.updateDownloadForm);
        },

        onShow: function() {
            // Update the download form on page load
            this.updateDownloadForm();
        },

        onDownload: function(event) {
            // Trigger a tracking event using the template's data attributes
            var linkData = $(event.currentTarget).data();
            this.options.trackingModel.trigger(
                'segment:track',
                linkData.trackEvent,
                {category: linkData.trackCategory});
            return true;
        },

        templateHelpers: function() {
            var hasDownloadData = !_.isEmpty(this.downloadBaseUrl);
            return {
                hasDownloadData: hasDownloadData,
                downloadDataTitle: this.options.downloadDataTitle,
                downloadDataMessage: this.options.downloadDataMessage,
                trackCategory: this.options.trackCategory
            };
        },

        getDownloadUrl: function() {
            var downloadQuery = '',
                separator = '?',
                collectionQuery = this.options.collection.getQueryString();

            // Return empty string if no downloadBaseUrl
            if (_.isEmpty(this.downloadBaseUrl)) {
                return '';
            }

            if (collectionQuery !== '') {
                separator = '&';
            }
            downloadQuery = Utils.toQueryString(this.downloadParams, separator);

            return this.downloadBaseUrl + collectionQuery + downloadQuery;
        },

        updateDownloadForm: function() {
            var downloadUrl = this.getDownloadUrl(),
                downloadForm = $(this.ui.dataDownloadForm),
                splitUrl = downloadUrl.split('?', 2),
                queryParams = Utils.parseQueryString(splitUrl[1]);

            // Set the action URL for the download form to the base download URL
            $(this.ui.dataDownloadForm).attr('action', splitUrl[0]);

            // Create hidden input items for each query string parameter
            downloadForm.find('input[type=hidden]').remove();
            _.map(queryParams, function (value, key) {
                downloadForm.append($('<input>', {type: 'hidden', name: key, value: value}));
            });
        }
    });

    return DownloadDataView;
});

