define((require) => {
  'use strict';

  const $ = require('jquery');
  const _ = require('underscore');
  const Marionette = require('marionette');

  const Utils = require('utils/utils');
  const downloadDataTemplate = require('components/download/templates/download-data.underscore');

  const DownloadDataView = Marionette.ItemView.extend({
    template: _.template(downloadDataTemplate),

    ui: {
      dataDownloadButton: '.action-download-data',
    },

    events: {
      'click .action-download-data': 'onDownload',
    },

    defaults: {
      trackCategory: 'download_file',
      downloadDataTitle: gettext('Download CSV'),
      downloadDataMessage: gettext('Download search results to CSV'),
    },

    initialize(options) {
      let splitUrl; let splitParams;
      this.options = _.extend({}, this.defaults, options);

      // Parse the downloadUrl, if given, into URL and query params
      if (this.options.collection && !_.isEmpty(this.options.collection.downloadUrl)) {
        splitUrl = this.options.collection.downloadUrl.split('?', 2);
        // eslint-disable-next-line prefer-destructuring
        this.downloadBaseUrl = splitUrl[0];

        // Store an ordered list of download query string parameters, ready to feed to Util.toQueryString
        splitParams = Utils.parseQueryString(splitUrl[1]);
        splitParams.course_id = this.options.collection.courseId;
        this.downloadParams = Object.keys(splitParams).sort().map((key) => ({ key, val: splitParams[key] }));
      }

      // Update the href on the download button when the collection changes.
      this.listenTo(this.options.collection, 'sync', this.updateDownloadLink);
    },

    onDownload(event) {
      // Trigger a tracking event using the template's data attributes
      const linkData = $(event.currentTarget).data();
      this.options.trackingModel.trigger(
        'segment:track',
        linkData.trackEvent,
        { category: linkData.trackCategory },
      );
      return true;
    },

    templateHelpers() {
      const hasDownloadData = !_.isEmpty(this.downloadBaseUrl);
      return {
        hasDownloadData,
        downloadDataTitle: this.options.downloadDataTitle,
        downloadDataMessage: this.options.downloadDataMessage,
        downloadUrl: this.getDownloadUrl(),
        trackCategory: this.options.trackCategory,
      };
    },

    getDownloadUrl() {
      let downloadQuery = '';
      let separator = '?';
      const { collection } = this.options;
      const collectionQuery = collection ? this.options.collection.getQueryString() : '';
      const pageSize = collection ? this.options.collection.state.totalRecords : 25;
      const downloadParams = _.extend([], this.downloadParams);

      // Return empty string if no downloadBaseUrl
      if (_.isEmpty(this.downloadBaseUrl)) {
        return '';
      }

      // Append the total records count as the page size
      // NOTE: will only work if the Analytics API's max_page_size is large enough
      if (pageSize) {
        downloadParams.push({
          key: 'page_size',
          val: pageSize,
        });
      }

      if (collectionQuery !== '') {
        separator = '&';
      }
      downloadQuery = Utils.toQueryString(downloadParams, separator);

      return this.downloadBaseUrl + collectionQuery + downloadQuery;
    },

    updateDownloadLink() {
      // Set the href for the download button to the current download URL
      $(this.ui.dataDownloadButton).attr('href', this.getDownloadUrl());
    },
  });

  return DownloadDataView;
});
