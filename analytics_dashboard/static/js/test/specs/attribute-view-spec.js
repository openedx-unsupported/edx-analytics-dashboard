define(['models/course-model', 'views/attribute-view'], (CourseModel, AttributeView) => {
  'use strict';

  describe('Attribute view', () => {
    it('should wait to render', () => {
      const attributeData = 'An Attribute';
      const model = new CourseModel();
      const view = new AttributeView({
        model,
        modelAttribute: 'attributeData',
        el: document.createElement('div'),
      });
      let actual;

      actual = view.$el.text();
      expect(actual).toEqual('');

      // now update the model to see if the text is displayed
      model.set('attributeData', attributeData);
      actual = view.$el.text();
      expect(actual).toEqual(attributeData);
    });

    it('should render immediate if data is available', () => {
      const view = new AttributeView({
        model: new CourseModel({ attributeData: 'Another Attribute' }),
        modelAttribute: 'attributeData',
        el: document.createElement('div'),
      });

      const actual = view.$el.text();
      expect(actual).toEqual('Another Attribute');
    });
  });
});
