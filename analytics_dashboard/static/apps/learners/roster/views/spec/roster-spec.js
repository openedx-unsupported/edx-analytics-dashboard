define((require) => {
  'use strict';

  const $ = require('jquery');
  const _ = require('underscore');
  const axe = require('axe-core');
  const SpecHelpers = require('uitk/utils/spec-helpers/spec-helpers');
  const URI = require('URI');

  const CourseMetadataModel = require('learners/common/models/course-metadata');
  const LearnerCollection = require('learners/common/collections/learners');
  const LearnerRosterView = require('learners/roster/views/roster');
  const TrackingModel = require('models/tracking-model');

  describe('LearnerRosterView', () => {
    const fixtureClass = 'roster-view-fixture';
    const perPage = 25;
    let server;

    const getLastRequest = function () {
      return server.requests[server.requests.length - 1];
    };

    const getLastRequestParams = function () {
      return (new URI(getLastRequest().url)).query(true);
    };

    const getResponseBody = function (numPages, pageNum) {
      let results;
      const page = pageNum || 1;
      if (numPages) {
        results = _.range(perPage * (page - 1), (perPage * (page - 1)) + perPage).map((index) => ({ name: `user ${index}`, username: `user_${index}` }));
      } else {
        results = [];
      }
      return {
        count: numPages * perPage,
        num_pages: numPages,
        results,
      };
    };

    const getRosterView = function (options) {
      const defaultOptions = _.defaults({}, options);
      const collection = defaultOptions.collection || new LearnerCollection(
        defaultOptions.collectionResponse,
        _.extend({ url: 'test-url' }, defaultOptions.collectionOptions),
      );
      const rosterView = new LearnerRosterView({
        collection,
        courseMetadata: defaultOptions.courseMetadataModel
                    || new CourseMetadataModel(defaultOptions.courseMetadata, { parse: true }),
        el: `.${fixtureClass}`,
        trackSubject: 'roster',
        hasData: true,
        trackingModel: new TrackingModel(),
        appClass: 'learners',
      }).render();
      rosterView.onBeforeShow();
      return rosterView;
    };

    const testTimeout = function (rosterView, actionFunction) {
      jasmine.clock().install();
      const ajaxSetup = $.ajaxSetup();
      $.ajaxSetup({ timeout: 1 });
      spyOn(rosterView, 'trigger');
      actionFunction();
      jasmine.clock().tick(2);
      expect(rosterView.trigger).toHaveBeenCalledWith(
        'appError',
        {
          title: 'Network error',
          description: 'Your request could not be processed. Reload the page to try again.',
        },
      );
      jasmine.clock().uninstall();
      $.ajaxSetup(ajaxSetup);
    };

    const verifyErrorHandling = function (rosterView, status) {
      getLastRequest().respond(status, {}, '');
      expect(rosterView.trigger).toHaveBeenCalledWith('appError', jasmine.any(Object));
    };

    const executeSearch = function (searchString) {
      $('#search-learners').val(searchString);
      $('#search-learners').keyup(); // Triggers rendering of the clear search control
      $('#search-learners').submit();
    };

    const clickPagingControl = function (titleSelector) {
      $(`a[title="${titleSelector}"]`).click();
    };

    beforeEach(() => {
      setFixtures(`<div class="${fixtureClass}"></div>`);
      server = sinon.fakeServer.create();
    });

    afterEach(() => {
      server.restore();
    });

    it('renders a list of learners', () => {
      const generateEngagements = function () {
        return {
          discussion_contributions: Math.floor(Math.random() * 10),
          problems_attempted: Math.floor(Math.random() * 10),
          problems_completed: Math.floor(Math.random() * 10),
          videos_viewed: Math.floor(Math.random() * 10),
          problem_attempts_per_completed: Math.floor(Math.random() * 10),
        };
      };
      const learners = [
        { name: 'agnes', username: 'agnes', engagements: generateEngagements() },
        { name: 'lily', username: 'lily', engagements: generateEngagements() },
        { name: 'zita', username: 'zita', engagements: generateEngagements() },
      ];
      const rosterView = getRosterView({
        collectionResponse: { results: learners },
        collectionOptions: { parse: true },
      });
      _.chain(_.zip(learners, rosterView.$('tbody tr'))).each((learnerAndTr) => {
        const learner = learnerAndTr[0];
        const tr = learnerAndTr[1];
        expect($(tr).find('th.learner-name-username-cell .name')).toContainText(learner.name);
        expect($(tr).find('th.learner-name-username-cell .username')).toContainText(learner.username);
        expect($(tr).find('td.discussion_contributions'))
          .toContainText(learner.engagements.discussion_contributions);
        expect($(tr).find('td.problems_attempted'))
          .toContainText(learner.engagements.problems_attempted);
        expect($(tr).find('td.problem_attempts_per_completed'))
          .toContainText(learner.engagements.problem_attempts_per_completed);
        expect($(tr).find('td.videos_viewed'))
          .toContainText(learner.engagements.videos_viewed);
      });
    });

    it('categorizes engagement values', () => {
      const learners = [{
        name: 'agnes',
        username: 'agnes',
        engagements: {
          discussion_contributions: 10,
          problems_attempted: 100,
          problems_completed: 32,
          videos_viewed: 1,
          problem_attempts_per_completed: 1.56,
        },
      }];
      const engagementRanges = {
        problems_attempted: {
          class_rank_bottom: [0, 10],
          class_rank_average: [11, 25],
          class_rank_top: [26, null],
        },
        videos_viewed: {
          class_rank_bottom: [0, 1],
          class_rank_average: [1, 10],
          class_rank_top: [10, null],
        },
        problems_completed: {
          class_rank_bottom: [0, 10],
          class_rank_average: [11, 50],
          class_rank_top: [50, null],
        },
        problem_attempts_per_completed: {
          class_rank_top: [1, 1.6],
          class_rank_average: [1.6, 25],
          class_rank_bottom: [26, 60],
        },
        discussion_contributions: {
          class_rank_bottom: [0, 100],
          class_rank_average: [100, 125],
          class_rank_top: [125, null],
        },
      };
      const rosterView = getRosterView({
        collectionResponse: { results: learners },
        collectionOptions: { parse: true },
        courseMetadata: {
          engagement_ranges: engagementRanges,
        },
      });
      const $tr = $(rosterView.$('tbody tr'));

      expect($tr.children('td.discussion_contributions'))
        .toHaveClass('learner-cell-rank-bottom');
      expect($tr.children('td.discussion_contributions ')).toHaveAttr('aria-label', '10 low');
      expect($tr.find('td.problems_completed'))
        .toHaveClass('learner-cell-rank-middle');
      expect($tr.find('td.problems_attempted'))
        .toHaveClass('learner-cell-rank-top');
      expect($tr.find('td.problems_attempted')).toHaveAttr('aria-label', '100 high');
      expect($tr.find('td.problem_attempts_per_completed'))
        .toHaveClass('learner-cell-rank-top');
      expect($tr.find('td.problem_attempts_per_completed')).toHaveAttr('aria-label', '1.56 high');
      expect($tr.find('td.videos_viewed'))
        .toHaveClass('learner-cell-rank-middle');
    });

    it('formats numbers', () => {
      const learners = [{
        name: 'agnes',
        username: 'agnes',
        engagements: {
          discussion_contributions: 0,
          problems_attempted: 0,
          problems_completed: 32,
          videos_viewed: 0,
          problem_attempts_per_completed: 0.566,
        },
      }];
      const rosterView = getRosterView({
        collectionResponse: { results: learners },
        collectionOptions: { parse: true },
      });
      const $tr = $(rosterView.$('tbody tr'));

      expect($tr.children('td.discussion_contributions'))
        .toContainText('0');
      expect($tr.find('td.problems_completed'))
        .toContainText('32');
      expect($tr.find('td.problems_attempted'))
        .toContainText('0');
      expect($tr.find('td.problem_attempts_per_completed'))
        .toContainText('0.6');
      expect($tr.find('td.videos_viewed'))
        .toContainText('0');
    });

    it('displays "infinite" metrics as N/A', () => {
      const learners = [{
        name: 'agnes',
        username: 'agnes',
        engagements: {
          discussion_contributions: 0,
          problems_attempted: 0,
          problems_completed: 0,
          videos_viewed: 0,
          problem_attempts_per_completed: null,
        },
      }];
      const rosterView = getRosterView({
        collectionResponse: { results: learners },
        collectionOptions: { parse: true },
      });
      const $tr = $(rosterView.$('tbody tr'));

      expect($tr.children('td.discussion_contributions'))
        .toContainText('0');
      expect($tr.find('td.problems_completed'))
        .toContainText('0');
      expect($tr.find('td.problems_attempted'))
        .toContainText('0');
      expect($tr.find('td.problem_attempts_per_completed'))
        .toContainText('N/A');
      expect($tr.find('td.videos_viewed'))
        .toContainText('0');
    });

    describe('table headers', () => {
      it('has tooltips', () => {
        const headerClasses = [
          'username',
          'videos_viewed',
          'problems_completed',
          'problems_attempted',
          'discussion_contributions',
          'problem_attempts_per_completed',
        ];

        getRosterView({
          collectionResponse: getResponseBody(1, 1),
          collectionOptions: { parse: true },
        });

        _(headerClasses).each((headerClass) => {
          const $heading = $(`th.${headerClass}`).focusin();

          // aria tag is added when tooltip is displayed (e.g. on focus)
          expect($heading).toHaveAttr('aria-describedby');
          const $tooltip = $(`#${$heading.attr('aria-describedby')}`);
          expect($tooltip.text().length).toBeGreaterThan(0);
        });
      });
    });

    describe('sorting', () => {
      const getSortingHeaderLink = function (headerClass) {
        return $(`th.${headerClass} button`);
      };

      const clickSortingHeader = function (headerClass) {
        getSortingHeaderLink(headerClass).click();
      };

      const expectSortCalled = function (sortField, sortValue) {
        expect(getLastRequestParams()).toEqual(jasmine.objectContaining({
          order_by: sortField,
          sort_order: sortValue,
        }));
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(1, 1)));
        expect(getSortingHeaderLink(sortField).find('span')).toHaveClass(`fa-sort-${sortValue}`);
      };

      const executeSortTest = function (field) {
        expect(getSortingHeaderLink(field).find('span.fa')).toHaveClass('fa-sort');
        clickSortingHeader(field);
        expectSortCalled(field, 'asc');
        clickSortingHeader(field);
        expectSortCalled(field, 'desc');
      };

      beforeEach(function () {
        this.rosterView = getRosterView({
          collectionResponse: getResponseBody(1, 1),
          collectionOptions: { parse: true },
        });
      });

      it('can sort by username', () => {
        executeSortTest('username');
      });

      it('can sort by discussion contributions', () => {
        executeSortTest('discussion_contributions');
      });

      it('can sort by problems attempted', () => {
        executeSortTest('problems_attempted');
      });

      it('can sort by attempts per problem completed', () => {
        executeSortTest('problem_attempts_per_completed');
      });

      it('can sort by videos watched', () => {
        executeSortTest('videos_viewed');
      });

      it('handles server errors', function () {
        spyOn(this.rosterView, 'trigger');
        clickSortingHeader('username');
        verifyErrorHandling(this.rosterView, 500);
        clickSortingHeader('username');
        verifyErrorHandling(this.rosterView, 504);
      });

      it('handles network errors', function () {
        testTimeout(this.rosterView, () => {
          clickSortingHeader('username');
        });
      });

      it('goes to the first page after applying a sort', function () {
        this.rosterView = getRosterView({
          collectionResponse: getResponseBody(2, 1),
          collectionOptions: { parse: true },
        });
        clickPagingControl('Page 2');
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(2, 2)));
        expect(this.rosterView.$('a[title="Page 2"]').parent('li')).toHaveClass('active');
        clickSortingHeader('username');
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(2, 2)));
        expect(getLastRequestParams()).toEqual(jasmine.objectContaining({
          page: '1',
          order_by: 'username',
        }));
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(2, 1)));
        expect(this.rosterView.$('a[title="Page 1"]').parent('li')).toHaveClass('active');
      });

      it('triggers a tracking event', function () {
        const triggerSpy = spyOn(this.rosterView.options.trackingModel, 'trigger');
        const headerClasses = [
          'username',
          'videos_viewed',
          'problems_attempted',
          'problems_completed',
          'discussion_contributions',
          'problem_attempts_per_completed',
        ];
        _.each(headerClasses, (column) => {
          executeSortTest(column);
          expect(triggerSpy).toHaveBeenCalledWith('segment:track', 'edx.bi.roster.sorted', {
            category: `${column}_asc`,
          });
          expect(triggerSpy).toHaveBeenCalledWith('segment:track', 'edx.bi.roster.sorted', {
            category: `${column}_desc`,
          });
        });
      });
    });

    describe('paging', () => {
      const createTwoPageRoster = function () {
        return getRosterView({
          collectionResponse: getResponseBody(2, 1),
          collectionOptions: { parse: true },
        });
      };

      const expectLinkStates = function (rosterView, activeLinkTitle, disabledLinkTitles) {
        rosterView.$('li > a').each((_index, link) => {
          const $link = $(link);
          const $parentLi = $link.parent('li');
          if ($link.attr('title') === activeLinkTitle) {
            expect($parentLi).toHaveClass('active');
            expect($parentLi).not.toHaveClass('disabled');
          } else if (_.contains(disabledLinkTitles, $link.attr('title'))) {
            expect($parentLi).not.toHaveClass('active');
            expect($parentLi).toHaveClass('disabled');
          } else {
            expect($parentLi).not.toHaveClass('active');
            expect($parentLi).not.toHaveClass('disabled');
          }
        });
      };

      const expectRequestedPage = function (pageNum) {
        expect(getLastRequestParams()).toEqual(jasmine.objectContaining({
          page: pageNum.toString(),
        }));
      };

      it('triggers a tracking event', () => {
        const rosterView = createTwoPageRoster();
        const triggerSpy = spyOn(rosterView.options.trackingModel, 'trigger');

        // verifies the initial state
        expectLinkStates(rosterView, 'Page 1', ['First', 'Previous']);

        // navigate to page 2
        clickPagingControl('Next');
        expectRequestedPage(2);
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(2, 2)));
        expectLinkStates(rosterView, 'Page 2', ['Next', 'Last']);
        expect(triggerSpy).toHaveBeenCalledWith('segment:track', 'edx.bi.roster.paged', {
          category: 2,
        });
      });

      it('can jump to a particular page', () => {
        const rosterView = createTwoPageRoster();
        clickPagingControl('Page 2');
        expectRequestedPage(2);
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(2, 2)));
        expectLinkStates(rosterView, 'Page 2', ['Next', 'Last']);
      });

      it('can navigate to the next/previous page', () => {
        const rosterView = createTwoPageRoster();

        clickPagingControl('Next');
        expectRequestedPage(2);
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(2, 2)));
        expectLinkStates(rosterView, 'Page 2', ['Next', 'Last']);

        clickPagingControl('Previous');
        expectRequestedPage(1);
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(2, 1)));
        expectLinkStates(rosterView, 'Page 1', ['First', 'Previous']);
      });

      it('does not enable pagination controls for unreachable pages', () => {
        const rosterView = createTwoPageRoster();
        // Verify no request, no view change
        clickPagingControl('Previous');
        expect(server.requests.length).toBe(0);
        expectLinkStates(rosterView, 'Page 1', ['First', 'Previous']);
      });

      it('handles gateway timeouts', () => {
        const rosterView = createTwoPageRoster();
        spyOn(rosterView, 'trigger');
        clickPagingControl('Next');
        verifyErrorHandling(rosterView, 504);
      });

      it('handles server errors', () => {
        const rosterView = createTwoPageRoster();
        spyOn(rosterView, 'trigger');
        clickPagingControl('Next');
        verifyErrorHandling(rosterView, 500);
      });

      it('handles network errors', () => {
        const rosterView = createTwoPageRoster();
        testTimeout(rosterView, () => {
          clickPagingControl('Next');
        });
      });
    });

    describe('search', () => {
      const expectSearchedFor = function (searchString) {
        expect(getLastRequestParams()).toEqual(jasmine.objectContaining({
          text_search: searchString,
        }));
      };

      it('renders the current search string', () => {
        const searchString = 'search string';
        const collection = new LearnerCollection();
        collection.setSearchString(searchString);
        const rosterView = getRosterView({ collection });
        expect(rosterView.$('#search-learners')).toHaveValue(searchString);
      });

      it('can search for arbitrary strings', () => {
        const searchString = 'search string';
        getRosterView();
        executeSearch(searchString);
        expect(getLastRequestParams()).toEqual(jasmine.objectContaining({
          text_search: searchString,
        }));
      });

      it('renders itself whenever the collection changes', function () {
        const rosterView = getRosterView({ courseMetadataModel: this.courseMetadata });
        const searchString = 'search string';
        executeSearch(searchString);
        expect(getLastRequestParams()).toEqual(jasmine.objectContaining({
          text_search: searchString,
        }));
        expect(rosterView.$('#search-learners')).toHaveValue(searchString);
        rosterView.options.collection.unsetSearchString();
        rosterView.options.collection.refresh();
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
        expect(rosterView.$('#search-learners')).toHaveValue('');
      });

      it('can clear the search with the clear link', () => {
        const searchString = 'search string';
        getRosterView();
        executeSearch(searchString);
        expectSearchedFor(searchString);
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(1, 1)));
        $('.clear.btn').click();
        expect(getLastRequestParams().text_search).toBeUndefined();
      });

      it('can clear the search by searching the empty string', () => {
        const searchString = 'search string';
        const rosterView = getRosterView();
        executeSearch(searchString);
        expectSearchedFor(searchString);
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(1, 1)));
        executeSearch('');
        expect(rosterView.options.collection.getSearchString()).toBeNull();
        expect(getLastRequestParams().text_search).toBeUndefined();
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(1, 1)));
      });

      it('triggers a tracking event', () => {
        const rosterView = getRosterView();
        const searchString = 'search string';
        const triggerSpy = spyOn(rosterView.options.trackingModel, 'trigger');

        executeSearch(searchString);
        expectSearchedFor(searchString);
        expect(triggerSpy).toHaveBeenCalledWith('segment:track', 'edx.bi.roster.searched', {
          category: 'search',
        });
      });

      it('handles server errors', () => {
        const rosterView = getRosterView();
        spyOn(rosterView, 'trigger');
        executeSearch('test search');
        verifyErrorHandling(rosterView, 504);
        executeSearch('test search');
        verifyErrorHandling(rosterView, 500);
      });

      it('handles network errors', () => {
        const rosterView = getRosterView();
        testTimeout(rosterView, () => {
          executeSearch('test search');
        });
      });
    });

    describe('filtering', () => {
      const expectCanFilterBy = function (filterKey, filterValue) {
        let expectedRequestSubset;
        $('select').val(filterValue);
        $('select').change();
        if (filterValue) {
          expectedRequestSubset = {};
          expectedRequestSubset[filterKey] = filterValue;
          expect(getLastRequestParams()).toEqual(jasmine.objectContaining(expectedRequestSubset));
        } else {
          expect(Object.prototype.hasOwnProperty.call(getLastRequestParams(), 'filterKey')).toBe(false);
        }
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(1, 1)));
        expect($(`option[value="${filterValue}"]`)).toBeSelected();
      };

      it('renders filters in alphabetical order', () => {
        const rosterView = getRosterView({
          courseMetadata: {
            cohorts: {
              zebra: 1,
              antelope: 2,
            },
          },
        });
        const options = rosterView.$('.learners-filter option');
        expect(options[1]).toHaveText('antelope (2)');
        expect(options[2]).toHaveText('zebra (1)');
      });

      SpecHelpers.withConfiguration({
        'by cohort': [
          'cohort', // filter field name
          'cohorts', // course metadata field name
          { 'Cohort A': 1, 'Cohort B': 2 }, // default cohort metadata
        ],
        'by enrollment track': [
          'enrollment_mode', // filter field name
          'enrollment_modes', // course metadata field name
          { verified: 1, audit: 2 }, // default enrollment modes
        ],
      }, function (filterFieldName, courseMetadataFieldName, filterOptions) {
        const courseMetadataAttributes = {};
        courseMetadataAttributes[courseMetadataFieldName] = filterOptions;
        this.courseMetadata = new CourseMetadataModel(courseMetadataAttributes);
        this.filterFieldName = filterFieldName;
        this.filterOptions = filterOptions;
        [this.firstFilterOption] = _.keys(this.filterOptions);
      }, () => {
        it('renders the filter which is currently applied', function () {
          const { firstFilterOption } = this;
          const collection = new LearnerCollection();
          collection.setFilterField(this.filterFieldName, firstFilterOption);
          const rosterView = getRosterView({
            courseMetadataModel: this.courseMetadata,
            collection,
          });
          expect(rosterView.$(`.learners-filter option[value="${firstFilterOption}"]`)).toBeSelected();
        });

        it('only renders when filter options are provided', function () {
          let rosterView;

          // Doesn't render when no filter options are provided.
          rosterView = getRosterView({ courseMetadata: {} });
          expect(rosterView.$('.learners-filter').children()).not.toExist();

          // Does render when filter options are provided.
          rosterView = getRosterView({ courseMetadataModel: this.courseMetadata });
          const selectOptions = rosterView.$('.learners-filter option').get();
          const defaultSelectOption = selectOptions[0];

          expect(defaultSelectOption).toBeSelected();
          expect(defaultSelectOption).toHaveValue('');
          expect(defaultSelectOption).toHaveText('All');

          _.chain(this.filterOptions)
            .pairs()
            .sortBy(0) // we expect the filter options to appear in alphabetical order
            .zip(_.rest(selectOptions))
            .each((filterAndSelectOption) => {
              const filterOption = filterAndSelectOption[0];
              const filterOptionKey = filterOption[0];
              const learnerCount = filterOption[1];
              const selectOption = filterAndSelectOption[1];
              expect(selectOption).not.toBeSelected();
              expect(selectOption).toHaveValue(filterOptionKey);
              expect(selectOption).toHaveText(`${filterOptionKey} (${learnerCount})`);
            });
        });

        it('can execute a filter', function () {
          getRosterView({ courseMetadataModel: this.courseMetadata });
          expectCanFilterBy(this.filterFieldName, this.firstFilterOption);
          expectCanFilterBy(this.filterFieldName, '');
        });

        it('renders itself whenever the collection changes', function () {
          const rosterView = getRosterView({ courseMetadataModel: this.courseMetadata });
          expectCanFilterBy(this.filterFieldName, this.firstFilterOption);
          rosterView.collection.unsetAllFilterFields();
          rosterView.collection.refresh();
          getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
          expect(rosterView.$('select option:selected')).toHaveValue('');
        });

        it('triggers a tracking event', function () {
          const rosterView = getRosterView({ courseMetadataModel: this.courseMetadata });
          const { filterFieldName } = this;
          const triggerSpy = spyOn(rosterView.options.trackingModel, 'trigger');

          expectCanFilterBy(filterFieldName, this.firstFilterOption);
          expect(triggerSpy).toHaveBeenCalledWith('segment:track', 'edx.bi.roster.filtered', {
            category: filterFieldName,
          });
        });

        it('sets focus to the top after filtering', function () {
          const { filterFieldName } = this;
          getRosterView({ courseMetadataModel: this.courseMetadata });
          spyOn($.fn, 'focus');
          expectCanFilterBy(filterFieldName, this.firstFilterOption);
          expect($('#learner-app-focusable').focus).toHaveBeenCalled();
        });

        it('handles server errors', function () {
          const rosterView = getRosterView({ courseMetadataModel: this.courseMetadata });
          spyOn(rosterView, 'trigger');
          rosterView.$('select').val(this.firstFilterOption);
          rosterView.$('select').change();
          verifyErrorHandling(rosterView, 500);
        });

        it('handles network errors', function () {
          const rosterView = getRosterView({ courseMetadataModel: this.courseMetadata });
          testTimeout(rosterView, () => {
            rosterView.$('select').val(this.firstFilterOption);
            rosterView.$('select').change();
          });
        });
      });
    });

    describe('activity date range', () => {
      it('renders dates', () => {
        const rosterView = getRosterView({
          courseMetadata: {
            engagement_ranges: {
              date_range: {
                start: '2016-01-12',
                end: '2016-03-30',
              },
            },
          },
        });
        expect(rosterView.$('.activity-date-range'))
          .toContainText('Activity between January 12, 2016 - March 30, 2016');
      });

      it('renders n/a when no date range available', () => {
        const rosterView = getRosterView();
        expect(rosterView.$('.activity-date-range'))
          .toContainText('Activity between n/a - n/a');
      });
    });

    describe('active filters', () => {
      const expectNoActiveFilters = function (rosterView) {
        expect(rosterView.$('#active-filters-title')).not.toExist();
        expect(rosterView.$('.action-clear-all-filters')).not.toExist();
      };

      const expectActiveFilters = function (rosterView, options) {
        const activeFiltersTitle = rosterView.$('#active-filters-title');
        const clearAllButton = rosterView.$('.action-clear-all-filters');
        const activeFilters = rosterView.$('.active-filters');
        const activeSearch = activeFilters.find('.filter-text_search');
        const activeCohort = activeFilters.find('.filter-cohort');
        const activeEngagement = activeFilters.find('.filter-ignore_segments');
        const activeEnrollmentTrack = activeFilters.find('.filter-enrollment_mode');
        const removeFilterText = 'Click to remove this filter';

        expect(activeFiltersTitle).toExist();
        expect(activeFilters.find('.filter').length).toEqual(_.keys(options).length);
        expect(clearAllButton).toExist();

        if (options.search) {
          expect(activeSearch).toContainText(`"${options.search}"`);
          expect(activeSearch.find('.sr-only')).toContainText(removeFilterText);
        } else {
          expect(activeSearch).not.toExist();
        }

        if (options.cohort) {
          expect(activeCohort).toContainText(`Cohort: ${options.cohort}`);
          expect(activeCohort.find('.sr-only')).toContainText(removeFilterText);
        } else {
          expect(activeCohort).not.toExist();
        }

        if (options.enrollmentTrack) {
          expect(activeEnrollmentTrack).toContainText(`Enrollment Track: ${options.enrollmentTrack}`);
          expect(activeEnrollmentTrack.find('.sr-only')).toContainText(removeFilterText);
        } else {
          expect(activeEnrollmentTrack).not.toExist();
        }

        if (options.engagement) {
          expect(activeEngagement).toContainText('Active Learners');
          expect(activeEngagement.find('.sr-only')).toContainText(removeFilterText);
        } else {
          expect(activeEngagement).not.toExist();
        }
      };

      it('does not render when there are no active filters', () => {
        expectNoActiveFilters(getRosterView());
      });

      it('renders a search filter', () => {
        const rosterView = getRosterView();
        rosterView.options.collection.setSearchString('hello, world');
        rosterView.options.collection.refresh();
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
        expectActiveFilters(rosterView, { search: 'hello, world' });
      });

      it('renders a cohort filter', () => {
        const rosterView = getRosterView();
        rosterView.options.collection.setFilterField('cohort', 'labrador');
        rosterView.options.collection.refresh();
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
        expectActiveFilters(rosterView, { cohort: 'Labrador' });
      });

      it('renders an enrollment track filter', () => {
        const rosterView = getRosterView();
        rosterView.options.collection.setFilterField('enrollment_mode', 'honor');
        rosterView.options.collection.refresh();
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
        expectActiveFilters(rosterView, { enrollmentTrack: 'Honor' });
      });

      it('renders an engagement filter', () => {
        const rosterView = getRosterView();
        rosterView.options.collection.setFilterField('ignore_segments', 'inactive');
        rosterView.options.collection.refresh();
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
        expectActiveFilters(rosterView, { engagement: 'inactive' });
      });

      it('renders multiple filters', () => {
        const rosterView = getRosterView();
        rosterView.options.collection.setSearchString('foo');
        rosterView.options.collection.setFilterField('cohort', 'labrador');
        rosterView.options.collection.setFilterField('enrollment_mode', 'honor');
        rosterView.options.collection.refresh();
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
        expectActiveFilters(rosterView, {
          search: 'foo',
          cohort: 'Labrador',
          enrollmentTrack: 'Honor',
        });
      });

      it('can clear a search', () => {
        const rosterView = getRosterView();
        rosterView.options.collection.setFilterField('cohort', 'labrador');
        rosterView.options.collection.setSearchString('foo');
        rosterView.options.collection.refresh();
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
        expectActiveFilters(rosterView, {
          search: 'foo',
          cohort: 'Labrador',
        });
        rosterView.$('.active-filters .filter-text_search .action-clear-filter').click();
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
        expect(rosterView.options.collection.hasActiveSearch()).toBe(false);
        expectActiveFilters(rosterView, { cohort: 'Labrador' });
      });

      it('can clear a filter', () => {
        const rosterView = getRosterView();
        rosterView.options.collection.setFilterField('cohort', 'labrador');
        rosterView.options.collection.setSearchString('foo');
        rosterView.options.collection.refresh();
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
        expectActiveFilters(rosterView, {
          search: 'foo',
          cohort: 'Labrador',
        });
        rosterView.$('.active-filters .filter-cohort .action-clear-filter').click();
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
        expectActiveFilters(rosterView, { search: 'foo' });
        expect(rosterView.collection.getFilterFieldValue('cohort')).not.toBe('labrador');
      });

      it('can clear all the filters', () => {
        const rosterView = getRosterView();
        rosterView.options.collection.setSearchString('foo');
        rosterView.options.collection.setFilterField('cohort', 'labrador');
        rosterView.options.collection.setFilterField('enrollment_mode', 'honor');
        rosterView.options.collection.refresh();
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
        expectActiveFilters(rosterView, {
          search: 'foo',
          cohort: 'Labrador',
          enrollmentTrack: 'Honor',
        });
        rosterView.$('.action-clear-all-filters').click();
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
        expectNoActiveFilters(rosterView);
      });

      it('handles server errors', function () {
        const rosterView = getRosterView({ courseMetadataModel: this.courseMetadata });
        spyOn(rosterView, 'trigger');
        rosterView.options.collection.setFilterField('cohort', 'labrador');
        rosterView.options.collection.refresh();
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
        rosterView.$('.active-filters .filter-cohort .action-clear-filter').click();
        verifyErrorHandling(rosterView, 500);
      });

      it('handles network errors', function () {
        const rosterView = getRosterView({ courseMetadataModel: this.courseMetadata });
        rosterView.options.collection.setFilterField('cohort', 'labrador');
        rosterView.options.collection.refresh();
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
        testTimeout(rosterView, () => {
          rosterView.$('.active-filters .filter-cohort .action-clear-filter').click();
        });
      });
    });

    describe('no results', () => {
      it('renders a "no results" view when there is no learner data in the initial collection', () => {
        const rosterView = getRosterView();
        expect(rosterView.$('.alert-information'))
          .toContainText('No learner data is currently available for your course.');
      });

      it('renders a "no results" view when there are no learners for the current search', () => {
        const rosterView = getRosterView({
          collectionResponse: getResponseBody(1, 1),
          collectionOptions: { parse: true },
        });
        executeSearch('Dan');
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
        expect(rosterView.$('.alert-information')).toContainText('No learners matched your criteria.');
        expect(rosterView.$('.alert-information')).toContainText('Try a different search.');
        expect(rosterView.$('.alert-information')).not.toContainText('Try clearing the filters.');
      });

      it('renders a "no results" view when there are no learners for the current filter', () => {
        const rosterView = getRosterView({
          collectionResponse: getResponseBody(1, 1),
          collectionOptions: { parse: true },
          courseMetadata: { cohorts: { 'Cohort A': 10 } },
        });
        $('select').val('Cohort A');
        $('select').change();
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
        expect(rosterView.$('.alert-information')).toContainText('No learners matched your criteria.');
        expect(rosterView.$('.alert-information')).toContainText('Try clearing the filters.');
        expect(rosterView.$('.alert-information')).not.toContainText('Try a different search.');
      });

      it('renders a "no results" view when there are no learners for the current search and filter', () => {
        const rosterView = getRosterView({
          collectionResponse: getResponseBody(1, 1),
          collectionOptions: { parse: true },
          courseMetadata: { cohorts: { 'Cohort A': 10 } },
        });
        executeSearch('Dan');
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(1, 1)));
        $('select').val('Cohort A');
        $('select').change();
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(0)));
        expect(rosterView.$('.alert-information')).toContainText('No learners matched your criteria.');
        expect(rosterView.$('.alert-information')).toContainText('Try clearing the filters.');
        expect(rosterView.$('.alert-information')).toContainText('Try a different search.');
      });
    });

    describe('accessibility', () => {
      it('the table has a <caption> element', () => {
        const rosterView = getRosterView({
          collectionResponse: getResponseBody(1, 1),
          collectionOptions: { parse: true },
        });
        expect(rosterView.$('table > caption')).toBeInDOM();
      });

      it('all <th> elements have scope attributes', () => {
        const rosterView = getRosterView({
          collectionResponse: getResponseBody(1, 1),
          collectionOptions: { parse: true },
        });
        rosterView.$('thead th').each((_index, $th) => {
          expect($th).toHaveAttr('scope', 'col');
        });

        rosterView.$('tbody th').each((_index, $th) => {
          expect($th).toHaveAttr('scope', 'row');
        });
      });

      it('all <th> elements have screen reader text', () => {
        const rosterView = getRosterView({
          collectionResponse: getResponseBody(1, 1),
          collectionOptions: { parse: true },
        });
        const screenReaderTextSelector = '.sr-sorting-text';
        const sortColumnSelector = 'th.username.sortable button';
        rosterView.$('thead th').each((_index, th) => {
          expect($(th).find(screenReaderTextSelector)).toHaveText('click to sort');
        });
        rosterView.$(sortColumnSelector).click();
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(2, 2)));
        expect(rosterView.$(sortColumnSelector).find(screenReaderTextSelector)).toHaveText('sort ascending');

        rosterView.$(sortColumnSelector).click();
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(2, 2)));
        expect(rosterView.$(sortColumnSelector).find(screenReaderTextSelector)).toHaveText('sort descending');
      });

      it('the search input has a label', () => {
        const rosterView = getRosterView();
        const searchContainer = rosterView.$('.learners-search-container');
        const inputId = searchContainer.find('input').attr('id');
        const $label = searchContainer.find('label');
        expect($label).toHaveAttr('for', inputId);
        expect($label).toHaveText('Search learners');
      });

      it('all icons should be aria-hidden', () => {
        const rosterView = getRosterView({
          collectionResponse: getResponseBody(1, 1),
          collectionOptions: { parse: true },
        });
        rosterView.$('i').each((_index, el) => {
          expect($(el)).toHaveAttr('aria-hidden', 'true');
        });
      });

      it('sets focus to the top of the table after taking a paging action', () => {
        const rosterView = getRosterView({
          collectionResponse: getResponseBody(2, 1),
          collectionOptions: { parse: true },
        });
        const firstPageLink = rosterView.$('.backgrid-paginator li a[title="Page 1"]');
        const secondPageLink = rosterView.$('.backgrid-paginator li a[title="Page 2"]');
        // It would be ideal to use jasmine-jquery's
        // expect(...).toBeFocused(), but that doesn't seem to
        // be working with jQuery's focus method.  A spy is
        // the next-best option.
        spyOn($.fn, 'focus');
        firstPageLink.click();
        // The first page link is disabled, and since we
        // haven't changed pages, it should receive focus.
        expect(firstPageLink.focus).toHaveBeenCalled();
        secondPageLink.click();
        // The second page link is not disabled, and after
        // clicking it, we should set focus to the top of the
        // table.
        getLastRequest().respond(200, {}, JSON.stringify(getResponseBody(2, 2)));
        expect($('#learner-app-focusable').focus).toHaveBeenCalled();
      });

      it('sets focus to the top after searching', () => {
        const searchString = 'search string';
        getRosterView();
        spyOn($.fn, 'focus');
        executeSearch(searchString);
        expect($('#learner-app-focusable').focus).toHaveBeenCalled();
      });

      it('does not violate the axe-core ruleset', (done) => {
        getRosterView({
          collectionResponse: getResponseBody(1, 1),
          collectionOptions: { parse: true },
        });
        axe.a11yCheck($('.roster-view-fixture')[0], (result) => {
          expect(result.violations.length).toBe(0);
          done();
        });
      });
    });
  });
});
