define(['models/course-model'], function(CourseModel) {
    'use strict';

    describe('Course model', function () {
        it('should be empty', function () {
            var model = new CourseModel();
            expect(model.isEmpty()).toBe(true);
        });

        it('should have an ID', function () {
            var model = new CourseModel({courseId: 'test'});
            expect(model.isEmpty()).toBe(false);
            expect(model.get('courseId')).toBe('test');
        });

        it('should determine if trend data is available ', function () {
            var model = new CourseModel();

            // the trend dataset is entirely unavailable
            expect(model.hasTrend('noDataProvided', 'test')).toBe(false);

            // the dataset is now available
            model.set('trendData', [{data: 10}, {data: 20}]);
            expect(model.hasTrend('trendData', 'data')).toBe(true);
            expect(model.hasTrend('trendData', 'notFound')).toBe(false);
        });

    });
});
