define((require) => {
  'use strict';

  const $ = require('jquery');
  const _ = require('underscore');
  const moment = require('moment');

  const EngagementTimelineModel = require('learners/common/models/engagement-timeline');
  const EngagementTimelineView = require('learners/detail/views/engagement-timeline');

  describe('EngagementTimelineView', () => {
    const expectLegendRendered = view => {
      const labels = ['Discussion Contributions', 'Problems Correct', 'Videos Viewed'];
      const legendItems = view.$('.nv-legend-text');
      expect(labels.length).toEqual(legendItems.length);
      _.each(labels, (label, index) => {
        expect(legendItems[index]).toHaveText(label);
      });
    };

    const expectXAxisRendered = view => {
      const dates = _.map(view.model.get('days'), (day) => moment.utc(Date.parse(day.date)).format('D MMM YYYY'));
      // Note that NVD3 unfortunately doesn't semantically order the
      // x-axis labels in the DOM, so we can't verify each label in order.
      const xLabels = _.chain(view.$('.nv-x.nv-axis text'))
        .filter((el) => $(el).text() !== '')
        .map((el) => $(el).text())
        .value();
      expect(dates.sort()).toEqual(xLabels.sort());
    };

    const expectTimelineRendered = view => {
      // We can't verify the rendering of the actual svg paths, since they
      // don't semantically encode which data they represent; instead NVD3
      // encodes pixel/location values of the points along the paths.
      // We also can't verify the rendering of Y axis, since it represents
      // the range of engagement values, and does so by taking the minimum
      // and maximum values, and interpolating values between them.
      expectLegendRendered(view);
      expectXAxisRendered(view);
    };

    const fixtureClass = '.engagement-timeline-fixture';

    const getTimelineModel = () => new EngagementTimelineModel({
      days: [{
        date: '2016-01-01',
        discussion_contributions: 1,
        problems_attempted: 1,
        problems_completed: 1,
        videos_viewed: 1,
      }, {
        date: '2016-01-02',
        discussion_contributions: 2,
        problems_attempted: 2,
        problems_completed: 2,
        videos_viewed: 2,
      }, {
        fdate: '2016-01-03',
        discussion_contributions: 3,
        problems_attempted: 3,
        problems_completed: 3,
        videos_viewed: 3,
      }],
    });

    beforeEach(() => {
      setFixtures(`<div class="${fixtureClass.slice(1)}"></div>`);
    });

    it('can render an engagement timeline', () => {
      const model = getTimelineModel();
      const view = new EngagementTimelineView({
        model,
        el: fixtureClass,
      });
      view.render().onAttach();
      expectTimelineRendered(view);
    });
  });
});
