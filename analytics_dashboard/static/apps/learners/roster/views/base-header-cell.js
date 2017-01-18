define(function(require) {
    'use strict';

    var BaseHeaderCell = require('components/generic-list/list/views/base-header-cell'),

        LearnersBaseHeaderCell;

    LearnersBaseHeaderCell = BaseHeaderCell.extend({
        tooltips: {
            username: gettext('The name and username of this learner. Click to sort by username.'),
            problems_attempted: gettext('Number of unique problems this learner attempted.'),
            problems_completed: gettext('Number of unique problems the learner answered correctly.'),
            videos_viewed: gettext('Number of unique videos this learner played.'),
            // eslint-disable-next-line max-len
            problem_attempts_per_completed: gettext('Average number of attempts per correct problem. Learners with a relatively high value compared to their peers may be struggling.'),
            // eslint-disable-next-line max-len
            discussion_contributions: gettext('Number of contributions by this learner, including posts, responses, and comments.')
        },
        container: '.learners-table'
    });

    return LearnersBaseHeaderCell;
});
