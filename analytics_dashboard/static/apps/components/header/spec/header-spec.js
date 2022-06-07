define((require) => {
  'use strict';

  const Backbone = require('backbone');

  const HeaderView = require('components/header/views/header');

  describe('HeaderView', () => {
    let fixture;

    beforeEach(() => {
      fixture = setFixtures('<div id="header-title"></div>');
    });

    it('renders updated title', () => {
      const pageModel = new Backbone.Model({ title: 'First Title' });

      new HeaderView({
        el: '#header-title',
        model: pageModel,
      }).render();

      expect(fixture).toContainText('First Title');
      expect(fixture).not.toContainText('Date Last Updated: unknown');
      pageModel.set('title', 'Updated Title');
      expect(fixture).toContainText('Updated Title');
    });

    it('renders a date', () => {
      const pageModel = new Backbone.Model({
        title: 'Initial Title',
        lastUpdated: new Date(2016, 0, 15),
      });

      new HeaderView({
        el: '#header-title',
        model: pageModel,
      }).render();

      expect(fixture).not.toContainText('Date Last Updated: January 15, 2016');
    });
  });
});
