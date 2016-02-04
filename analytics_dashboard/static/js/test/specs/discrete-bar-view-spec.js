define(['models/course-model', 'views/discrete-bar-view'], function(CourseModel, DiscreteBarView) {
    'use strict';

    describe('Discrete bar view', function () {
        it('should format labels for display', function () {
            var model = new CourseModel(),
                view = new DiscreteBarView({
                    model: model,
                    el: document.createElement('div'),
                    modelAttribute: 'data',
                    trends: [{
                        color: function(bar, index) {
                            return index === 0 ? '#ffffff' : '#000000';
                        }
                    }],
                    x: { key: 'category' },
                    y: { key: 'count' },
                    dataType: 'percent'
                }),
                data = [
                    {
                        category: 'Cloudy',
                        count: 15
                    },
                    {
                        category: null,
                        count: 50
                    }
                ],
                assembledData;

            view.render = jasmine.createSpy('render');
            expect(view.render).not.toHaveBeenCalled();

            // mock getChart (otherwise, an error is thrown)
            view.getChart = jasmine.createSpy('getChart');

            // phantomjs doesn't have the bind method on function object
            // (see https://github.com/novus/nvd3/issues/367) and nvd3 will
            // throw an error when it tries to render (when trend data is set).
            try {
                model.set('data', data);
            } catch (e) {
                if (e.name !== 'TypeError') {
                    throw e;
                }
            }

            expect(view.options.barSelector).toBe('.discreteBar');
            expect(view.getChart).toHaveBeenCalled();

            expect(view.parseXData(data[0])).toBe('Cloudy');
            expect(view.formatXValue(data[0].category)).toBe('Cloudy');

            expect(view.parseXData(data[1])).toBe(null);
            expect(view.formatXValue(data[1].category)).toBe('(empty)');

            expect(view.getYAxisFormat()(0.5)).toBe('50.0%');

            assembledData = view.assembleTrendData();
            expect(assembledData.length).toBe(1);
            expect(assembledData[0].color({}, 0)).toBe('#ffffff');
            expect(assembledData[0].color({}, 1)).toBe('#000000');
        });

    });
});
