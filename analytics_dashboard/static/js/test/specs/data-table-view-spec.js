define(['models/course-model', 'views/data-table-view'], function(CourseModel, DataTableView) {
    'use strict';

    describe('Data Table View', function () {
        it('should format display of the max number (e.g. 100+)', function() {
            var dataType = 'myData',
                renderType = 'display',
                model = new CourseModel(),
                view = new DataTableView({
                    el: document.createElement('div'),
                    model: model,
                    modelAttribute: 'ages'
                }),
                maxNumberFunc = view.createFormatMaxNumberFunc(dataType, 100),
                row = {};

            row[dataType] = 50;
            expect(maxNumberFunc(row, renderType)).toBe('50');

            row[dataType] = 100;
            expect(maxNumberFunc(row, renderType)).toBe('100+');

            // non-numbers will be returned without formatting
            row[dataType] = 'unknown';
            expect(maxNumberFunc(row, renderType)).toBe('unknown');
        });

        it('should format display of a percentage', function() {
            var dataType = 'myData',
                renderType = 'display',
                model = new CourseModel(),
                view = new DataTableView({
                    el: document.createElement('div'),
                    model: model,
                    modelAttribute: 'ages'
                }),
                percentFunc = view.createFormatPercentFunc(dataType, 100),
                row = {};

            row[dataType] = 0.05;
            expect(percentFunc(row, renderType)).toBe('5.0%');

            row[dataType] = 0.00001;
            expect(percentFunc(row, renderType)).toBe('< 1%');

            row[dataType] = 1;
            expect(percentFunc(row, renderType)).toBe('100.0%');
        });

        it('should format display of a date', function() {
            var dataType = 'myData',
                renderType = 'display',
                model = new CourseModel(),
                view = new DataTableView({
                    el: document.createElement('div'),
                    model: model,
                    modelAttribute: 'ages'
                }),
                dateFunc = view.createFormatDateFunc(dataType, 100),
                row = {};

            row[dataType] = new Date(2014, 0, 1);
            expect(dateFunc(row, renderType)).toBe('January 1, 2014');
        });

    });

});
