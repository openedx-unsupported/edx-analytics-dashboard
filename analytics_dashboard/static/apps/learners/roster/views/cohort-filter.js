/**
 * A component to filter the roster view by cohort.
 */
define(function (require) {
    'use strict';

    var $ = require('jquery'),
        _ = require('underscore'),
        Marionette = require('marionette'),

        Utils = require('utils/utils'),
        cohortFilterTemplate = require('text!learners/roster/templates/cohort-filter.underscore'),

        CohortFilter;

    CohortFilter = Marionette.ItemView.extend({
        events: {
            'change #cohort-filter': 'onSelectCohort'
        },
        className: 'learners-cohort-filter',
        template: _.template(cohortFilterTemplate),
        initialize: function (options) {
            this.options = options || {};
            _.bind(this.onSelectCohort, this);
        },
        templateHelpers: function () {
            // 'cohorts' is an array of objects, each having a 'cohortName' key
            // and a 'displayName' key.  'cohortName' is the canonical name for
            // the cohort, while 'displayName' is the user-facing representation
            // of the cohort.
            var catchAllCohortName,
                cohorts,
                selectedCohort;
            cohorts = _.chain(this.options.courseMetadata.get('cohorts'))
                .pairs()
                .map(function (cohortPair) {
                    var cohortName = cohortPair[0],
                        numLearners = cohortPair[1];
                    return {
                        cohortName: cohortName,
                        displayName: _.template(ngettext(
                            // jshint ignore:start
                            // Translators: 'cohortName' is the name of the cohort and 'numLearners' is the number of learners in that cohort.  The resulting phrase displays a cohort and the number of students belonging to it. For example: "Cohort Awesome (1,234 learners)".
                            '<%= cohortName %> (<%= numLearners %> learner)',
                            // Translators: 'cohortName' is the name of the cohort and 'numLearners' is the number of learners in that cohort.  The resulting phrase displays a cohort and the number of students belonging to it.
                            '<%= cohortName %> (<%= numLearners %> learners)',
                            // jshint ignore:end
                            numLearners
                        ))({
                            cohortName: cohortName,
                            numLearners: Utils.localizeNumber(numLearners, 0)
                        })
                    };
                })
                .value();

            if (cohorts.length) {
                // There can never be a cohort with no name, due to
                // validation in the LMS, therefore it's safe to use the
                // empty string as a property in this object.  The API
                // interprets this as "all students, regardless of
                // cohort".
                catchAllCohortName = '';
                cohorts.unshift({
                    cohortName: catchAllCohortName,
                    // Translators: "All" refers to viewing all the learners in a course.
                    displayName: gettext('All')
                });

                // Assumes that you can only filter by one cohort at a time.
                selectedCohort = _.chain(cohorts)
                    .pluck('cohortName')
                    .intersection(this.options.collection.getActiveFilterFields())
                    .first()
                    .value() || catchAllCohortName;
                _.findWhere(cohorts, {cohortName: selectedCohort}).selected = true;
            }

            return {
                cohorts: cohorts,
                // Translators: "Cohort Groups" refers to groups of students within a course.
                selectDisplayName: gettext('Cohort Groups')
            };
        },
        onSelectCohort: function (event) {
            // Sends a request to the server for the learner list filtered by
            // cohort then resets focus.
            event.preventDefault();
            this.collection.setFilterField('cohort', $(event.currentTarget).find('option:selected').val());
            this.collection.refresh();
            $('#learner-app-focusable').focus();
        }
    });

    return CohortFilter;
});
