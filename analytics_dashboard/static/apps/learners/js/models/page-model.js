define([
    'backbone'
], function (Backbone) {
    'use strict';

    var PageModel = Backbone.Model.extend({
        defaults: {
            title: '',  // title displayed in header
            lastUpdated: undefined  // last updated date displayed in header
        }
    });

    return PageModel;
});
