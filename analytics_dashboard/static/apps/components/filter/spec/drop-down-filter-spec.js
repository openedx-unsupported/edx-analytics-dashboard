define(function(require) {
    'use strict';

    var $ = require('jquery'),

        DropDownFilter = require('components/filter/views/drop-down-filter'),
        TrackingModel = require('models/tracking-model'),
        ListCollection = require('components/generic-list/common/collections/collection');

    describe('DropDownFilter', function() {
        var dropDownFilter,
            fixture;

        beforeEach(function() {
            fixture = setFixtures('<div id="basic-drop-down"><span id="app-focusable"/></div>');
            dropDownFilter = new DropDownFilter({
                el: '#basic-drop-down',
                collection: new ListCollection([], {mode: 'client'}),
                trackingModel: new TrackingModel(),
                trackSubject: 'tracking',
                appClass: 'app',
                filterKey: 'flowers',
                filterValues: [{
                    name: 'tulips',
                    displayName: 'Flower: tulips',
                    count: 1000
                }],
                sectionDisplayName: 'Drop Down Title'
            });
            dropDownFilter.render();
        });

        it('renders a drop down', function() {
            var items = dropDownFilter.$el.find('option');
            expect(fixture).toContainElement('#filter-flowers');
            expect(dropDownFilter.$el.find('label')).toContainText('Drop Down Title');
            expect(items.length).toEqual(2);
            expect(items[0]).toContainText('All');
            expect(items[1]).toContainText('Flower: tulips (1,000)');
        });

        it('updates focus', function() {
            spyOn($.fn, 'focus');
            $('#filter-flowers').trigger('change');
            expect($('#app-focusable').focus).toHaveBeenCalled();
        });

        it('triggers tracking', function() {
            var triggerSpy = spyOn(dropDownFilter.options.trackingModel, 'trigger');
            $('#filter-flowers').trigger('change');
            expect(triggerSpy).toHaveBeenCalledWith('segment:track', 'edx.bi.tracking.filtered', {
                category: 'flowers'
            });
        });
    });
});
