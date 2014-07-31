define(['utils/utils'], function(Utils) {
    'use strict';

    describe('Utils', function () {
        it('should return node attributes', function () {
            var actualAttributes,
                element;

            // create your node with attributes
            element = document.createElement('div');
            element.setAttribute('attribute', 'myAttribute');
            element.setAttribute('data-type', 'my-data-type');
            element.setAttribute('data-category', 'my-data-category');
            element.setAttribute('data-event', 'my-data-event');

            actualAttributes = Utils.getNodeProperties(element.attributes);
            expect(actualAttributes).toEqual({
                    attribute: 'myAttribute',
                    'data-type': 'my-data-type',
                    'data-category': 'my-data-category',
                    'data-event': 'my-data-event'
            });

            actualAttributes = Utils.getNodeProperties(element.attributes,
                'data-');
            expect(actualAttributes).toEqual({
                'type': 'my-data-type',
                'category': 'my-data-category',
                'event': 'my-data-event'
            });

            actualAttributes = Utils.getNodeProperties(element.attributes,
                'data-', ['data-type', 'data-category']);
            expect(actualAttributes).toEqual({
                'event': 'my-data-event'
            });
        });

    });
});
