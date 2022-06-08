/**
 * Renders a sortable, filterable, and searchable paginated table of
 * learners for the Learner Analytics app.
 *
 * Add a DOM element with id=resultsTarget that the controls can set focus to for
 * keyboard users.
 */
define((require) => {
  'use strict';

  const ParentView = require('components/generic-list/common/views/parent-view');
  const ListUtils = require('components/utils/utils');

  // Load modules without exports
  require('backgrid-filter');
  require('components/skip-link/behaviors/skip-target-behavior');

  /**
     * Wraps up the search view, table view, and pagination footer
     * view.
     */
  const ListView = ParentView.extend({
    className: 'generic-list',

    ui: {
      skipTarget: '#resultsTarget',
    },

    behaviors: {
      SkipTargetBehavior: {},
    },

    initialize(options) {
      this.options = options || {};

      const eventTransformers = {
        serverError: ListUtils.EventTransformers.serverErrorToAppError,
        networkError: ListUtils.EventTransformers.networkErrorToAppError,
        sync: ListUtils.EventTransformers.syncToClearError,
      };
      ListUtils.mapEvents(this.options.collection, eventTransformers, this);
    },

    templateHelpers() {
      return {
        controlsLabel: this.controlsLabel,
        resultsText: gettext('Results'),
      };
    },
  });

  return ListView;
});
