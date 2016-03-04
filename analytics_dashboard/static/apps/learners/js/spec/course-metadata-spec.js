require(['learners/js/models/course-metadata'], function (CourseMetadataModel) {
    'use strict';

    describe('CourseMetadataModel', function () {
        it('sets its url through the initialize function', function () {
            var url = '/resource/';
            expect(new CourseMetadataModel(null, {url: url}).url()).toBe(url);
        });
    });
});
