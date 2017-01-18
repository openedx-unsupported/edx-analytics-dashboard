/**
 * Class for the pagination footer, which needs to set focus to
 * the top of the table after being clicked.
 */
define(function(require) {
    'use strict';

    var $ = require('jquery'),
        _ = require('underscore'),
        Backgrid = require('backgrid'),

        pageHandleTemplate = require('text!components/generic-list/list/templates/page-handle.underscore'),

        PagingFooter;

    // backgrid-paginator attaches itself to 'Backgrid.Extension'
    require('backgrid-paginator');

    PagingFooter = Backgrid.Extension.Paginator.extend({
        attributes: {
            role: 'navigation'
        },
        controls: {
            rewind: {title: 'First', label: '<span class="fa fa-fast-backward" aria-hidden="true"></span>'},
            back: {title: 'Previous', label: '<span class="fa fa-step-backward" aria-hidden="true"></span>'},
            forward: {title: 'Next', label: '<span class="fa fa-step-forward" aria-hidden="true"></span>'},
            fastForward: {title: 'Last', label: '<span class="fa fa-fast-forward" aria-hidden="true"></span>'}
        },
        initialize: function(options) {
            Backgrid.Extension.Paginator.prototype.initialize.call(this, options);
            this.options = options || {};
            this.appFocusable = $('#' + options.appClass + '-focusable');
            this.trackPageEventName = options.trackPageEventName || 'edx.bi.list.paged';
        },
        render: function() {
            var trackingModel = this.options.trackingModel,
                appFocusable = this.appFocusable,
                trackPageEventName = this.trackPageEventName;
            Backgrid.Extension.Paginator.prototype.render.call(this);

            // Pass the tracking model to the page handles so that they can trigger tracking event. Also passes the
            // focusable div that jumps the user to the top of the page and the tracking event name.
            // We have to do it in this awkward way because the pageHandle class cannot access the `this` scope of this
            // overall PagingFooter class.
            _(this.handles).each(function(handle) {
                /* eslint-disable no-param-reassign */
                handle.trackingModel = trackingModel;
                handle.appFocusable = appFocusable;
                handle.trackPageEventName = trackPageEventName;
                /* eslint-enable no-param-reassign */
            });
        },

        /**
         * NOTE: this PageHandle class is a subclass of PagingFooter. The `changePage` function is called internally by
         * Backgrid when the page handle is clicked by the user. We add some side-effects to the `changePage` function
         * here: sending a tracking event and refocusing the browser to the top of the table. This subclass needs
         * variables from the encompassing PagingFooter class in order to perform those side-effects and we pass them
         * down from the PagingFooter in its render function above.
         */
        pageHandle: Backgrid.Extension.PageHandle.extend({
            template: _.template(pageHandleTemplate),
            trackingModel: undefined,  // set by PagingFooter
            render: function() {
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
            changePage: function() {
                Backgrid.Extension.PageHandle.prototype.changePage.apply(this, arguments);
                if (!this.$el.hasClass('active') && !this.$el.hasClass('disabled')) {
                    this.appFocusable.focus();
                } else {
                    this.$('a').focus();
                }
                this.trackingModel.trigger('segment:track', this.trackPageEventName, {
                    category: this.pageIndex
                });
            }
        })
    });

    return PagingFooter;
});
