define(function(require) {
    'use strict';

    var _ = require('underscore'),
        TrackingModel = require('models/tracking-model'),
        DownloadDataView = require('components/download/views/download-data'),
        LearnerCollection = require('learners/common/collections/learners');

    describe('DownloadDataView', function() {
        beforeEach(function() {
            this.user = {};
        });

        it('has default options', function() {
            var downloadDataView = new DownloadDataView({
                    collection: new LearnerCollection(
                        [this.user],
                        {url: 'http://example.com'}
                    )
                }),
                templateVars = downloadDataView.templateHelpers();
            expect(templateVars.hasDownloadData).toBe(false);
            expect(templateVars.trackCategory).toBe('download_file');
            expect(templateVars.downloadDataTitle).toBe('Download CSV');
            expect(templateVars.downloadDataMessage).toBe('Download search results to CSV');
            expect(templateVars.downloadUrl).toBe('');
        });

        it('accepts options overrides', function() {
            var downloadDataView = new DownloadDataView({
                    collection: new LearnerCollection(
                        [this.user],
                        {url: 'http://example.com'}
                    ),
                    hasDownloadData: true,
                    trackCategory: 'tracking-my-downloads',
                    downloadDataTitle: 'Download My CSV',
                    downloadDataMessage: 'Download my search results'
                }),
                templateVars = downloadDataView.templateHelpers();
            expect(templateVars.hasDownloadData).toBe(false);
            expect(templateVars.trackCategory).toBe('tracking-my-downloads');
            expect(templateVars.downloadDataTitle).toBe('Download My CSV');
            expect(templateVars.downloadDataMessage).toBe('Download my search results');
            expect(templateVars.downloadUrl).toBe('');
        });

        it('must have a downloadUrl to display the download button', function() {
            // Collections without downloadUrl get no download button
            var downloadDataView = new DownloadDataView({
                    collection: new LearnerCollection(
                        [this.user],
                        {url: 'http://example.com'}
                    )
                }),
                templateVars = downloadDataView.templateHelpers();
            expect(downloadDataView.getDownloadUrl()).toBe('');
            expect(templateVars.hasDownloadData).toBe(false);
            expect(templateVars.downloadUrl).toBe('');

            // Collections with downloadUrl get a download button
            downloadDataView = new DownloadDataView({
                collection: new LearnerCollection(
                    [this.user],
                    {
                        url: 'http://example.com',
                        downloadUrl: '/list.csv'
                    }
                )
            });
            expect(downloadDataView.getDownloadUrl()).toBe('/list.csv?page=1&course_id=undefined');
            templateVars = downloadDataView.templateHelpers();
            expect(templateVars.hasDownloadData).toBe(true);
            expect(templateVars.downloadUrl).toBe('/list.csv?page=1&course_id=undefined');
        });

        it('changes the downloadUrl query string based on search filters', function() {
            // course_id but no active filters
            var collection = new LearnerCollection([this.user],
                {
                    url: 'http://example.com',
                    downloadUrl: '/list.csv',
                    courseId: 'course-v1:Demo:test'
                }),
                downloadDataView = new DownloadDataView({
                    collection: collection
                });

            expect(downloadDataView.getDownloadUrl()).toBe(
                '/list.csv' +
                '?page=1' +
                '&course_id=course-v1%3ADemo%3Atest'
            );

            // set a filter field
            collection.setFilterField('enrollment_mode', 'audit');
            expect(downloadDataView.getDownloadUrl()).toBe(
                '/list.csv' +
                '?enrollment_mode=audit' +
                '&page=1' +
                '&course_id=course-v1%3ADemo%3Atest'
            );

            // add another filter field (will maintain alphabetical order)
            collection.setFilterField('alpha', 'beta');
            expect(downloadDataView.getDownloadUrl()).toBe(
                '/list.csv' +
                '?enrollment_mode=audit' +
                '&alpha=beta' +
                '&page=1' +
                '&course_id=course-v1%3ADemo%3Atest'
            );

            // unset filter field restores original URL
            collection.unsetAllFilterFields();
            expect(downloadDataView.getDownloadUrl()).toBe(
                '/list.csv' +
                '?page=1' +
                '&course_id=course-v1%3ADemo%3Atest'
            );
        });

        it('allows query parameters to be in the downloadUrl', function() {
            var collection = new LearnerCollection([this.user],
                {
                    url: 'http://example.com',
                    downloadUrl: '/list.csv?fields=abc,def&other=ghi',
                    courseId: 'course-v1:Demo:test'
                }),
                downloadDataView = new DownloadDataView({
                    collection: collection
                });

            // query string parameters will be sorted alphabetically
            expect(downloadDataView.getDownloadUrl()).toBe(
                '/list.csv' +
                '?page=1' +
                '&course_id=course-v1%3ADemo%3Atest' +
                '&fields=abc%2Cdef' +
                '&other=ghi'
            );

            // set a filter field
            collection.setFilterField('enrollment_mode', 'audit');
            expect(downloadDataView.getDownloadUrl()).toBe(
                '/list.csv' +
                '?enrollment_mode=audit' +
                '&page=1' +
                '&course_id=course-v1%3ADemo%3Atest' +
                '&fields=abc%2Cdef' +
                '&other=ghi'
            );

            // unset filter field restores original URL
            collection.unsetAllFilterFields();
            expect(downloadDataView.getDownloadUrl()).toBe(
                '/list.csv' +
                '?page=1' +
                '&course_id=course-v1%3ADemo%3Atest' +
                '&fields=abc%2Cdef' +
                '&other=ghi'
            );
        });

        it('has sends tracking event on download', function() {
            _.each([{}, {trackCategory: 'another_category'}], function(extraViewArgs) {
                var collection = new LearnerCollection([{}],
                    {
                        url: 'http://example.com',
                        downloadUrl: '/list.csv?fields=abc,def',
                        courseId: 'course-v1:Demo:test'
                    }),
                    downloadDataView = new DownloadDataView(_.extend({
                        collection: collection,
                        trackingModel: new TrackingModel()
                    }, extraViewArgs)).render(),
                    downloadButton = downloadDataView.$(downloadDataView.ui.dataDownloadButton),
                    triggerSpy = spyOn(downloadDataView.options.trackingModel, 'trigger'),
                    trackCategory = extraViewArgs.trackCategory || 'download_file';

                // Verify the tracking event is triggered when button is clicked.
                expect(downloadButton).toContainText('Download CSV');
                downloadButton.click();
                expect(triggerSpy).toHaveBeenCalledWith('segment:track', 'edx.bi.csv.downloaded', {
                    category: trackCategory
                });
            });
        });
    });
});
