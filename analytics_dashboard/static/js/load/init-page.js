/**
 * Initializes page with the model and various UI elements that need JS hooks.
 */
const initTracking = require('load/init-tracking');

define([
  'jquery', 'load/init-models', 'load/init-tooltips',
], ($, models) => {
  'use strict';

  // initialize tracking
  initTracking(models);

  return {
    models,
  };
});
