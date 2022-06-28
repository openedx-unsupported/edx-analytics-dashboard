define((require) => {
  'use strict';

  const CourseMetadataModel = require('learners/common/models/course-metadata');

  describe('CourseMetadataModel', () => {
    let server;

    beforeEach(() => {
      jasmine.clock().install();
      server = sinon.fakeServer.create();
    });

    afterEach(() => {
      jasmine.clock().uninstall();
      server.restore();
    });

    it('sets its url through the initialize function', () => {
      const url = '/resource/';
      expect(new CourseMetadataModel(null, { url }).url()).toBe(url);
    });

    it('triggers a serverError event on server errors', () => {
      const courseMetadata = new CourseMetadataModel(null, { url: '/resource/' });
      spyOn(courseMetadata, 'trigger');
      courseMetadata.fetch();
      server.requests[server.requests.length - 1].respond(500, {}, '{}');
      expect(courseMetadata.trigger).toHaveBeenCalledWith('serverError', 500, {});
    });

    it('triggers a networkError event on network errors', () => {
      const courseMetadata = new CourseMetadataModel(null, { url: '/resource/' });
      spyOn(courseMetadata, 'trigger');
      courseMetadata.fetch({ timeout: 1 });
      jasmine.clock().tick(2);
      expect(courseMetadata.trigger).toHaveBeenCalledWith('networkError', 'timeout');
    });

    it('categorizes engagement values', () => {
      const courseMetadata = new CourseMetadataModel({
        engagement_ranges: {
          problems_attempted: {
            class_rank_bottom: [0, 10],
            class_rank_average: [10, 25],
            class_rank_top: [25, null],
          },
          problem_attempts_per_completed: {
            class_rank_top: [1, 1.4],
            class_rank_average: [1.4, 5.8],
            class_rank_bottom: [5.8, null],
          },
        },
      }, { parse: true });

      expect(courseMetadata.getEngagementCategory('problems_attempted', 9)).toBe('classRankBottom');
      expect(courseMetadata.getEngagementCategory('problems_attempted', 12)).toBe('classRankMiddle');
      expect(courseMetadata.getEngagementCategory('problems_attempted', 100)).toBe('classRankTop');

      expect(courseMetadata.getEngagementCategory('problem_attempts_per_completed', 1.1)).toBe('classRankTop');
      expect(courseMetadata.getEngagementCategory('problem_attempts_per_completed', 3.3))
        .toBe('classRankMiddle');
      expect(courseMetadata.getEngagementCategory('problem_attempts_per_completed', 6)).toBe('classRankBottom');
    });

    it('parses nulls in ranges', () => {
      const courseMetadata = new CourseMetadataModel({
        engagement_ranges: {
          problems_attempted: {
            class_rank_bottom: [0, 10],
            class_rank_average: [10, null],
            class_rank_top: null,
          },
          problem_attempts_per_completed: {
            class_rank_top: [0, 10],
            class_rank_average: [10, null],
            class_rank_bottom: [null, null],
          },
        },
      }, { parse: true });
      expect(courseMetadata.get('engagement_ranges').problems_attempted.class_rank_bottom).toEqual([0, 10]);
      expect(courseMetadata.get('engagement_ranges').problems_attempted.class_rank_average)
        .toEqual([10, Infinity]);
      expect(courseMetadata.get('engagement_ranges').problems_attempted.class_rank_top).toEqual(null);
      expect(courseMetadata.get('engagement_ranges').problem_attempts_per_completed.class_rank_bottom)
        .toEqual([Infinity, Infinity]);
    });

    it('does not parse engagement date range', () => {
      const courseMetadata = new CourseMetadataModel({
        engagement_ranges: {
          date_range: {
            start: '2015-12-03',
            end: '2016-06-01',
          },
        },
      }, { parse: true });
      expect(courseMetadata.get('engagement_ranges').date_range.start).toEqual('2015-12-03');
      expect(courseMetadata.get('engagement_ranges').date_range.end).toEqual('2016-06-01');
    });

    describe('getFilterOptions', () => {
      it('returns filter options in expected format', () => {
        const courseMetadata = new CourseMetadataModel({
          cohorts: {
            chinchillas: 9876,
          },
        });
        expect(courseMetadata.getFilterOptions('cohorts')).toEqual([{
          name: 'chinchillas',
          displayName: 'chinchillas',
          count: 9876,
        }]);
      });

      it('returns undefined when no filter is found', () => {
        const courseMetadata = new CourseMetadataModel();
        expect(courseMetadata.getFilterOptions('dogs')).toBe(undefined);
      });
    });

    describe('inMetricRange', () => {
      it('returns true when value is in range', () => {
        const courseMetadata = new CourseMetadataModel();
        expect(courseMetadata.inMetricRange(1, [0, 2])).toBe(true);
        expect(courseMetadata.inMetricRange(10.5, [5, 11])).toBe(true);
        expect(courseMetadata.inMetricRange(44, [-Infinity, 45])).toBe(true);
        expect(courseMetadata.inMetricRange(59.3, [59, Infinity])).toBe(true);
      });

      it('returns false when value is out of range', () => {
        const courseMetadata = new CourseMetadataModel();
        expect(courseMetadata.inMetricRange(3, [0, 2])).toBe(false);
        expect(courseMetadata.inMetricRange(4.5, [5, 11])).toBe(false);
        expect(courseMetadata.inMetricRange(45, [-Infinity, 45])).toBe(false);
        expect(courseMetadata.inMetricRange(58.3, [59, Infinity])).toBe(false);
      });

      it('inf is included in ranges with an infinite upper bound', () => {
        const courseMetadata = new CourseMetadataModel();
        expect(courseMetadata.inMetricRange(Infinity, [0, Infinity])).toBe(true);
      });

      it('value is included in ranges where value is specified on both sides', () => {
        const courseMetadata = new CourseMetadataModel();
        expect(courseMetadata.inMetricRange(0, [0, 0])).toBe(true);
        expect(courseMetadata.inMetricRange(Infinity, [Infinity, Infinity])).toBe(true);
      });
    });
  });
});
