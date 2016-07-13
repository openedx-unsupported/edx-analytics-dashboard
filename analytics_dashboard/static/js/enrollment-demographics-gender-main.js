/**
 * This is the first script called by the enrollment demographics gender page.  It loads
 * the libraries and kicks off the application.
 */
var doc = require('vendor/domReady!'),
    page = require('load/init-page'),
    _ = require('underscore'),
    DataTableView = require('views/data-table-view'),
    WorldMapView = require('views/world-map-view');

(function(doc, page) {
    'use strict';

    (function(_, DataTableView, DiscreteBarView) {
        new DiscreteBarView({
            el: '#enrollment-chart-view',
            model: page.models.courseModel,
            modelAttribute: 'genders',
            dataType: 'percent',
            trends: [{
                title: gettext('Percentage'),
                color: 'rgb(58, 162, 224)'
            }],
            x: {key: 'gender'},
            y: {key: 'percent'},
            // Translators: <%=value%> will be replaced with a level of gender (e.g. Female).
            interactiveTooltipHeaderTemplate: _.template(gettext('Gender: <%=value%>'))
        });

        // Daily enrollment table
        new DataTableView({
            el: '[data-role=enrollment-table]',
            model: page.models.courseModel,
            modelAttribute: 'genderTrend',
            columns: [
                {key: 'date', title: gettext('Date'), type: 'date'},
                {key: 'total', title: gettext('Current Enrollment'), type: 'number', className: 'text-right'},
                {key: 'female', title: gettext('Female'), type: 'number', className: 'text-right'},
                {key: 'male', title: gettext('Male'), type: 'number', className: 'text-right'},
                {key: 'other', title: gettext('Other'), type: 'number', className: 'text-right'},
                {key: 'unknown', title: gettext('Not Reported'), type: 'number', className: 'text-right'}
            ],
            sorting: ['-date']
        });
    });
});
