define(function(require) {
    'use strict';

    var ListCollection = require('components/generic-list/common/collections/collection'),
        CourseModel = require('course-list/common/models/course'),

        CourseListCollection;

    CourseListCollection = ListCollection.extend({
        model: CourseModel,

        initialize: function(models, options) {
            ListCollection.prototype.initialize.call(this, models, options);

            this.registerSortableField('catalog_course_title', gettext('Course Name'));
            this.registerSortableField('start_date', gettext('Start Date'));
            this.registerSortableField('end_date', gettext('End Date'));
            this.registerSortableField('cumulative_count', gettext('Total Enrollment'));
            this.registerSortableField('count', gettext('Current Enrollment'));
            this.registerSortableField('count_change_7_days', gettext('Change Last Week'));
            this.registerSortableField('verified_enrollment', gettext('Verified Enrollment'));

            this.registerFilterableField('availability', gettext('Availability'));
            this.registerFilterableField('pacing_type', gettext('Pacing Type'));
        },

        state: {
            pageSize: 100,
            sortKey: 'catalog_course_title',
            order: 0
        },

        // Override PageableCollection's setPage() method because it has a bug where it assumes that backgrid getPage()
        // will always return a promise. It does not in client mode.
        setPage: function(page) {
            var oldPage = this.state.currentPage,
                self = this,
                deferred = $.Deferred(),
                newPage = this.getPage(page - (1 - this.state.firstPage), {reset: true});
            if (typeof newPage.then === 'function') { // is server mode
                newPage.then(
                    function() {
                        self.isStale = false;
                        self.trigger('page_changed');
                        deferred.resolve();
                    },
                    function() {
                        self.state.currentPage = oldPage;
                        deferred.fail();
                    }
                );
            } else { // is client mode
                // getPage() will probably throw an exception if it fails in client mode, so assume succeeded
                self.isStale = false;
                self.trigger('page_changed');
                deferred.resolve();
            }
            return deferred.promise();
        }
    });

    return CourseListCollection;
});
