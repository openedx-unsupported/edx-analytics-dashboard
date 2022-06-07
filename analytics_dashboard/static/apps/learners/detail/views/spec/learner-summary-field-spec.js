define((require) => {
  'use strict';

  const Backbone = require('backbone');
  const LearnerSummaryFieldView = require('learners/detail/views/learner-summary-field');

  describe('LearnerSummaryField', () => {
    let fixture;

    beforeEach(() => {
      fixture = setFixtures('<div id="summary"></div>');
    });

    it('displays a field and value', () => {
      const model = new Backbone.Model({ animal: 'Rubber Duck' });
      const view = new LearnerSummaryFieldView({
        model,
        modelAttribute: 'animal',
        fieldDisplayName: 'Animal',
        el: fixture,
      });

      view.render();

      expect(fixture).toContainText('Animal');
      expect(fixture).toContainText('Rubber Duck');
    });

    it('displays "n/a" initially and updates', () => {
      const model = new Backbone.Model();
      const view = new LearnerSummaryFieldView({
        model,
        modelAttribute: 'model-attribute',
        fieldDisplayName: 'Field',
        el: fixture,
      });

      view.render();
      expect(fixture).toContainText('Field');
      expect(fixture).toContainText('n/a');

      model.set('model-attribute', 'My Attribute');
      expect(fixture).toContainText('Field');
      expect(fixture).toContainText('My Attribute');
    });

    it('formats values', () => {
      const model = new Backbone.Model({ animal: 'Rubber Duck' });
      const view = new LearnerSummaryFieldView({
        model,
        modelAttribute: 'animal',
        fieldDisplayName: 'Friend',
        el: fixture,
        valueFormatter(value) {
          return `${value}y`;
        },
      });

      view.render();
      expect(fixture).toContainText('Friend');
      expect(fixture).toContainText('Rubber Ducky');
    });
  });
});
