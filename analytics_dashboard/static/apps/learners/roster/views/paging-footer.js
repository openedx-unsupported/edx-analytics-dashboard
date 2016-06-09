/**
 * Class for the pagination footer, which needs to set focus to
 * the top of the table after being clicked.
 */
define(function (require) {
    'use strict';

    var $ = require('jquery'),
        _ = require('underscore'),
        Backgrid = require('backgrid'),

        pageHandleTemplate = require('text!learners/roster/templates/page-handle.underscore'),

        PagingFooter;

    // backgrid-paginator attaches itself to 'Backgrid.Extension'
    require('backgrid-paginator');

    PagingFooter = Backgrid.Extension.Paginator.extend({
        attributes: {
            role: 'navigation'
        },
        controls: {
            rewind: {title: 'First', label: '<i class="fa fa-fast-backward" aria-hidden="true"></i>'},
            back: {title: 'Previous', label: '<i class="fa fa-step-backward" aria-hidden="true"></i>'},
            forward: {title: 'Next', label: '<i class="fa fa-step-forward" aria-hidden="true"></i>'},
            fastForward: {title: 'Last', label: '<i class="fa fa-fast-forward" aria-hidden="true"></i>'}
        },
        initialize: function (options) {
            Backgrid.Extension.Paginator.prototype.initialize.call(this, options);
            this.options = options || {};
        },
        render: function () {
            var self = this;
            Backgrid.Extension.Paginator.prototype.render.call(this);

            // pass the tracking model to the page handles so that they can trigger
            // tracking event
            _(this.handles).each(function (handle) {
                handle.trackingModel = self.options.trackingModel;
            });

        },
        pageHandle: Backgrid.Extension.PageHandle.extend({
            template: _.template(pageHandleTemplate),
            trackingModel: undefined,  // set by PagingFooter
            render: function () {
                var isHiddenFromSr = true,
                    srText;
                Backgrid.Extension.PageHandle.prototype.render.apply(this, arguments);
                if (this.isRewind) {
                    srText = gettext('first page');
                } else if (this.isBack) {
                    srText = gettext('previous page');
                } else if (this.isForward) {
                    srText = gettext('next page');
                } else if (this.isFastForward) {
                    srText = gettext('last page');
                } else {
                    srText = gettext('page') + ' ';
                    isHiddenFromSr = false;
                }
                this.$el.html(this.template({
                    title: this.title,
                    srText: srText,
                    isHiddenFromSr: isHiddenFromSr,
                    nonSrText: this.label,
                    isDisabled: this.$el.hasClass('disabled')
                }));
                this.delegateEvents();
                return this;
            },
            changePage: function () {
                Backgrid.Extension.PageHandle.prototype.changePage.apply(this, arguments);
                if (!this.$el.hasClass('active') && !this.$el.hasClass('disabled')) {
                    $('#learner-app-focusable').focus();
                } else {
                    this.$('a').focus();
                }
                this.trackingModel.trigger('segment:track', 'edx.bi.roster.paged', {
                    category: this.pageIndex
                });
            }
        })
    });

    return PagingFooter;
});
