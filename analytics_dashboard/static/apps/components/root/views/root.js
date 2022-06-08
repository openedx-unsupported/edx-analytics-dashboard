/**
 * A layout view to manage app page rendering.
 *
 * Options:
 *  - pageModel: PageModel object
 *  - appClass: CSS class to prepend in root template HTML
 */
define((require) => {
  'use strict';

  const _ = require('underscore');
  const Marionette = require('marionette');

  const AlertView = require('components/alert/views/alert-view');
  const HeaderView = require('components/header/views/header');
  const rootTemplate = require('components/root/templates/root.underscore');

  const RootView = Marionette.LayoutView.extend({
    template: _.template(rootTemplate),

    templateHelpers() {
      return this.options;
    },

    regions(options) {
      return {
        alert: _.template('.<%= appClass %>-alert-region')(options),
        header: _.template('.<%= appClass %>-header-region')(options),
        main: _.template('.<%= appClass %>-main-region')(options),
        navigation: _.template('.<%= appClass %>-navigation-region')(options),
      };
    },

    childEvents: {
      appError: 'onAppError',
      appWarning: 'onAppWarning',
      clearError: 'onClearError',
      setFocusToTop: 'onSetFocusToTop',
    },

    initialize(options) {
      this.options = _.defaults({ displayHeader: true }, options);
    },

    onRender() {
      if (this.options.displayHeader) {
        this.showChildView('header', new HeaderView({
          model: this.options.pageModel,
        }));
      }
    },

    onAppError(childView, options) {
      this.showAlert('error', options.title, options.description);
    },

    onAppWarning(childView, options) {
      this.showAlert('info', options.title, options.description);
    },

    onClearError() {
      this.hideAlert();
    },

    /**
         * Renders an alert view.
         *
         * @param {string} type - the type of alert that should be shown.  Alert
         * types are defined in the AlertView module.
         * @param {string} title - the title of the alert.
         * @param {string} description - the description of the alert.
         * @param {object} link - the link for the alert. Has key "url"
         * (the href) and key "text" (the display text for the link).
         */
    showAlert(type, title, description, link) {
      this.showChildView('alert', new AlertView({
        alertType: type,
        title,
        body: description,
        link,
      }));
    },

    /**
         * Hides the alert view, if active.
         */
    hideAlert() {
      this.getRegion('alert').empty();
    },
  });

  return RootView;
});
