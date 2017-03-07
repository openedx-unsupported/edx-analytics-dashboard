import requests
from bok_choy.promise import EmptyPromise
from bok_choy.web_app_test import WebAppTest
from selenium.webdriver.common.keys import Keys

from acceptance_tests import (
    ENABLE_COURSE_LIST_FILTERS,
    TEST_COURSE_ID,
)
from acceptance_tests.mixins import AnalyticsDashboardWebAppTestMixin
from acceptance_tests.pages import CourseIndexPage


_multiprocess_can_split_ = True


class CourseIndexTests(AnalyticsDashboardWebAppTestMixin, WebAppTest):
    test_skip_link_url = False

    def setUp(self):
        super(CourseIndexTests, self).setUp()
        self.page = CourseIndexPage(self.browser)
        self.maxDiff = None

    def test_page(self):
        super(CourseIndexTests, self).test_page()
        self._test_course_list()
        self._test_search()
        self._test_clear_input()
        self._test_clear_active_filter()
        self._test_clear_all_filters()
        if ENABLE_COURSE_LIST_FILTERS:
            self._test_filters()
        self._test_download_csv()

    def _test_course_list(self):
        """
        Course list should contain a link to the test course.
        """
        # text after the new line is only visible to screen readers
        columns = [
            'Course Name \nsort ascending',
            'Start Date \nclick to sort',
            'End Date \nclick to sort',
            'Total Enrollment \nclick to sort',
            'Current Enrollment \nclick to sort',
            'Change Last Week \nclick to sort',
            'Verified Enrollment \nclick to sort'
        ]
        self.assertTable('.course-list-table', columns)

        # Validate that we have a list of courses
        course_ids = self.page.q(css='.course-list .course-id')
        self.assertTrue(course_ids.present)

        # The element should list the test course id.
        self.assertIn(TEST_COURSE_ID, course_ids.text)

        # Validate the course links
        course_links = self.page.q(css='.course-list .course-name-cell a').attrs('href')

        for link, course_id in zip(course_links, course_ids):
            self.assertTrue(link.endswith(u'/courses/{}'.format(course_id.text)))

    def _test_search(self):
        """
        Tests that a user can perform a search to filter the course list.
        """
        # Search bar is present
        search_bar = self.page.q(css='#search-course-list')
        self.assertTrue(search_bar.present)

        # Clear any existing search first
        self.clear_all_filters()
        # Make sure all courses show before performing a search
        self.check_cleared()

        # Perform search
        search_input = self.driver.find_element_by_id('search-course-list')
        search_input.send_keys(Keys.CONTROL, 'a')  # in-case there is a previous search
        search_input.send_keys('search')
        # Check that clear icon shows up
        clear = self.page.q(css='button.clear')
        self.assertTrue(clear.present)
        search_input.send_keys(Keys.ENTER)

        # Search bar contains query
        search_input = self.page.q(css='#search-course-list')
        self.assertEqual(search_input.attrs('value'), ['search'])

        # Check that active filters show search value
        EmptyPromise(
            lambda: self.page.q(css='ul.active-filters').present,
            "Search performed"
        ).fulfill()
        active_filters = self.page.q(css='ul.active-filters')
        self.assertTrue(active_filters.present)
        search_active_filter = self.page.q(css='ul.active-filters li.filter-text_search')
        self.assertTrue('search' in search_active_filter.text[0])

        # No courses match search query, so alert should show
        course_ids = self.page.q(css='.course-list .course-id')
        self.assertFalse(course_ids.present)

        alert = self.page.q(css='.list-main .alert-information')
        self.assertTrue(alert.present)
        self.assertTrue('No courses matched your criteria' in alert.text[0])

    def _test_filter(self, filter_id, display_name, course_in_filter=False, clear_existing_filters=True):
        """
        Tests that a user can check a filter option to filter the course list.
        """
        # Filter is present
        filter_box = self.page.q(css='#' + filter_id)
        self.assertTrue(filter_box.present)

        if clear_existing_filters:
            # Clear any existing filter first
            self.clear_all_filters()
            # Make sure all courses show before performing a filter
            self.check_cleared()

        # Perform filter
        filter_box.click()

        # Check that active filters show search value
        EmptyPromise(
            lambda: self.page.q(css='ul.active-filters').present,
            "Search performed"
        ).fulfill()
        active_filters = self.page.q(css='ul.active-filters')
        self.assertTrue(active_filters.present)
        self.assertTrue(display_name in active_filters.text[0])

        course_ids = self.page.q(css='.course-list .course-id')
        num_results = self.page.q(css='.course-list .course-list-num-results .num-results')
        num_results_sr = self.page.q(css='.course-list .num-results-sr')
        if course_in_filter:
            self.assertTrue(course_ids.present)
            self.assertTrue('1' in num_results.text[0])
            self.assertTrue('1' in num_results_sr.text[0])
        else:
            # No courses match filter, so alert should show
            self.assertFalse(course_ids.present)
            alert = self.page.q(css='.list-main .alert-information')
            self.assertTrue(alert.present)
            self.assertTrue('No courses matched your criteria' in alert.text[0])
            self.assertTrue('0' in num_results.text[0])
            self.assertTrue('0' in num_results_sr.text[0])

    def clear_all_filters(self):
        # Check that the clear button is present. AKA a search/filter has been made.
        clear_all_filters = self.page.q(css='ul.active-filters button.action-clear-all-filters')
        if clear_all_filters.present:
            # Press clear search input
            clear_all_filters.first.click()

    def check_cleared(self):
        EmptyPromise(
            lambda: (self.driver.find_element_by_id('search-course-list').get_attribute('value') != 'search'),
            "Search input cleared"
        ).fulfill()

        # Search bar no longer contains query
        search_input = self.driver.find_element_by_id('search-course-list')
        self.assertNotEqual(search_input.get_attribute('value'), 'search')

        # Check that active filters are hidden
        EmptyPromise(
            lambda: not self.page.q(css='ul.active-filters').present,
            "Active filters hidden"
        ).fulfill()
        active_filters = self.page.q(css='ul.active-filters')
        self.assertFalse(active_filters.present)

        # Now that search is gone, the list should show with the test course
        EmptyPromise(
            lambda: (self.page.q(css='.course-list .course-id').present),
            "Table unfiltered"
        ).fulfill()
        course_ids = self.page.q(css='.course-list .course-id')
        self.assertTrue(course_ids.present)
        self.assertIn(TEST_COURSE_ID, course_ids.text)

    def _test_clear_input(self):
        """
        Tests that a user can clear the search filter to unfilter the results.
        """
        self._test_search()  # populate a search if it hasn't already

        # Check that clear icon shows up
        clear = self.page.q(css='button.clear')
        self.assertTrue(clear.present)

        # Press clear search input
        clear.first.click()

        self.check_cleared()

    def _test_clear_active_filter(self):
        """
        Tests that a user can clear the search filter to unfilter the results using active filters clear controls.
        """
        self._test_search()  # populate a search if it hasn't already

        search_active_filter = self.page.q(css='ul.active-filters li.filter-text_search button')

        # Press the active filter button (which should clear that filter)
        search_active_filter.first.click()

        self.check_cleared()

    def _test_clear_all_filters(self):
        """
        Tests that a user can clear the search filter to unfilter the results using clear all filters control.
        """
        self._test_search()  # populate a search if it hasn't already

        clear_all_filters = self.page.q(css='ul.active-filters button.action-clear-all-filters')

        # Press the "Clear" button link which should clear all filters including the search
        clear_all_filters.first.click()

        self.check_cleared()

    def _test_individual_filters(self):
        """
        Tests checking each option under each filter set.

        The test course will only be displayed under "Upcoming" or "self_paced" filters.
        """
        # maps id of filter in DOM to display name shown in active filters
        filters = {
            "Archived": "Archived",
            "Current": "Current",
            "Upcoming": "Upcoming",
            "unknown": "Unknown",
            "instructor_paced": "Instructor-Paced",
            "self_paced": "Self-Paced",
        }
        course_in_filters = ['Upcoming', 'self_paced']
        for filter_id, display_name in filters.items():
            self._test_filter(filter_id, display_name,
                              course_in_filter=(True if filter_id in course_in_filters else False))

    def _test_multiple_filters(self, filter_sequence):
        """
        Tests checking multiple filter options together and whether the course is shown after each filter application.

        filter_sequence should be a list of tuples where each element, by index, is:
            0. the filter id to apply
            1. the filter display name
            2. boolean for whether the test course is shown in the list after the filter is applied.
        """
        for index, filter_data in enumerate(filter_sequence):
            filter_id = filter_data[0]
            name = filter_data[1]
            course_shown = filter_data[2]
            first_filter = index == 0
            self._test_filter(filter_id, name, course_in_filter=course_shown, clear_existing_filters=first_filter)

    def _test_filters(self):
        self._test_individual_filters()

        # Filters ORed within a set
        self._test_multiple_filters([
            ('Archived', 'Archived', False),
            ('Upcoming', 'Upcoming', True),
            ('Current', 'Current', True),
            ('unknown', 'Unknown', True),
        ])

        # Filters ANDed between sets
        self._test_multiple_filters([
            ('Upcoming', 'Upcoming', True),
            ('instructor_paced', 'Instructor-Paced', False),
            ('self_paced', 'Self-Paced', True),
        ])

    def _test_download_csv(self):
        # Download button is present
        download_button = self.page.q(css='a.action-download-data')
        self.assertTrue(download_button.present)

        link = download_button.attrs('href')[0]

        # Steal the cookies from the logged-in firefox browser and use them in a python-initiated request
        kwargs = dict()
        session_id = [{i['name']: i['value']} for i in self.browser.get_cookies() if i['name'] == u'sessionid']
        if session_id:
            kwargs.update({
                'cookies': session_id[0]
            })
        response = requests.get(link, **kwargs)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['content-type'], 'text/csv')
