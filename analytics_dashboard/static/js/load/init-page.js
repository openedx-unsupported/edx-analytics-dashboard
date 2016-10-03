/**
 * Initializes page with the model and various UI elements that need JS hooks.
 */
define([
    'jquery', 'utils/fix-language', 'load/init-models', 'load/init-tooltips'
], function($, fixLanguage, models) {
    'use strict';

    // set the standardized language code
    window.language = fixLanguage(window.language);

    // initialize tracking
    require(['load/init-tracking'], function(initTracking) {
        initTracking(models);
    });

    return {
        models: models
    };
});
