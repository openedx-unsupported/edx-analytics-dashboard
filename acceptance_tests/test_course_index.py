from bok_choy.promise import EmptyPromise
from bok_choy.web_app_test import WebAppTest
from selenium.webdriver.common.keys import Keys

from acceptance_tests import TEST_COURSE_ID
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

    def _test_course_list(self):
        """
        Course list should contain a link to the test course.
        """
        # text after the new line is only visible to screen readers
        columns = [
            'Course Name\nclick to sort',
            'Start Date\nclick to sort',
            'End Date\nclick to sort',
            'Total Enrollment\nclick to sort',
            'Current Enrollment\nsort descending',
            'Change Last Week\nclick to sort',
            'Verified Enrollment\nclick to sort'
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

        # Perform search
        search_input = self.driver.find_element_by_id('search-course-list')
        search_input.send_keys(Keys.CONTROL, 'a')  # in-case there is a previous search
        search_input.send_keys('search')
        # Check that clear icon shows up
        clear = self.page.q(css='button.clear')
        self.assertTrue(clear.present)
        search_input.send_keys(Keys.ENTER)

        # Search bar contains query
        self.assertEqual(search_input.get_attribute('value'), 'search')

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
        print alert.text[0]
        self.assertTrue('No courses matched your criteria' in alert.text[0])

    def check_cleared(self):
        EmptyPromise(
            lambda: (self.driver.find_element_by_id('search-course-list').get_attribute('value') != 'search'),
            "Search input cleared"
        ).fulfill()

        # Search bar no longer contains query
        search_input = self.driver.find_element_by_id('search-course-list')
        self.assertNotEqual(search_input.get_attribute('value'), 'search')

        # Now that search is gone, the list should show with the test course
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
