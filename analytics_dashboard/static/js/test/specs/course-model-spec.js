define(['models/course-model'], function(CourseModel) {
    'use strict';
    // this is a test that will always pass just so that we have something for
    // jasmine to test with initially
    describe('Course model', function () {
        it('should be empty', function () {
            var model = new CourseModel();
            expect(model.isEmpty()).toBe(true);
        });
    });

    describe('Course model', function () {
        it('should have an ID', function () {
            var model = new CourseModel({courseId: 'test'});
            expect(model.isEmpty()).toBe(false);
        });
    });
});
