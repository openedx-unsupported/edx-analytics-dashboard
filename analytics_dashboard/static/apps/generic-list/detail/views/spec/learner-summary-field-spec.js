define(function(require) {
    'use strict';

    var Backbone = require('backbone'),
        LearnerSummaryFieldView = require('learners/detail/views/learner-summary-field');

    describe('LearnerSummaryField', function() {
        var fixture;

        beforeEach(function() {
            fixture = setFixtures('<div id="summary"></div>');
        });

        it('displays a field and value', function() {
            var model = new Backbone.Model({animal: 'Rubber Duck'}),
                view = new LearnerSummaryFieldView({
                    model: model,
                    modelAttribute: 'animal',
                    fieldDisplayName: 'Animal',
                    el: fixture
                });

            view.render();

            expect(fixture).toContainText('Animal');
            expect(fixture).toContainText('Rubber Duck');
        });

        it('displays "n/a" initially and updates', function() {
            var model = new Backbone.Model(),
                view = new LearnerSummaryFieldView({
                    model: model,
                    modelAttribute: 'model-attribute',
                    fieldDisplayName: 'Field',
                    el: fixture
                });

            view.render();
            expect(fixture).toContainText('Field');
            expect(fixture).toContainText('n/a');

            model.set('model-attribute', 'My Attribute');
            expect(fixture).toContainText('Field');
            expect(fixture).toContainText('My Attribute');
        });

        it('formats values', function() {
            var model = new Backbone.Model({animal: 'Rubber Duck'}),
                view = new LearnerSummaryFieldView({
                    model: model,
                    modelAttribute: 'animal',
                    fieldDisplayName: 'Friend',
                    el: fixture,
                    valueFormatter: function(value) {
                        return value + 'y';
                    }
                });

            view.render();
            expect(fixture).toContainText('Friend');
            expect(fixture).toContainText('Rubber Ducky');
        });
    });
});
