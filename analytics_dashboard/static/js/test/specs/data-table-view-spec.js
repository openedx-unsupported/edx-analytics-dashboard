define(['models/course-model', 'views/data-table-view'], (CourseModel, DataTableView) => {
  'use strict';

  describe('Data Table View', () => {
    it('should format display of the max number (e.g. 100+)', () => {
      const dataType = 'myData';
      const renderType = 'display';
      const model = new CourseModel();
      const view = new DataTableView({
        el: document.createElement('div'),
        model,
        modelAttribute: 'ages',
      });
      const maxNumberFunc = view.createFormatMaxNumberFunc(dataType, 100);
      const row = {};

      view.renderIfDataAvailable();
      row[dataType] = 50;
      expect(maxNumberFunc(row, renderType)).toBe('50');

      row[dataType] = 100;
      expect(maxNumberFunc(row, renderType)).toBe('100+');

      // non-numbers will be returned without formatting
      row[dataType] = 'unknown';
      expect(maxNumberFunc(row, renderType)).toBe('unknown');
    });

    it('should format display of a percentage', () => {
      const dataType = 'myData';
      const renderType = 'display';
      const model = new CourseModel();
      const view = new DataTableView({
        el: document.createElement('div'),
        model,
        modelAttribute: 'ages',
        replaceZero: '-',
      });
      const percentFunc = view.createFormatPercentFunc(dataType, 100);
      const row = {};

      view.renderIfDataAvailable();
      row[dataType] = 0.05;
      expect(percentFunc(row, renderType)).toBe('5.0%');

      row[dataType] = 0.00001;
      expect(percentFunc(row, renderType)).toBe('< 1%');

      row[dataType] = 1;
      expect(percentFunc(row, renderType)).toBe('100.0%');

      row[dataType] = 0;
      expect(percentFunc(row, renderType)).toBe('-');
    });

    it('should format display of a date', () => {
      const dataType = 'myData';
      const renderType = 'display';
      const model = new CourseModel();
      const view = new DataTableView({
        el: document.createElement('div'),
        model,
        modelAttribute: 'ages',
      });
      const dateFunc = view.createFormatDateFunc(dataType, 100);
      const row = {};

      view.renderIfDataAvailable();
      row[dataType] = new Date(2014, 0, 1);
      expect(dateFunc(row, renderType)).toBe('January 1, 2014');
    });

    it('should format display of a boolean', () => {
      const dataType = 'myData';
      const renderType = 'display';
      const model = new CourseModel();
      const view = new DataTableView({
        el: document.createElement('div'),
        model,
        modelAttribute: 'ages',
      });
      const func = view.createFormatBoolFunc(dataType);
      const row = {};

      view.renderIfDataAvailable();
      row[dataType] = true;
      expect(func(row, renderType)).toBe('Correct');

      row[dataType] = false;
      expect(func(row, renderType)).toBe('-');
    });

    it('should format display of a date', () => {
      const dataType = 'myData';
      const renderType = 'display';
      const model = new CourseModel();
      const view = new DataTableView({
        el: document.createElement('div'),
        model,
        modelAttribute: 'ages',
      });
      const func = view.createFormatHasNullFunc(dataType);
      const row = {};

      view.renderIfDataAvailable();
      row[dataType] = 'Not Null';
      expect(func(row, renderType)).toBe('Not Null');

      row[dataType] = null;
      expect(func(row, renderType)).toBe('(empty)');
    });

    it('should format display of a formatted number', () => {
      const dataType = 'myData';
      const renderType = 'display';
      const model = new CourseModel();
      const view = new DataTableView({
        el: document.createElement('div'),
        model,
        modelAttribute: 'ages',
        replaceZero: '-',
      });
      const func = view.createFormatNumberFunc(dataType);
      const row = {};

      view.renderIfDataAvailable();
      row[dataType] = 0;
      expect(func(row, renderType)).toBe('-');

      row[dataType] = 3;
      expect(func(row, renderType)).toBe('3');

      row[dataType] = 1234567;
      expect(func(row, renderType)).toBe('1,234,567');
    });
  });
});
