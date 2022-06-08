define((require) => {
  'use strict';

  const Backbone = require('backbone');
  const ProgramModel = require('course-list/common/models/program');

  const ProgramsCollection = Backbone.Collection.extend({
    model: ProgramModel,
  });

  return ProgramsCollection;
});
