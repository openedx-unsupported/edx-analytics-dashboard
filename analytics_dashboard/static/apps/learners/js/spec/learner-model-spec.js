define(['backbone', 'learners/js/models/learner-model'], function (Backbone, LearnerModel) {
    'use strict';

    describe('LearnerModel', function () {
        it('should have all the expected fields', function () {
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
                engagements: {},
                last_updated: null,
                course_id: ''
            });
        });

        it('should parse ISO 8601 dates', function () {
            var dateString = '2016-01-11',
                dateObj = new Date(dateString),
                learner = new LearnerModel(
                    {enrollment_date: dateString, last_updated: dateString},
                    {parse: true}
                );
            expect(learner.get('enrollment_date')).toEqual(dateObj);
            expect(learner.get('last_updated')).toEqual(dateObj);
        });

        it('should treat the username as its id', function () {
            var learner = new LearnerModel({username: 'daniel', course_id: 'edX/DemoX/Demo_Course'});
            new (Backbone.Collection.extend({url: '/endpoint/'}))([learner]);
            expect(learner.url()).toEqual('/endpoint/daniel?course_id=edX%2FDemoX%2FDemo_Course');
            learner = new (LearnerModel.extend({
                urlRoot: '/other-endpoint/'
            }))({username: 'daniel', course_id: 'edX/DemoX/Demo_Course'});
            expect(learner.url()).toEqual('/other-endpoint/daniel?course_id=edX%2FDemoX%2FDemo_Course');
        });
    });
});
