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

        it('should convert a string date to UTC', function () {
            var model = new CourseModel(),
                dates = ['2014-01-01', '2014-12-31'],
                expected = [1388534400000, 1419984000000],
                actual;

            // do the conversion
            actual = model.convertDate(dates[0]);
            expect(actual).toBe(expected[0]);

            actual = model.convertDate(dates[1]);
            expect(actual).toBe(expected[1]);
        });

        it('should zip up enrollment dates with counts', function () {
            var model = new CourseModel(),
                enrollmentTrends = [
                    {count: 0, date: '2014-01-01'},
                    {count: 4567, date: '2014-12-31'}
                ],
                expectedDates = [1388534400000, 1419984000000],
                series;

            model.set('enrollmentTrends', enrollmentTrends);

            // do the conversion
            series = model.getEnrollmentSeries();

            expect(series.length).toBe(2);

            expect(series[0][0]).toBe(expectedDates[0]);
            expect(series[0][1]).toBe(0);

            expect(series[1][0]).toBe(expectedDates[1]);
            expect(series[1][1]).toBe(4567);
        });

    });

});
