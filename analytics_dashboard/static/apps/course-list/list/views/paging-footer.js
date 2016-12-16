define(function(require) {
    'use strict';

    var $ = require('jquery'),
        PagingFooter = require('components/generic-list/list/views/paging-footer'),

        CourseListPagingFooter;

    CourseListPagingFooter = PagingFooter.extend({
        initialize: function(options) {
            PagingFooter.prototype.initialize.call(this, options);
            this.$appFocusable = $('#course-list-app-focusable');
            this.trackPageEventName = 'edx.bi.course_list.paged';
        }
    });

    return CourseListPagingFooter;
});
