require(['learners/js/models/course-metadata'], function (CourseMetadataModel) {
    'use strict';

    describe('CourseMetadataModel', function () {
        var server;

        beforeEach(function () {
            jasmine.clock().install();
            server = sinon.fakeServer.create(); // jshint ignore:line
        });

        afterEach(function () {
            jasmine.clock().uninstall();
            server.restore();
        });

        it('sets its url through the initialize function', function () {
            var url = '/resource/';
            expect(new CourseMetadataModel(null, {url: url}).url()).toBe(url);
        });

        it('triggers a serverError event on server errors', function () {
            var courseMetadata = new CourseMetadataModel(null, {url: '/resource/'});
            spyOn(courseMetadata, 'trigger');
            courseMetadata.fetch();
            server.requests[server.requests.length - 1].respond(500, {}, '{}');
            expect(courseMetadata.trigger).toHaveBeenCalledWith('serverError', 500, {});
        });

        it('triggers a networkError event on network errors', function () {
            var courseMetadata = new CourseMetadataModel(null, {url: '/resource/'});
            spyOn(courseMetadata, 'trigger');
            courseMetadata.fetch({timeout: 1});
            jasmine.clock().tick(2);
            expect(courseMetadata.trigger).toHaveBeenCalledWith('networkError', 'timeout');
        });
    });
});
