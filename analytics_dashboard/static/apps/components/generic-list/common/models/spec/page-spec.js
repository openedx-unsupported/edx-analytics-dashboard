define((require) => {
  'use strict';

  const PageModel = require('components/generic-list/common/models/page');
  const $ = require('jquery');

  describe('PageModel', () => {
    const titleConstantPart = 'edx/DemoX/Demo_Course | Open edX Insights';

    beforeEach(() => {
      // Setup default page title
      $('title').text(`List - ${titleConstantPart}`);
    });

    it('should have all the expected default fields', () => {
      const page = new PageModel();
      expect(page.attributes).toEqual({
        title: '',
        lastUpdated: undefined,
      });
    });

    it('should update <title> element on title attribute change', () => {
      const page = new PageModel();
      page.set('title', 'foo');
      expect($('title').text()).toEqual(`foo - ${titleConstantPart}`);
    });
  });
});
