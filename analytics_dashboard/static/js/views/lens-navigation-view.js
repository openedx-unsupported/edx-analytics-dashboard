define(['jquery', 'backbone', 'models/course-model'],
    function($, Backbone, CourseModel){
        'use strict';

        var LensNavigationView = Backbone.View.extend({

            el: '#sidebar',

            // Renders the view's template to the UI
            render: function() {
                var self = this;
                // Maintains chainability
                return this;
            }

        });

        return LensNavigationView;
    }
);