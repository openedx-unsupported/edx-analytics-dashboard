define(['underscore', 'models/course-model', 'views/stacked-bar-view'], function(_, CourseModel, StackedBarView) {
    'use strict';

    describe('Stacked bar view', function () {
        it('should format labels for display', function () {
            var model = new CourseModel(),
                view = new StackedBarView({
                    model: model,
                    el: document.createElement('div'),
                    modelAttribute: 'data',
                    trends: [
                        {
                            key: 'correct_submissions',
                            title: 'Correct',
                            color: '#4BB4FB'
                        },
                        {
                            key: 'incorrect_submissions',
                            title: 'Incorrect',
                            color: '#CA0061'
                        }
                    ],
                    x: { key: 'id', displayKey: 'name' },
                    y: { key: 'count' },
                    click: function() {}
                }),
                data = [
                    {
                        id: 123,
                        name: 'sameName',
                        correct_submissions: 100,
                        incorrect_submissions: 200
                    },
                    {
                        id: 456,
                        name: 'sameName',
                        correct_submissions: 30,
                        incorrect_submissions: 10
                    }
                ],
                assembledData,
                xLabelMapping;

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

            expect(view.options.barSelector).toBe('.nv-bar');
            expect(view.getChart).toHaveBeenCalled();

            xLabelMapping = view.buildXLabelMapping();
            expect(view.parseXData(data[0])).toBe(123);
            expect(view.formatXTick(123)).toBe('sameName');
            expect(xLabelMapping[123]).toBe('sameName');

            expect(view.parseXData(data[1])).toBe(456);
            expect(view.formatXTick(456)).toBe('sameName');
            expect(xLabelMapping[456]).toBe('sameName');

            assembledData = view.assembleTrendData();
            expect(assembledData.length).toBe(2);
            expect(assembledData[0].color).toBe('#4BB4FB');
            expect(assembledData[1].color).toBe('#CA0061');
        });

        it('should have default options', function () {
            var view = new StackedBarView({model: new CourseModel(), modelAttribute: 'data'}),
                trend = {
                    value: 200,
                    options: {percent_key: 'percent'},
                    point: {percent: 0.1239}
                },
                expectedTooltip = '200 (12.4%)';
            expect(_.isFunction(view.options.click)).toBe(true);
            expect(view.options.truncateXTicks).toBe(true);
            expect(view.options.barSelector).toBe('.nv-bar');
            expect(view.options.barSelector).toBe('.nv-bar');
            expect(view.options.x).toEqual({key: 'id', displayKey: 'name'});
            expect(view.options.y).toEqual({key: 'count'});
            expect(view.options.interactiveTooltipValueTemplate(trend)).toBe(expectedTooltip);
        });

    });
});
