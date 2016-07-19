define(['moment', 'underscore', 'utils/globalization'], function(moment, _, Globalize) {
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

            _(_(nodeAttributes.length).range()).each(function(i) {
                var nodeName = nodeAttributes.item(i).nodeName,
                    strippedName;
                // filter the attributes to just the ones that start with our
                // selection and aren't in our blacklist
                if (nodeName.indexOf(startsWithAndStrip) === 0 && !_(blackList).contains(nodeName)) {
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
         * @param {(string|Date)} date (ex. 2014-01-31 or Date object)
         * @returns {string} Returns a formatted date (ex. January 31, 2014)
         */
        formatDate: function(date) {
            // moment accepts 'zh-cn' rather than 'zh' and 'zh-tw' rather than 'zh-hant'
            if (window.language === 'zh') {
                moment.locale('zh-cn');
            } else if (window.language === 'zh-hant') {
                moment.locale('zh-tw');
            } else {
                moment.locale(window.language);
            }
            return moment(date).format('LL');
        },

        /**
         * Format the given number for the current locale
         * @param value {number}
         * @returns {string}
         */
        localizeNumber: function(value, fractionDigits) {
            var options = {
                minimumFractionDigits: fractionDigits,
                maximumFractionDigits: fractionDigits
            };
            return Globalize.formatNumber(value, options);
        },

        /**
         * Format the given value as a percentage to be displayed to the end user.
         * @param value {number}
         * @returns {string}
         */
        formatDisplayPercentage: function(value) {
            var display = '< 1%';
            if (value >= 0.01 || value === 0) {
                display = Globalize.formatNumber(value, {
                    style: 'percent',
                    minimumFractionDigits: 1,
                    maximumFractionDigits: 1
                });
            }
            return display;
        },

        /**
         * Truncates text and adds ellipse at the end.
         */
        truncateText: function(text, characterLimit) {
            var formattedLabel = text.slice(0, characterLimit);
            if (characterLimit > 3 && _(text).size() > characterLimit) {
                formattedLabel = text.slice(0, characterLimit - 3) + gettext('...');
            }
            return formattedLabel;
        },

        /**
         * Converts seconds into MM:SS format.
         */
        formatTime: function(totalSeconds) {
            var minutes = Math.floor(totalSeconds / 60),
                seconds = totalSeconds - (minutes * 60);
            return _([minutes, seconds]).map(function(time) {
                if (time < 10) {
                    time = '0' + time;
                }
                return time;
            }).join(':');
        },

        /**
         * Converts the querystring portion of the URL into an object
         * mapping keys to argument values.
         *
         * Examples:
         * - 'foo=bar&baz=quux' -> {foo: 'bar', baz: 'quux'}
         * - 'foo=bar&' -> {foo: 'bar'}
         * - 'foo=bar&baz' -> {foo: 'bar', baz: ''}
         * - 'foo=bar&baz=' -> {foo: 'bar', baz: ''}
         * - '' -> {}
         * - null -> {}
         *
         * @param queryString {string}
         * @returns {object}
         */
        parseQueryString: function(queryString) {
            if (queryString) {
                return _(decodeURI(queryString).split('&')).map(function(namedVal) {
                    var keyValPair = namedVal.split('='),
                        params = {};
                    if (keyValPair.length === 1 && keyValPair[0]) {  // No value
                        params[keyValPair[0]] = '';
                    } else if (keyValPair.length === 2) {
                        params[keyValPair[0]] = keyValPair[1];
                    } else if (keyValPair.length > 2) {  // Have something like foo=bar=...
                        throw new TypeError('Each "&"-separated substring must either be a key or a key-value pair');
                    }
                    return params;
                }).reduce(function(memo, keyValPair) {
                    return _.extend(memo, keyValPair);
                });
            } else {
                return {};
            }
        }
    };

    return utils;
});
