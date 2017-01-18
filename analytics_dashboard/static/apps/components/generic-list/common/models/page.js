define(function(require) {
    'use strict';

    var Backbone = require('backbone'),
        $ = require('jquery'),

        PageModel;

    PageModel = Backbone.Model.extend({
        defaults: {
            title: '',  // title displayed in header
            lastUpdated: undefined  // last updated date displayed in header
        },

        initialize: function() {
            this.bind('change:title', this.updateTitleElement);
        },

        updateTitleElement: function() {
            var self = this;
            $('title').text(function() {
                return $(this).text().replace(/^.*[-]/, self.get('title') + ' -');
            });
        }
    });

    return PageModel;
});
