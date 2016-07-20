define(function(require) {
    'use strict';

    var AlertView = require('learners/common/views/alert-view');

    describe('AlertView', function() {
        var alertView;

        it('throws exception for invalid alert types', function() {
            expect(function() {
                alertView = new AlertView({alertType: 'scooby-doo'});
            }).toThrow(new Error('AlertView error: "scooby-doo" is not valid. Valid types are error, info.'));
        });

        it('renders an error alert', function() {
            var fixture = setFixtures('<div id="error-alert"></div>');

            alertView = new AlertView({
                el: '#error-alert',
                alertType: 'error',
                title: 'edX Error Alert'
            });
            alertView.render();

            expect(fixture).toContainElement('i.fa-exclamation-triangle');
            expect(fixture).toContainElement('.alert-error-container');
        });

        it('renders an info alert', function() {
            var fixture = setFixtures('<div class="info-alert"></div>');

            alertView = new AlertView({
                el: '.info-alert',
                alertType: 'info',
                title: 'edX Info Alert',
                body: 'More description about an information alert.',
                suggestions: ['Display alerts.', 'Alerts are helpful messages!']
            });
            alertView.render();

            expect(fixture).toContainElement('i.fa-bullhorn');
            expect(fixture).toContainElement('.alert-info-container');
            expect(fixture).toContainElement('li');
        });

        it('renders an alert with a link', function() {
            var fixture = setFixtures('<div class="info-alert"></div>');

            alertView = new AlertView({
                el: '.info-alert',
                alertType: 'info',
                title: 'edX Info Alert',
                body: 'More description about an information alert.',
                suggestions: ['Display alerts.', 'Alerts are helpful messages!'],
                link: {url: 'http://example.com', text: 'A helpful link.'}
            });
            alertView.render();

            expect(fixture).toContainElement('i.fa-bullhorn');
            expect(fixture).toContainElement('.alert-info-container');
            expect(fixture).toContainElement('li');
            expect(fixture).toContainElement('.link');
            expect(fixture).toContainElement('a');
        });
    });
});
