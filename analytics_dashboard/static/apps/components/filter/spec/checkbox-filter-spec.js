define((require) => {
  'use strict';

  const $ = require('jquery');

  const CheckboxFilter = require('components/filter/views/checkbox-filter');
  const TrackingModel = require('models/tracking-model');
  const ListCollection = require('components/generic-list/common/collections/collection');

  describe('CheckboxFilter', () => {
    let checkboxFilter;
    let fixture;

    beforeEach(() => {
      fixture = setFixtures('<div id="basic-checkbox"><span id="app-focusable"/></div>');
      checkboxFilter = new CheckboxFilter({
        el: '#basic-checkbox',
        collection: new ListCollection([], { mode: 'client' }),
        trackingModel: new TrackingModel(),
        trackSubject: 'tracking-subject',
        appClass: 'app',
        filterKey: 'trees',
        filterValues: [{
          name: 'dogwood',
          displayName: 'Dogwood is a tree',
        }],
        sectionDisplayName: 'Checkbox of Trees',
      });
      checkboxFilter.render();
    });

    it('renders a checkbox', () => {
      expect(fixture).toContainElement('#filter-trees');
      expect(fixture).toContainElement('input#dogwood');
      expect($('#filter-trees label')).toContainText('Dogwood is a tree');
      expect($('.filters-label')).toContainText('Checkbox of Trees');
    });

    it('updates focus', () => {
      spyOn($.fn, 'focus');
      $('#filter-trees').trigger('change');
      expect($('#app-focusable').focus).toHaveBeenCalled();
    });

    it('triggers tracking', () => {
      const triggerSpy = spyOn(checkboxFilter.options.trackingModel, 'trigger');

      // refresh will trigger a page reload, so mocking it pretends it happened
      spyOn(checkboxFilter.options.collection, 'refresh');
      $('input#dogwood').prop('checked', true);
      $('#filter-trees').trigger('change');
      expect(triggerSpy).toHaveBeenCalledWith('segment:track', 'edx.bi.tracking-subject.filtered', {
        category: 'dogwood',
      });
    });
  });
});
