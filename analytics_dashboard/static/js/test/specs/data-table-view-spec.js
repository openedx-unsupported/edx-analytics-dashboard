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
                    modelAttribute: 'ages',
                    replaceZero: '-'
                }),
                percentFunc = view.createFormatPercentFunc(dataType, 100),
                row = {};

            row[dataType] = 0.05;
            expect(percentFunc(row, renderType)).toBe('5.0%');

            row[dataType] = 0.00001;
            expect(percentFunc(row, renderType)).toBe('< 1%');

            row[dataType] = 1;
            expect(percentFunc(row, renderType)).toBe('100.0%');

            row[dataType] = 0;
            expect(percentFunc(row, renderType)).toBe('-');
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

        it('should format display of a boolean', function() {
            var dataType = 'myData',
                renderType = 'display',
                model = new CourseModel(),
                view = new DataTableView({
                    el: document.createElement('div'),
                    model: model,
                    modelAttribute: 'ages'
                }),
                func = view.createFormatBoolFunc(dataType),
                row = {};

            row[dataType] = true;
            expect(func(row, renderType)).toBe('Correct');

            row[dataType] = false;
            expect(func(row, renderType)).toBe('-');
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
                func = view.createFormatHasNullFunc(dataType),
                row = {};

            row[dataType] = 'Not Null';
            expect(func(row, renderType)).toBe('Not Null');

            row[dataType] = null;
            expect(func(row, renderType)).toBe('(empty)');
        });

        it('should format display of a formatted number', function() {
            var dataType = 'myData',
                renderType = 'display',
                model = new CourseModel(),
                view = new DataTableView({
                    el: document.createElement('div'),
                    model: model,
                    modelAttribute: 'ages',
                    replaceZero: '-'
                }),
                func = view.createFormatNumberFunc(dataType),
                row = {};

            row[dataType] = 0;
            expect(func(row, renderType)).toBe('-');

            row[dataType] = 3;
            expect(func(row, renderType)).toBe('3');

            row[dataType] = 1234567;
            expect(func(row, renderType)).toBe('1,234,567');
        });

    });

});
