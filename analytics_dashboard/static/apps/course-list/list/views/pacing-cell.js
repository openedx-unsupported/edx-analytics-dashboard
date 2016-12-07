/**
 * Cell class which formats the display of the pacing type of a course in the course list table.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Backgrid = require('backgrid'),

        pacingCellTemplate = require('text!course-list/list/templates/pacing-cell.underscore'),

        PACING_DISPLAY_NAMES = {self_paced: 'Self Paced', instructor_paced: 'Instructor Paced', '': '--'},

        PacingCell;

    PacingCell = Backgrid.Cell.extend({
        className: 'pacing-cell',
        template: _.template(pacingCellTemplate),
        render: function() {
            var pacing = this.model.get('pacing_type');
            pacing = PACING_DISPLAY_NAMES[pacing] || pacing;
            this.$el.html(this.template({pacing: pacing}));
            return this;
        }
    });

    return PacingCell;
});
