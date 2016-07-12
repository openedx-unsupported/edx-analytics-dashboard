define(function(require) {
    'use strict';

    var AlertView = require('learners/common/views/alert-view');

    describe('AlertView', function() {
        it('throws exception for invalid alert types', function() {
            expect(function() {
                new AlertView({alertType: 'scooby-doo'});
            }).toThrow(new Error('AlertView error: "scooby-doo" is not valid. Valid types are error, info.'));
        });

        it('renders an error alert', function() {
            var fixture = setFixtures('<div id="error-alert"></div>');

            new AlertView({
                el: '#error-alert',
                alertType: 'error',
                title: 'edX Error Alert'
            }).render();

            expect(fixture).toContainElement('i.fa-exclamation-triangle');
            expect(fixture).toContainElement('.alert-error-container');
        });

        it('renders an info alert', function() {
            var fixture = setFixtures('<div class="info-alert"></div>');

            new AlertView({
                el: '.info-alert',
                alertType: 'info',
                title: 'edX Info Alert',
                body: 'More description about an information alert.',
                suggestions: ['Display alerts.', 'Alerts are helpful messages!']
            }).render();

            expect(fixture).toContainElement('i.fa-bullhorn');
            expect(fixture).toContainElement('.alert-info-container');
            expect(fixture).toContainElement('li');
        });
    });
});
