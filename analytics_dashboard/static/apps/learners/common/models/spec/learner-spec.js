define(function(require) {
    'use strict';

    var Backbone = require('backbone'),

        LearnerModel = require('learners/common/models/learner');

    describe('LearnerModel', function() {
        it('should have all the expected fields', function() {
            var learner = new LearnerModel();
            expect(learner.attributes).toEqual({
                name: '',
                username: '',
                email: '',
                account_url: '',
                enrollment_mode: '',
                enrollment_date: null,
                cohort: null,
                segments: [],
                engagements: {
                    discussion_contributions: 0,
                    problems_attempted: 0,
                    problems_completed: 0,
                    videos_viewed: 0,
                    problem_attempts_per_completed: Infinity
                },
                last_updated: null,
                course_id: ''
            });
        });

        it('should parse ISO 8601 dates', function() {
            var dateString = '2016-01-11',
                dateObj = new Date(dateString),
                learner = new LearnerModel(
                    {enrollment_date: dateString, last_updated: dateString},
                    {parse: true}
                );
            expect(learner.get('enrollment_date')).toEqual(dateObj);
            expect(learner.get('last_updated')).toEqual(dateObj);
        });

        it('should parse engagement metrics', function() {
            var learner = new LearnerModel({
                engagements: {
                    discussion_contributions: 1,
                    problems_attempted: 2,
                    problems_completed: 3,
                    videos_viewed: 4,
                    problem_attempts_per_completed: null
                }
            }, {parse: true});
            expect(learner.get('engagements').discussion_contributions).toEqual(1);
            expect(learner.get('engagements').problems_attempted).toEqual(2);
            expect(learner.get('engagements').problems_completed).toEqual(3);
            expect(learner.get('engagements').videos_viewed).toEqual(4);
            // Note that null engagement metrics should be parsed as Infinity
            expect(learner.get('engagements').problem_attempts_per_completed).toEqual(Infinity);
        });

        it('should treat the username as its id', function() {
            var learner = new LearnerModel({username: 'daniel', course_id: 'edX/DemoX/Demo_Course'}),
                // eslint-disable-next-line no-unused-vars
                collection = new (Backbone.Collection.extend({url: '/endpoint/'}))([learner]);
            expect(learner.url()).toEqual('/endpoint/daniel?course_id=edX%2FDemoX%2FDemo_Course');
            learner = new (LearnerModel.extend({
                urlRoot: '/other-endpoint/'
            }))({username: 'daniel', course_id: 'edX/DemoX/Demo_Course'});
            expect(learner.url()).toEqual('/other-endpoint/daniel?course_id=edX%2FDemoX%2FDemo_Course');
        });

        it('should use username to determine if data is available', function() {
            var learner = new LearnerModel();
            expect(learner.hasData()).toBe(false);

            learner.set('username', 'spiderman');
            expect(learner.hasData()).toBe(true);
        });
    });
});
