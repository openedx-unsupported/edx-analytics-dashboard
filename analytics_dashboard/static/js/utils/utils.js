define(['moment', 'underscore'], function (moment, _) {
    'use strict';
    var utils = {
        /**
         * Returns the attributes of a node.
         *
         * @param nodeAttributes Attributes of the node.
         * @param startsWithAndStrip Filters only attributes that start with
         *   this string and strips it off the attribute.
         * @param blackList Exclude attributes in this array of strings.
         * @returns Hash of found attributes.
         */
        getNodeProperties: function(nodeAttributes, startsWithAndStrip, blackList) {
            var properties = {};

            // fill in defaults
            startsWithAndStrip = startsWithAndStrip || '';
            blackList = blackList || [];

            _(_(nodeAttributes.length).range()).each(function(i){
                var nodeName = nodeAttributes.item(i).nodeName,
                    strippedName;
                // filter the attributes to just the ones that start with our
                // selection and aren't in our blacklist
                if(nodeName.indexOf(startsWithAndStrip) === 0 && !_(blackList).contains(nodeName)) {
                    // remove the
                    strippedName = nodeName.replace(startsWithAndStrip, '');
                    properties[strippedName] =
                        nodeAttributes.item(i).value;
                }
            });
            return properties;
        },

        /**
         * Takes a standard string date and returns a formatted date.
         * @param String date (ex. 2014-01-31)
         * @returns Returns a formatted date (ex. January 31, 2014)
         */
        formatDate: function(date) {
            return moment(date).format('MMMM D, YYYY');
        }
    };

    return utils;
});
