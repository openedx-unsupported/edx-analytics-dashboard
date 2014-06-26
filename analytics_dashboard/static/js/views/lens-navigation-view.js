define(['jquery', 'backbone', 'models/course-model'],
    function($, Backbone, CourseModel){
        'use strict';

        var LensNavigationView = Backbone.View.extend({

            el: '#lens-navigation',

            // Renders the view's template to the UI
            render: function() {
                var self = this;

                self.$el.append('<h2>Navigation Section for ' +
                    self.model.get('courseId') + '</h2>');

                // Maintains chainability
                return this;
            }

        });

        return LensNavigationView;
    }
);