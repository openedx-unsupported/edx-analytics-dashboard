define(function(require) {
    'use strict';

    var Backbone = require('backbone'),
        LearnerCollection = require('learners/common/collections/learners'),
        LearnersController = require('learners/app/controller'),
        LearnersRouter = require('learners/app/router'),
        PageModel = require('components/generic-list/common/models/page');

    describe('LearnersRouter', function() {
        beforeEach(function() {
            Backbone.history.start({silent: true});
            this.server = sinon.fakeServer.create();
            this.user = {
                last_updated: new Date(2016, 1, 28)
            };
            this.collection = new LearnerCollection([this.user], {url: 'http://example.com'});
            this.controller = new LearnersController({
                learnerCollection: this.collection,
                pageModel: new PageModel()
            });
            spyOn(this.controller, 'showLearnerRosterPage').and.stub();
            spyOn(this.controller, 'showLearnerDetailPage').and.stub();
            spyOn(this.controller, 'showNotFoundPage').and.stub();
            spyOn(this.controller, 'onShowPage').and.stub();
            this.router = new LearnersRouter({
                controller: this.controller
            });
        });

        afterEach(function() {
            // Clear previous route
            this.router.navigate('');
            Backbone.history.stop();
            this.server.restore();
        });

        it('triggers a showPage event for pages beginning with "show"', function() {
            this.router.navigate('foo', {trigger: true});
            expect(this.controller.onShowPage).toHaveBeenCalled();
            this.router.navigate('/', {trigger: true});
            expect(this.controller.onShowPage).toHaveBeenCalled();
        });

        describe('showLearnerRosterPage', function() {
            beforeEach(function() {
                // Backbone won't trigger a route unless we were on a previous url
                this.router.navigate('initial-fragment', {trigger: false});
            });

            it('should trigger on an empty URL fragment', function() {
                this.router.navigate('', {trigger: true});
                expect(this.controller.showLearnerRosterPage).toHaveBeenCalled();
            });

            it('should trigger on a single forward slash', function() {
                this.router.navigate('/', {trigger: true});
                expect(this.controller.showLearnerRosterPage).toHaveBeenCalled();
            });

            it('should trigger on an empty URL fragment with a querystring', function() {
                var querystring = 'text_search=some_username';
                this.router.navigate('?' + querystring, {trigger: true});
                expect(this.controller.showLearnerRosterPage).toHaveBeenCalledWith(querystring, null);
            });
        });

        describe('showLearnerDetailPage', function() {
            it('should trigger on a username', function() {
                this.router.navigate('username', {trigger: true});
                expect(this.controller.showLearnerDetailPage).toHaveBeenCalledWith('username', null, null);
            });

            it('should trigger on a username and a trailing slash', function() {
                this.router.navigate('username/', {trigger: true});
                expect(this.controller.showLearnerDetailPage).toHaveBeenCalledWith('username', null, null);
            });

            it('should trigger on a username and a querystring', function() {
                var querystring = 'order_by=problems_attempted';
                this.router.navigate('username/?' + querystring, {trigger: true});
                expect(this.controller.showLearnerDetailPage).toHaveBeenCalledWith(
                    'username', querystring, null
                );
            });
        });

        describe('showNotFoundPage', function() {
            it('should trigger on unmatched URLs', function() {
                this.router.navigate('this/does/not/match', {trigger: true});
                expect(this.controller.showNotFoundPage).toHaveBeenCalledWith('this/does/not/match', null);
            });
        });

        it('URL fragment is updated on LearnerCollection sync', function(done) {
            this.collection.state.currentPage = 2;
            this.collection.setFilterField('text_search', 'foo');
            this.collection.fetch({reset: true});
            this.collection.once('sync', function() {
                expect(Backbone.history.getFragment()).toBe('?text_search=foo&page=2');
                done();
            });
            this.server.requests[0].respond(200, {}, JSON.stringify([this.user]));
        });
    });
});
