define((require) => {
  'use strict';

  const _ = require('underscore');
  const TrackingModel = require('models/tracking-model');
  const DownloadDataView = require('components/download/views/download-data');
  const LearnerCollection = require('learners/common/collections/learners');

  describe('DownloadDataView', () => {
    beforeEach(function () {
      this.user = {};
    });

    it('has default options', function () {
      const downloadDataView = new DownloadDataView({
        collection: new LearnerCollection(
          [this.user],
          { url: 'http://example.com' },
        ),
      });
      const templateVars = downloadDataView.templateHelpers();
      expect(templateVars.hasDownloadData).toBe(false);
      expect(templateVars.trackCategory).toBe('download_file');
      expect(templateVars.downloadDataTitle).toBe('Download CSV');
      expect(templateVars.downloadDataMessage).toBe('Download search results to CSV');
      expect(templateVars.downloadUrl).toBe('');
    });

    it('accepts options overrides', function () {
      const downloadDataView = new DownloadDataView({
        collection: new LearnerCollection(
          [this.user],
          { url: 'http://example.com' },
        ),
        hasDownloadData: true,
        trackCategory: 'tracking-my-downloads',
        downloadDataTitle: 'Download My CSV',
        downloadDataMessage: 'Download my search results',
      });
      const templateVars = downloadDataView.templateHelpers();
      expect(templateVars.hasDownloadData).toBe(false);
      expect(templateVars.trackCategory).toBe('tracking-my-downloads');
      expect(templateVars.downloadDataTitle).toBe('Download My CSV');
      expect(templateVars.downloadDataMessage).toBe('Download my search results');
      expect(templateVars.downloadUrl).toBe('');
    });

    it('must have a downloadUrl to display the download button', function () {
      // Collections without downloadUrl get no download button
      let downloadDataView = new DownloadDataView({
        collection: new LearnerCollection(
          [this.user],
          { url: 'http://example.com' },
        ),
      });
      let templateVars = downloadDataView.templateHelpers();
      expect(downloadDataView.getDownloadUrl()).toBe('');
      expect(templateVars.hasDownloadData).toBe(false);
      expect(templateVars.downloadUrl).toBe('');

      // Collections with downloadUrl get a download button
      downloadDataView = new DownloadDataView({
        collection: new LearnerCollection(
          [this.user],
          {
            url: 'http://example.com',
            downloadUrl: '/list.csv',
          },
        ),
      });
      expect(downloadDataView.getDownloadUrl()).toBe('/list.csv?page=1&course_id=undefined');
      templateVars = downloadDataView.templateHelpers();
      expect(templateVars.hasDownloadData).toBe(true);
      expect(templateVars.downloadUrl).toBe('/list.csv?page=1&course_id=undefined');
    });

    it('changes the downloadUrl query string based on search filters', function () {
      // course_id but no active filters
      const collection = new LearnerCollection(
        [this.user],
        {
          url: 'http://example.com',
          downloadUrl: '/list.csv',
          courseId: 'course-v1:Demo:test',
        },
      );
      const downloadDataView = new DownloadDataView({
        collection,
      });

      expect(downloadDataView.getDownloadUrl()).toBe(
        '/list.csv'
                + '?page=1'
                + '&course_id=course-v1%3ADemo%3Atest',
      );

      // set a filter field
      collection.setFilterField('enrollment_mode', 'audit');
      expect(downloadDataView.getDownloadUrl()).toBe(
        '/list.csv'
                + '?enrollment_mode=audit'
                + '&page=1'
                + '&course_id=course-v1%3ADemo%3Atest',
      );

      // add another filter field (will maintain alphabetical order)
      collection.setFilterField('alpha', 'beta');
      expect(downloadDataView.getDownloadUrl()).toBe(
        '/list.csv'
                + '?enrollment_mode=audit'
                + '&alpha=beta'
                + '&page=1'
                + '&course_id=course-v1%3ADemo%3Atest',
      );

      // unset filter field restores original URL
      collection.unsetAllFilterFields();
      expect(downloadDataView.getDownloadUrl()).toBe(
        '/list.csv'
                + '?page=1'
                + '&course_id=course-v1%3ADemo%3Atest',
      );
    });

    it('allows query parameters to be in the downloadUrl', function () {
      const collection = new LearnerCollection(
        [this.user],
        {
          url: 'http://example.com',
          downloadUrl: '/list.csv?fields=abc,def&other=ghi',
          courseId: 'course-v1:Demo:test',
        },
      );
      const downloadDataView = new DownloadDataView({
        collection,
      });

      // query string parameters will be sorted alphabetically
      expect(downloadDataView.getDownloadUrl()).toBe(
        '/list.csv'
                + '?page=1'
                + '&course_id=course-v1%3ADemo%3Atest'
                + '&fields=abc%2Cdef'
                + '&other=ghi',
      );

      // set a filter field
      collection.setFilterField('enrollment_mode', 'audit');
      expect(downloadDataView.getDownloadUrl()).toBe(
        '/list.csv'
                + '?enrollment_mode=audit'
                + '&page=1'
                + '&course_id=course-v1%3ADemo%3Atest'
                + '&fields=abc%2Cdef'
                + '&other=ghi',
      );

      // unset filter field restores original URL
      collection.unsetAllFilterFields();
      expect(downloadDataView.getDownloadUrl()).toBe(
        '/list.csv'
                + '?page=1'
                + '&course_id=course-v1%3ADemo%3Atest'
                + '&fields=abc%2Cdef'
                + '&other=ghi',
      );
    });

    it('has sends tracking event on download', () => {
      _.each([{}, { trackCategory: 'another_category' }], (extraViewArgs) => {
        const collection = new LearnerCollection(
          [{}],
          {
            url: 'http://example.com',
            downloadUrl: '/list.csv?fields=abc,def',
            courseId: 'course-v1:Demo:test',
          },
        );
        const downloadDataView = new DownloadDataView(_.extend({
          collection,
          trackingModel: new TrackingModel(),
        }, extraViewArgs)).render();
        const downloadButton = downloadDataView.$(downloadDataView.ui.dataDownloadButton);
        const triggerSpy = spyOn(downloadDataView.options.trackingModel, 'trigger');
        const trackCategory = extraViewArgs.trackCategory || 'download_file';

        // Verify the tracking event is triggered when button is clicked.
        expect(downloadButton).toContainText('Download CSV');
        downloadButton.click();
        expect(triggerSpy).toHaveBeenCalledWith('segment:track', 'edx.bi.csv.downloaded', {
          category: trackCategory,
        });
      });
    });
  });
});
