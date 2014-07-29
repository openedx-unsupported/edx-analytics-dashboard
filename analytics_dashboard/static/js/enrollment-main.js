/**
 * This is the first script called by the enrollment page.  It loads
 * the libraries and kicks off the application.
 */

// Load common.js first, which defines all of the models.  This is shared
// between pages.
require(['./common'], function () {
    'use strict';
    require(['jquery', 'models/course-model', 'views/lens-navigation-view', 'views/enrollment-trend-view', 'bootstrap', 'views/data-table-view', 'views/world-map-view', 'views/simple-model-attribute-view'],
        function ($, CourseModel, LensNavigationView, EnrollmentTrendView, bootstrap, DataTableView, WorldMapView, SimpleModelAttributeView) {
            $(document).ready(function () {
                // ok, we've loaded all the libraries and the page is loaded, so
                // lets kick off our application
                var application = {

                    /*jshint nonew: false */
                    onLoad: function () {
                        var model,
                            jsonData = JSON.parse($('#content').attr('data-analytics-init'));

                        // this data will be set by something else eventually
                        model = new CourseModel();


                        new LensNavigationView({model: model}).render();

                        // enable tooltips.  If individual tooltips need customization, we can have the specific views
                        // take care of them.
                        $('.has-tooltip').tooltip();

                        // Daily enrollment graph
                        new EnrollmentTrendView({
                            el: '#enrollment-trend-view',
                            model: model,
                            modelAttribute: 'enrollmentTrends'
                        });

                        // Daily enrollment table
                        new DataTableView({
                            el: '[data-role=enrollment-table]',
                            model: model,
                            modelAttribute: 'enrollmentTrends',
                            columns: [
                                {key: 'date', title: 'Date'},
                                {key: 'count', title: 'Count'}
                            ],
                            sorting: ['-date']
                        });

                        // Enrollment by country last updated label
                        new SimpleModelAttributeView({
                            el: '[data-view=enrollment-by-country-update-date]',
                            model: model,
                            modelAttribute: 'enrollmentByCountryUpdateDate'
                        });

                        // Enrollment by country map
                        new WorldMapView({
                            el: '[data-view=world-map]',
                            model: model,
                            modelAttribute: 'enrollmentByCountry'
                        });

                        // Enrollment by country table
                        new DataTableView({
                            el: '[data-role=enrollment-location-table]',
                            model: model,
                            modelAttribute: 'enrollmentByCountry',
                            columns: [
                                {key: 'country_name', title: 'Country'},
                                {key: 'value', title: 'Count'}
                            ],
                            sorting: ['-value']
                        });

                        // Update the model to trigger view rendering
                        model.set(jsonData);
                        model.fetchEnrollmentByCountry();
                    }
                };

                application.onLoad();
            });
        }
    );
});
