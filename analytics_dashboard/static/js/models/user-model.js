define(['backbone'], (Backbone) => {
  'use strict';

  /**
     * Stores our user logic and information.
     */
  const UserModel = Backbone.Model.extend({
    defaults: {
      ignoreInReporting: false,
    },
  });

  return UserModel;
});
