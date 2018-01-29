define(function(require) {
    'use strict';

    var Backbone = require('backbone'),
        ProgramModel = require('course-list/common/models/program'),

        ProgramsCollection;

    ProgramsCollection = Backbone.Collection.extend({
        model: ProgramModel
    });

    return ProgramsCollection;
});
