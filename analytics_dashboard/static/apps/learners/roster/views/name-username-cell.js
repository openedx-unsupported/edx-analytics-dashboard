/**
 * Cell class which combines username and name.  The username links
 * to the user detail page.
 */
define((require) => {
  'use strict';

  const _ = require('underscore');

  const RowHeaderCell = require('components/generic-list/list/views/row-header-cell');
  const nameUsernameCellTemplate = require('learners/roster/templates/name-username-cell.underscore');

  const NameAndUsernameCell = RowHeaderCell.extend({
    className: 'learner-name-username-cell',
    template: _.template(nameUsernameCellTemplate),
  });

  return NameAndUsernameCell;
});
