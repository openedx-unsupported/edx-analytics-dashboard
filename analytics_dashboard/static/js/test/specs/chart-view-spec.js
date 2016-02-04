define(['d3', 'models/course-model', 'views/chart-view'], function(d3, CourseModel, ChartView) {
    'use strict';

    describe('Chart view', function () {
        it('should assemble data for nvd3', function () {
            var model = new CourseModel(),
                view = new ChartView({
                    model: model,
                    el: document.createElement('div'),
                    modelAttribute: 'trends',
                    trends: [
                        {
                            key: 'trendA',
                            title: 'A Label',
                            color: '#8DA0CB'
                        },
                        {
                            key: 'trendB',
                            title: 'B Label'
                        }
                    ],
                    title: 'Trend Title',
                    x: {
                        title: 'Title X',
                        // key in the data
                        key: 'date'
                    },
                    y: {
                        title: 'Title Y',
                        key: 'yData'
                    }
                }),
                assembledData,
                actualTrend,
                explicitXTicks;

            view.render = jasmine.createSpy('render');
            expect(view.render).not.toHaveBeenCalled();

            // mock getChart (otherwise, an error is thrown)
            view.getChart = jasmine.createSpy('getChart');

            // phantomjs doesn't have the bind method on function object
            // (see https://github.com/novus/nvd3/issues/367) and nvd3 will
            // throw an error when it tries to render (when trend data is set).
            try {
                model.set('trends', [
                    {
                        date: '2014-01-01',
                        trendA: 10,
                        trendB: 0
                    },
                    {
                        date: '2014-01-02',
                        trendA: 20,
                        trendB: 1000
                    }
                ]);
            } catch (e) {
                if (e.name !== 'TypeError') {
                    throw e;
                }
            }

            // check that x data can be parsed correctly
            expect(view.parseXData({date: '2014-01-01'})).toBe('2014-01-01');

            // check the data passed to nvd3
            assembledData = view.assembleTrendData();
            expect(assembledData.length).toBe(2);

            actualTrend = assembledData[0];
            // 'key' is the title/label of the of the trend
            expect(actualTrend.key).toBe('A Label');
            expect(actualTrend.values.length).toBe(2);
            expect(actualTrend.values).toContain({date: '2014-01-01', yData: 10, trendA: 10, trendB: 0});
            expect(actualTrend.values).toContain({date: '2014-01-02', yData: 20, trendA: 20, trendB: 1000});
            expect(actualTrend.color).toBe('#8DA0CB');

            actualTrend = assembledData[1];
            expect(actualTrend.key).toBe('B Label');
            expect(actualTrend.values.length).toBe(2);
            expect(actualTrend.values).toContain({date: '2014-01-01', yData: 0, trendA: 10, trendB: 0});
            expect(actualTrend.values).toContain({date: '2014-01-02', yData: 1000, trendA: 20, trendB: 1000});
            expect(actualTrend.color).toBeUndefined();

            explicitXTicks = view.getExplicitXTicks(assembledData);
            expect(explicitXTicks.length).toBe(2);
            expect(explicitXTicks[0]).toBe('2014-01-01');
            expect(explicitXTicks[1]).toBe('2014-01-02');
        });

    });

    describe('Chart view', function () {
        it('should build x label mappings', function () {
            var model = new CourseModel(),
                view = new ChartView({
                    model: model,
                    el: document.createElement('div'),
                    modelAttribute: 'assignments',
                    trends: [
                        {
                            key: 'correct_submissions',
                            title: 'Correct Submissions',
                            color: '#4BB4FB'
                        },
                        {
                            key: 'incorrect_submissions',
                            title: 'Incorrect Submissions',
                            color: '#CA0061'
                        }
                    ],
                    x: {key: 'id', displayKey: 'name'},
                    y: {key: 'count'}
                }),
                mapping;

            view.render = jasmine.createSpy('render');
            expect(view.render).not.toHaveBeenCalled();

            // mock getChart (otherwise, an error is thrown)
            view.getChart = jasmine.createSpy('getChart');

            // phantomjs doesn't have the bind method on function object
            // (see https://github.com/novus/nvd3/issues/367) and nvd3 will
            // throw an error when it tries to render (when trend data is set).
            try {
                model.set('assignments', [
                    {
                        id: 'assignment_1',
                        name: 'Assignment 1',
                        correct_submissions: 100,
                        incorrect_submissions: 200
                    },
                    {
                        id: 'assignment_2',
                        name: 'Assignment 2',
                        correct_submissions: 100,
                        incorrect_submissions: 200
                    }
                ]);
            } catch (e) {
                if (e.name !== 'TypeError') {
                    throw e;
                }
            }

            // check the data passed to nvd3
            mapping = view.buildXLabelMapping();

            expect(mapping.assignment_1).toBe('Assignment 1');
            expect(view.formatXTick('assignment_1')).toBe('Assignment 1');

            expect(mapping.assignment_2).toBe('Assignment 2');
            expect(view.formatXTick('assignment_2')).toBe('Assignment 2');
        });

    });

    describe('Chart view', function () {
        it('should format y values', function () {
            var view = new ChartView({
                    el: document.createElement('div'),
                    model: new CourseModel()
                });

            expect(view.getYAxisFormat()(1000)).toBe('1000');

            view = new ChartView({
                el: document.createElement('div'),
                model: new CourseModel(),
                dataType: 'percent'
            });
            expect(view.getYAxisFormat()(0.1024)).toBe('10.2%');
        });

    });
});
