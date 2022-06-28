/**
 * Renders a sortable, filterable, and searchable paginated table of
 * courses for the Course List app.
 *
 * Requires the following values in the options hash:
 * - options.collection - an instance of CourseListCollection
 */
define((require) => {
  'use strict';

  const _ = require('underscore');
  const ActiveFiltersView = require('components/generic-list/list/views/active-filters');
  const CourseListControlsView = require('course-list/list/views/controls');
  const CourseListResultsView = require('course-list/list/views/results');
  const DownloadDataView = require('components/download/views/download-data');
  const ListView = require('components/generic-list/list/views/list');
  const NumResultsView = require('components/generic-list/list/views/num-results');

  const listTemplate = require('course-list/list/templates/list.underscore');

  const CourseListView = ListView.extend({
    className: 'course-list',

    template: _.template(listTemplate),

    regions: {
      activeFilters: '.course-list-active-filters',
      controls: '.course-list-table-controls',
      downloadData: '.course-list-download-data',
      results: '.course-list-results',
      numResults: '.course-list-num-results',
    },

    initialize(options) {
      ListView.prototype.initialize.call(this, options);

      this.childViews = [
        {
          region: 'activeFilters',
          class: ActiveFiltersView,
          options: {
            collection: this.options.collection,
            showChildrenOnRender: true,
          },
        },
        {
          region: 'controls',
          class: CourseListControlsView,
          options: {
            collection: this.options.collection,
            trackingModel: this.options.trackingModel,
            trackSubject: this.options.trackSubject,
            appClass: this.options.appClass,
            filteringEnabled: this.options.filteringEnabled,
          },
        },
        {
          region: 'downloadData',
          class: DownloadDataView,
          options: {
            collection: this.options.collection,
            trackingModel: this.options.trackingModel,
            trackCategory: 'course_list',
            downloadDataMessage: gettext('Download full course list to CSV'),
          },
        },
        {
          region: 'results',
          class: CourseListResultsView,
          options: {
            collection: this.options.collection,
            hasData: this.options.hasData,
            tableName: this.options.tableName,
            trackingModel: this.options.trackingModel,
            trackSubject: this.options.trackSubject,
            appClass: this.options.appClass,
          },
        },
        {
          region: 'numResults',
          class: NumResultsView,
          options: {
            collection: this.options.collection,
            appClass: this.options.appClass,
          },
        },
      ];

      this.controlsLabel = gettext('Course list controls');
    },
  });

  return CourseListView;
});
