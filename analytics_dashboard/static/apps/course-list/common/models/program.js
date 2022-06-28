define((require) => {
  'use strict';

  const _ = require('underscore');
  const Backbone = require('backbone');

  const ProgramModel = Backbone.Model.extend({
    defaults() {
      return {
        created: '',
        program_id: '',
        program_title: '',
        program_type: '',
        course_ids: [],
      };
    },

    idAttribute: 'program_id',

    /**
         * Returns true if the program_id has been set.  False otherwise.
         */
    hasData() {
      return !_(this.get('program_id')).isEmpty();
    },
  });

  return ProgramModel;
});
