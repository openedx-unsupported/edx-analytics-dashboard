define((require) => {
  'use strict';

  const $ = require('jquery');

  const DropDownFilter = require('components/filter/views/drop-down-filter');
  const TrackingModel = require('models/tracking-model');
  const ListCollection = require('components/generic-list/common/collections/collection');

  describe('DropDownFilter', () => {
    let dropDownFilter;
    let fixture;

    beforeEach(() => {
      fixture = setFixtures('<div id="basic-drop-down"><span id="app-focusable"/></div>');
      dropDownFilter = new DropDownFilter({
        el: '#basic-drop-down',
        collection: new ListCollection([], { mode: 'client' }),
        trackingModel: new TrackingModel(),
        trackSubject: 'tracking',
        appClass: 'app',
        filterKey: 'flowers',
        filterValues: [{
          name: 'tulips',
          displayName: 'Flower: tulips',
          count: 1000,
        }],
        sectionDisplayName: 'Drop Down Title',
      });
      dropDownFilter.render();
    });

    it('renders a drop down', () => {
      const items = dropDownFilter.$el.find('option');
      expect(fixture).toContainElement('#filter-flowers');
      expect(dropDownFilter.$el.find('label')).toContainText('Drop Down Title');
      expect(items.length).toEqual(2);
      expect(items[0]).toContainText('All');
      expect(items[1]).toContainText('Flower: tulips (1,000)');
    });

    it('updates focus', () => {
      spyOn($.fn, 'focus');
      $('#filter-flowers').trigger('change');
      expect($('#app-focusable').focus).toHaveBeenCalled();
    });

    it('triggers tracking', () => {
      const triggerSpy = spyOn(dropDownFilter.options.trackingModel, 'trigger');
      $('#filter-flowers').trigger('change');
      expect(triggerSpy).toHaveBeenCalledWith('segment:track', 'edx.bi.tracking.filtered', {
        category: 'flowers',
      });
    });
  });
});
