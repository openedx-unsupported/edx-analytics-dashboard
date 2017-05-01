define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Backbone = require('backbone'),

        ProgramModel;

    ProgramModel = Backbone.Model.extend({
        defaults: function() {
            return {
                created: '',
                program_id: '',
                program_title: '',
                program_type: '',
                course_ids: []
            };
        },

        idAttribute: 'program_id',

        /**
         * Returns true if the program_id has been set.  False otherwise.
         */
        hasData: function() {
            return !_(this.get('program_id')).isEmpty();
        }
    });

    return ProgramModel;
});
