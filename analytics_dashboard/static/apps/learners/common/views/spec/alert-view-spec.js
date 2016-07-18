define(function(require) {
    'use strict';

    var AlertView = require('learners/common/views/alert-view');

    describe('AlertView', function() {
        it('throws exception for invalid alert types', function() {
            expect(function() {
                var alertView = new AlertView({alertType: 'scooby-doo'});
                alertView.validateAndUpdateTemplate();
            }).toThrow(new Error('AlertView error: "scooby-doo" is not valid. Valid types are error, info.'));
        });

        it('renders an error alert', function() {
            var fixture = setFixtures('<div id="error-alert"></div>'),
                alertView = new AlertView({
                    el: '#error-alert',
                    alertType: 'error',
                    title: 'edX Error Alert'
                });
            alertView.validateAndUpdateTemplate().render();

            expect(fixture).toContainElement('i.fa-exclamation-triangle');
            expect(fixture).toContainElement('.alert-error-container');
        });

        it('renders an info alert', function() {
            var fixture = setFixtures('<div class="info-alert"></div>'),
                alertView = new AlertView({
                    el: '.info-alert',
                    alertType: 'info',
                    title: 'edX Info Alert',
                    body: 'More description about an information alert.',
                    suggestions: ['Display alerts.', 'Alerts are helpful messages!']
                });
            alertView.validateAndUpdateTemplate().render();

            expect(fixture).toContainElement('i.fa-bullhorn');
            expect(fixture).toContainElement('.alert-info-container');
            expect(fixture).toContainElement('li');
        });
    });
});
