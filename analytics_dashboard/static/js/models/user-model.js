define(['backbone'], function(Backbone) {
    'use strict';

    /**
     * Stores our user logic and information.
     */
    var UserModel = Backbone.Model.extend({
        defaults: {
            ignoreInReporting: false
        }
    });

    return UserModel;
});
