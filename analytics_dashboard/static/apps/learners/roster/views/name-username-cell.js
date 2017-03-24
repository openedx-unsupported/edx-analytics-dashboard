/**
 * Cell class which combines username and name.  The username links
 * to the user detail page.
 */
define(function(require) {
    'use strict';

    var _ = require('underscore'),

        RowHeaderCell = require('components/generic-list/list/views/row-header-cell'),
        nameUsernameCellTemplate = require('text!learners/roster/templates/name-username-cell.underscore'),

        NameAndUsernameCell;

    NameAndUsernameCell = RowHeaderCell.extend({
        className: 'learner-name-username-cell',
        template: _.template(nameUsernameCellTemplate)
    });

    return NameAndUsernameCell;
});
