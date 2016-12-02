define(['jquery', 'models/course-model', 'models/tracking-model', 'models/user-model', 'views/tracking-view'],
    function($, CourseModel, TrackingModel, UserModel, TrackingView) {
        'use strict';

        describe('Tracking View', function() {
            var USER_DETAILS = {
                username: 'edX',
                name: 'Ed Xavier',
                email: 'edx@example.com',
                ignoreInReporting: true
            };

            it('should call segment with application key and page', function() {
                var view;

                view = new TrackingView({
                    model: new TrackingModel()
                });
                view.applicationIdSet();

                // mock segment
                view.segment = {
                    load: jasmine.createSpy('load'),
                    page: jasmine.createSpy('page')
                };
                view.initSegment('myKey');

                expect(view.segment.load).toHaveBeenCalledWith('myKey');
                expect(view.segment.page).toHaveBeenCalled();
            });

            it('should call segment with user information', function() {
                var view = new TrackingView({
                    model: new TrackingModel(),
                    userModel: new UserModel(USER_DETAILS)
                });
                view.applicationIdSet();

                // mock segment
                view.segment = {
                    identify: jasmine.createSpy('identify')
                };

                view.logUser();

                expect(view.segment.identify).toHaveBeenCalledWith(USER_DETAILS.username, {
                    name: USER_DETAILS.name,
                    email: USER_DETAILS.email,
                    ignoreInReporting: true
                });
            });

            it('should call applicationIdSet() when segmentApplicationId is set', function() {
                var view,
                    courseModel = new CourseModel(),
                    trackingModel = new TrackingModel(),
                    userModel = new TrackingModel();

                view = new TrackingView({
                    model: trackingModel,
                    courseModel: courseModel,
                    userModel: userModel
                });
                view.applicationIdSet();

                // mock segment
                view.segment = {
                    load: jasmine.createSpy('load'),
                    page: jasmine.createSpy('page'),
                    identify: jasmine.createSpy('identify')
                };

                // segment view should call segment methods when data is set
                courseModel.set({
                    courseId: 'this/is/a/course',
                    org: 'org'
                });
                trackingModel.set({
                    segmentApplicationId: 'applicationId',
                    page: {
                        scope: 'course',
                        lens: 'mylens',
                        report: 'myreport',
                        depth: '',
                        name: 'course_mylens_myreport'
                    }
                });
                userModel.set(USER_DETAILS);

                // check to see if the methods were called
                expect(view.segment.identify).toHaveBeenCalled();
                expect(view.segment.page).toHaveBeenCalledWith({
                    courseId: 'this/is/a/course',
                    org: 'org',
                    label: 'course_mylens_myreport',
                    current_page: {
                        scope: 'course',
                        lens: 'mylens',
                        report: 'myreport',
                        depth: '',
                        name: 'course_mylens_myreport'
                    }
                });
                expect(view.segment.load).toHaveBeenCalled();
            });

            it('should only attach listeners if application ID set', function() {
                var view,
                    courseModel = new CourseModel(),
                    trackingModel = new TrackingModel(),
                    userModel = new TrackingModel();

                view = new TrackingView({
                    model: trackingModel,
                    courseModel: courseModel,
                    userModel: userModel
                });
                view.applicationIdSet();

                // mock segment
                view.segment = {
                    track: jasmine.createSpy('track'),
                    load: jasmine.createSpy('load'),
                    page: jasmine.createSpy('page'),
                    identify: jasmine.createSpy('identify')
                };

                trackingModel.set('segmentApplicationId', null);

                // check to make sure nothing on segment was called
                expect(view.segment.identify).not.toHaveBeenCalled();
                expect(view.segment.page).not.toHaveBeenCalled();
                expect(view.segment.load).not.toHaveBeenCalled();
                expect(view.segment.track).not.toHaveBeenCalled();
            });

            it('should call segment::track() when segment events are triggers', function() {
                var view,
                    courseModel = new CourseModel({
                        courseId: 'my/course/id',
                        org: 'org'
                    }),
                    trackingModel = new TrackingModel({
                        page: {
                            scope: 'course',
                            lens: 'mylens',
                            report: 'myreport',
                            depth: '',
                            name: 'course_mylens_myreport'
                        }
                    }),
                    userModel = new TrackingModel();

                view = new TrackingView({
                    model: trackingModel,
                    courseModel: courseModel,
                    userModel: userModel
                });
                view.applicationIdSet();

                // mock segment
                view.segment = {
                    track: jasmine.createSpy('track'),
                    load: jasmine.createSpy('load'),
                    page: jasmine.createSpy('page'),
                    identify: jasmine.createSpy('identify')
                };

                // trigger a segment event
                trackingModel.trigger('segment:track', 'trackingEvent', {param: 'my-param'});

                // we don't track events until segment has been loaded
                expect(view.segment.track).not.toHaveBeenCalled();

                trackingModel.set('segmentApplicationId', 'some ID');

                // trigger an event and make sure that track is called
                trackingModel.trigger('segment:track', 'trackingEvent', {param: 'my-param'});
                expect(view.segment.track).toHaveBeenCalledWith(
                    'trackingEvent', {
                        label: 'course_mylens_myreport',
                        courseId: 'my/course/id',
                        org: 'org',
                        param: 'my-param',
                        current_page: {
                            scope: 'course',
                            lens: 'mylens',
                            report: 'myreport',
                            depth: '',
                            name: 'course_mylens_myreport'
                        }
                    });
            });

            it('should call segment::page()', function() {
                var view,
                    courseModel = new CourseModel({
                        courseId: 'my/course/id',
                        org: 'org'
                    }),
                    trackingModel = new TrackingModel({
                        page: {
                            scope: 'course',
                            lens: 'mylens',
                            report: 'myreport',
                            depth: '',
                            name: 'course_mylens_myreport'
                        }
                    }),
                    userModel = new TrackingModel();

                view = new TrackingView({
                    model: trackingModel,
                    courseModel: courseModel,
                    userModel: userModel
                });
                view.applicationIdSet();

                // mock segment
                view.segment = {
                    track: jasmine.createSpy('track'),
                    load: jasmine.createSpy('load'),
                    page: jasmine.createSpy('page'),
                    identify: jasmine.createSpy('identify')
                };

                // trigger a segment event
                trackingModel.trigger('segment:page', 'pageName', {param: 'my-param'});

                // we don't track events until segment has been loaded
                expect(view.segment.page).not.toHaveBeenCalled();

                trackingModel.set('segmentApplicationId', 'some ID');

                // trigger an event and make sure that page is called
                trackingModel.trigger('segment:page', 'pageName', {param: 'my-param'});
                expect(view.segment.page).toHaveBeenCalledWith(
                    'pageName', {
                        label: 'course_mylens_myreport',
                        courseId: 'my/course/id',
                        org: 'org',
                        param: 'my-param',
                        current_page: {
                            scope: 'course',
                            lens: 'mylens',
                            report: 'myreport',
                            depth: '',
                            name: 'course_mylens_myreport'
                        }
                    });
            });
        });

        describe('Tracking element events', function() {
            beforeEach(function() {
                $('<div id="sandbox"></div>').appendTo('body');
            });

            afterEach(function() {
                $('#sandbox').remove();
            });

            function setupTest() {
                var view,
                    courseModel = new CourseModel({
                        courseId: 'my/course/id',
                        org: 'org'
                    }),
                    trackingModel = new TrackingModel({
                        page: {
                            scope: 'course',
                            lens: 'mylens',
                            report: 'myreport',
                            depth: '',
                            name: 'course_mylens_myreport'
                        },
                        segmentApplicationId: 'some ID'
                    }),
                    userModel = new TrackingModel(),
                    $sandbox = $('#sandbox');

                view = new TrackingView({
                    el: document,
                    model: trackingModel,
                    courseModel: courseModel,
                    userModel: userModel
                });
                view.applicationIdSet();

                // mock segment
                view.segment = {
                    track: jasmine.createSpy('track'),
                    load: jasmine.createSpy('load'),
                    page: jasmine.createSpy('page'),
                    identify: jasmine.createSpy('identify')
                };

                $sandbox.attr('data-track-event', 'trackingEvent');
                $sandbox.attr('data-track-param', 'my-param');
                $sandbox.attr('data-track-foo', 'bar');

                return {
                    trackingModel: trackingModel,
                    view: view,
                    sandbox: $sandbox,
                    showTooltip: function() {
                        $sandbox.trigger('shown.bs.tooltip');
                    },
                    expectNoEventToHaveBeenEmitted: function() {
                        expect(view.segment.track).not.toHaveBeenCalled();
                    },
                    expectEventEmitted: function(eventType, properties) {
                        expect(view.segment.track).toHaveBeenCalledWith(eventType, properties);
                    }
                };
            }

            it('should emit an event when tooltips are shown', function() {
                var test = setupTest();

                test.showTooltip();

                test.expectEventEmitted(
                    'trackingEvent', {
                        label: 'course_mylens_myreport',
                        courseId: 'my/course/id',
                        org: 'org',
                        param: 'my-param',
                        foo: 'bar',
                        current_page: {
                            scope: 'course',
                            lens: 'mylens',
                            report: 'myreport',
                            depth: '',
                            name: 'course_mylens_myreport'
                        }
                    }
                );
            });

            it('should not emit an event when tooltips are shown when tracking is not enabled', function() {
                var test = setupTest();

                test.trackingModel.unset('segmentApplicationId');

                test.showTooltip();
                test.expectNoEventToHaveBeenEmitted();
            });

            it('should not emit an event when tooltips are shown when event type is empty', function() {
                var test = setupTest();

                test.sandbox.attr('data-track-event', '');
                test.showTooltip();
                test.expectNoEventToHaveBeenEmitted();
            });

            it('should not emit an event when tooltips are shown when event type is undefined', function() {
                var test = setupTest();

                test.sandbox.removeAttr('data-track-event');
                test.showTooltip();
                test.expectNoEventToHaveBeenEmitted();
            });

            it('should transform target HTML data attributes', function() {
                var test = setupTest();

                test.sandbox.attr('data-track-target-scope', 'course');
                test.sandbox.attr('data-track-target-lens', 'mylens');
                test.sandbox.attr('data-track-target-report', 'myreport');
                test.sandbox.attr('data-track-target-depth', 'mydepth');
                test.showTooltip();

                test.expectEventEmitted(
                    'trackingEvent', {
                        label: 'course_mylens_myreport',
                        courseId: 'my/course/id',
                        org: 'org',
                        param: 'my-param',
                        foo: 'bar',
                        current_page: {
                            scope: 'course',
                            lens: 'mylens',
                            report: 'myreport',
                            depth: '',
                            name: 'course_mylens_myreport'
                        },
                        target_page: {
                            scope: 'course',
                            lens: 'mylens',
                            report: 'myreport',
                            depth: 'mydepth',
                            name: 'course_mylens_myreport_mydepth'
                        }
                    }
                );
            });

            it('should transform target HTML data attributes (with name parts missing)', function() {
                var test = setupTest();

                test.sandbox.attr('data-track-target-scope', 'course');
                test.sandbox.attr('data-track-target-lens', 'mylens');
                test.showTooltip();

                test.expectEventEmitted(
                    'trackingEvent', {
                        label: 'course_mylens_myreport',
                        courseId: 'my/course/id',
                        org: 'org',
                        param: 'my-param',
                        foo: 'bar',
                        current_page: {
                            scope: 'course',
                            lens: 'mylens',
                            report: 'myreport',
                            depth: '',
                            name: 'course_mylens_myreport'
                        },
                        target_page: {
                            scope: 'course',
                            lens: 'mylens',
                            report: '',
                            depth: '',
                            name: 'course_mylens'
                        }
                    }
                );
            });

            it('should transform link-name and menu-depth HTML data attributes', function() {
                var test = setupTest();

                test.sandbox.attr('data-track-menu-depth', 'lens');
                test.sandbox.attr('data-track-link-name', 'mylens');
                test.showTooltip();

                test.expectEventEmitted(
                    'trackingEvent', {
                        label: 'course_mylens_myreport',
                        courseId: 'my/course/id',
                        org: 'org',
                        param: 'my-param',
                        foo: 'bar',
                        current_page: {
                            scope: 'course',
                            lens: 'mylens',
                            report: 'myreport',
                            depth: '',
                            name: 'course_mylens_myreport'
                        },
                        menu_depth: 'lens',
                        link_name: 'mylens',
                        category: 'lens+mylens'
                    }
                );
            });
        });
    });
