/**
 * This is the first script called by the engagement page.  It loads the libraries
 * and kicks off the application.
 */

// Load common.js first, which defines all of the models.  This is shared
// between pages.
require(['./common'], function () {
    'use strict';
    require(['jquery', 'models/course-model', 'views/lens-navigation-view', 'bootstrap', 'holder'],
        function ($, CourseModel, LensNavigationView, bootstrap, holder, DataTableView) {
            $(document).ready(function () {
                // ok, we've loaded all the libraries and the page is loaded, so
                // lets kick off our application
                var application = {

                    onLoad: function() {
                        var model,
                            view,
                            jsonData = JSON.parse( $('#content')
                                .attr('data-analytics-init') );

                        // this data will be set by something else eventually
                        model = new CourseModel();
                        // lets assume that django is passing us the data in the
                        // correct format for now
                        model.set(jsonData);

                        view = new LensNavigationView({model: model});
                        view.render();

                        // enable tooltips.  If individual tooltips need
                        // customization, we can have the specific views
                        // take care of them
                        $('.has-tooltip').tooltip();
                    }

                };

                application.onLoad();
            });
        }
    );
});
