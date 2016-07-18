define(function(require) {
    'use strict';

    var Backbone = require('backbone'),

        PageModel;

    PageModel = Backbone.Model.extend({
        defaults: {
            title: '',  // title displayed in header
            lastUpdated: undefined  // last updated date displayed in header
        }
    });

    return PageModel;
});
