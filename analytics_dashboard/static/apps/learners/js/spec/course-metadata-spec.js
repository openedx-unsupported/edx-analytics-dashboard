define(['learners/js/models/course-metadata'], function (CourseMetadataModel) {
    'use strict';

    describe('CourseMetadataModel', function () {
        var server;

        beforeEach(function () {
            jasmine.clock().install();
            server = sinon.fakeServer.create();
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

        it('categorizes engagement values', function () {
            var engagementRanges = {
                    problems_attempted: {
                        below_average: [0, 10],
                        average: [11, 25],
                        above_average: [26, null]
                    },
                    problem_attempts_per_completed: {
                        below_average: [null, 1],
                        average: [2, 5.8],
                        above_average: [null, null]
                    }
                },
                courseMetadata = new CourseMetadataModel();

            courseMetadata.set('engagement_ranges', engagementRanges);
            expect(courseMetadata.getEngagementCategory('problems_attempted', 9)).toBe('below_average');
            expect(courseMetadata.getEngagementCategory('problems_attempted', 12)).toBe('average');
            expect(courseMetadata.getEngagementCategory('problems_attempted', 100)).toBe('above_average');

            expect(courseMetadata.getEngagementCategory('problem_attempts_per_completed', 0)).toBe('below_average');
            expect(courseMetadata.getEngagementCategory('problem_attempts_per_completed', 3.3)).toBe('average');
            expect(courseMetadata.getEngagementCategory('problem_attempts_per_completed', 100)).toBe(undefined);
        });

    });
});
