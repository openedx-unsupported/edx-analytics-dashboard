define(function(require) {
    'use strict';

    var $ = require('jquery'),
        _ = require('underscore'),
        moment = require('moment'),

        EngagementTimelineModel = require('learners/common/models/engagement-timeline'),
        EngagementTimelineView = require('learners/detail/views/engagement-timeline');

    describe('EngagementTimelineView', function() {
        var expectLegendRendered,
            expectTimelineRendered,
            expectXAxisRendered,
            fixtureClass,
            getTimelineModel;

        expectLegendRendered = function(view) {
            var labels,
                legendItems;
            labels = ['Discussion Contributions', 'Problems Correct', 'Videos Viewed'];
            legendItems = view.$('.nv-legend-text');
            expect(labels.length).toEqual(legendItems.length);
            _.each(labels, function(label, index) {
                expect(legendItems[index]).toHaveText(label);
            });
        };

        expectXAxisRendered = function(view) {
            var dates,
                xLabels;
            dates = _.map(view.model.get('days'), function(day) {
                return moment.utc(Date.parse(day.date)).format('D MMM YYYY');
            });
            // Note that NVD3 unfortunately doesn't semantically order the
            // x-axis labels in the DOM, so we can't verify each label in order.
            xLabels = _.chain(view.$('.nv-x.nv-axis text'))
                .filter(function(el) {
                    return $(el).text() !== '';
                })
                .map(function(el) {
                    return $(el).text();
                })
                .value();
            expect(dates.sort()).toEqual(xLabels.sort());
        };

        expectTimelineRendered = function(view) {
            // We can't verify the rendering of the actual svg paths, since they
            // don't semantically encode which data they represent; instead NVD3
            // encodes pixel/location values of the points along the paths.
            // We also can't verify the rendering of Y axis, since it represents
            // the range of engagement values, and does so by taking the minimum
            // and maximum values, and interpolating values between them.
            expectLegendRendered(view);
            expectXAxisRendered(view);
        };

        fixtureClass = '.engagement-timeline-fixture';

        getTimelineModel = function() {
            return new EngagementTimelineModel({
                days: [{
                    date: '2016-01-01',
                    discussion_contributions: 1,
                    problems_attempted: 1,
                    problems_completed: 1,
                    videos_viewed: 1
                }, {
                    date: '2016-01-02',
                    discussion_contributions: 2,
                    problems_attempted: 2,
                    problems_completed: 2,
                    videos_viewed: 2
                }, {
                    fdate: '2016-01-03',
                    discussion_contributions: 3,
                    problems_attempted: 3,
                    problems_completed: 3,
                    videos_viewed: 3
                }]
            });
        };

        beforeEach(function() {
            setFixtures('<div class="' + fixtureClass.slice(1) + '"></div>');
        });

        it('can render an engagement timeline', function() {
            var model,
                view;
            model = getTimelineModel();
            view = new EngagementTimelineView({
                model: model,
                el: fixtureClass
            });
            view.render().onAttach();
            expectTimelineRendered(view);
        });
    });
});
