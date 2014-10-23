define(['models/course-model', 'views/trends-view'], function(CourseModel, TrendsView) {
    'use strict';

    describe('Trends view', function () {
        it('should assemble format x-axis ticks', function () {
            var view = new TrendsView({
                    model: new CourseModel(),
                    modelAttribute: 'trends',
                    x: {
                        title: 'Title X',
                        // key in the data
                        key: 'date'
                    }
                });
            expect(view.formatXTick('2014-06-15')).toBe('6/15');
        });

        it('should parse x data as a timestamp', function () {
            var view = new TrendsView({
                    model: new CourseModel(),
                    modelAttribute: 'trends',
                    x: {
                        title: 'Title X',
                        // key in the data
                        key: 'date'
                    }
                });
            expect(view.parseXData({date: '2014-06-15'})).toBe(1402790400000);
        });
    });
});
