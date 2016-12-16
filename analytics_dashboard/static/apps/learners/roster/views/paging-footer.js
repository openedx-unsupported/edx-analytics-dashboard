define(function(require) {
    'use strict';

    var $ = require('jquery'),
        PagingFooter = require('components/generic-list/list/views/paging-footer'),

        LearnersPagingFooter;

    LearnersPagingFooter = PagingFooter.extend({
        initialize: function(options) {
            PagingFooter.prototype.initialize.call(this, options);
            this.$appFocusable = $('#learner-app-focusable');
            this.trackPageEventName = 'edx.bi.roster.paged';
        }
    });

    return LearnersPagingFooter;
});
