/**
 * Cell class which combines username and name.  The username links
 * to the user detail page.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),
        Backgrid = require('backgrid'),

        nameUsernameCellTemplate = require('text!learners/roster/templates/name-username-cell.underscore'),

        NameAndUsernameCell;

    NameAndUsernameCell = Backgrid.Cell.extend({
        className: 'learner-name-username-cell',
        template: _.template(nameUsernameCellTemplate),
        render: function() {
            this.$el.html(this.template(this.model.toJSON()));
            return this;
        }
    });

    return NameAndUsernameCell;
});
