define(['views/enrollment-trend-view', 'models/course-model'], function (EnrollmentTrendView, CourseModel) {
    'use strict';

    describe('EnrollmentTrendView', function () {
        var model, view;

        beforeEach(function () {
            model = new CourseModel({courseId: 'edX/DemoX/Demo_Course'});
            view = new EnrollmentTrendView({model: model, modelAttribute: 'enrollmentTrends'})
        });

        describe('_convertDate', function () {
            it('should convert a string date to UTC', function () {
                expect(view._convertDate('2014-01-01')).toEqual(1388534400000);
                expect(view._convertDate('2014-12-31')).toEqual(1419984000000);
            });
        });

        describe('_formatData', function () {
            it('should zip up enrollment dates with counts', function () {
                var input = [
                    {count: 0, date: '2014-01-01'},
                    {count: 4567, date: '2014-12-31'}
                ], expected = [
                    [1388534400000, 0],
                    [1419984000000, 4567]
                ];

                expect(view._formatData(input)).toEqual(expected);
            });
        });
    });
});
