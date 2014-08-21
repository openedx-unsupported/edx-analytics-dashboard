define(['models/course-model', 'views/attribute-view'], function(CourseModel, AttributeView) {
    'use strict';

    describe('Attribute view', function () {

        it('should wait to render', function () {
            var attributeData = 'An Attribute',
                model = new CourseModel(),
                view = new AttributeView({
                    model: model,
                    modelAttribute: 'attributeData',
                    el: document.createElement('div')
                }),
                actual;

            actual = view.$el.text();
            expect(actual).toEqual('');

            // now update the model to see if the text is displayed
            model.set('attributeData', attributeData);
            actual = view.$el.text();
            expect(actual).toEqual(attributeData);
        });

        it('should render immediate if data is available', function () {
            var view = new AttributeView({
                    model: new CourseModel({attributeData: 'Another Attribute'}),
                    modelAttribute: 'attributeData',
                    el: document.createElement('div')
                }),
                actual;

            actual = view.$el.text();
            expect(actual).toEqual('Another Attribute');
        });
    });
});
