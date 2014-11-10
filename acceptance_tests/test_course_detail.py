from bok_choy.web_app_test import WebAppTest

from acceptance_tests.mixins import CoursePageTestsMixin
from acceptance_tests.pages import CourseHomePage


_multiprocess_can_split_ = True


class CourseHomeTests(CoursePageTestsMixin, WebAppTest):
    def setUp(self):
        super(CourseHomeTests, self).setUp()
        self.page = CourseHomePage(self.browser)
        self.course = self.analytics_api_client.courses(self.page.course_id)

    def test_page(self):
        super(CourseHomeTests, self).test_page()
        self._test_table()

    def _test_data_update_message(self):
        # The course homepage does not display any data.
        pass

    def _view_to_href(self, view):
        return '/' + view.replace('_', '/').replace(':', '/%s/' % self.page.course_id) + '/'

    def _test_table(self):
        table_items = [
            {
                'name': 'Enrollment',
                'icon': 'fa-child',
                'heading': 'Who are my students?',
                'items': [
                    {
                        'title': 'How many students are in my course?',
                        'view': 'courses:enrollment_activity',
                        'breadcrumbs': ['Activity']
                    },
                    {
                        'title': 'How old are my students?',
                        'view': 'courses:enrollment_demographics_age',
                        'breadcrumbs': ['Demographics', 'Age']
                    },
                    {
                        'title': 'What level of education do my students have?',
                        'view': 'courses:enrollment_demographics_education',
                        'breadcrumbs': ['Demographics', 'Education']
                    },
                    {
                        'title': 'What is the student gender breakdown?',
                        'view': 'courses:enrollment_demographics_gender',
                        'breadcrumbs': ['Demographics', 'Gender']
                    },
                    {
                        'title': 'Where are my students?',
                        'view': 'courses:enrollment_geography',
                        'breadcrumbs': ['Geography']
                    },
                ],
            },
            {
                'name': 'Engagement',
                'icon': 'fa-bar-chart',
                'heading': 'What are students doing in my course?',
                'items': [
                    {
                        'title': 'How many students are interacting with my course?',
                        'view': 'courses:engagement_content',
                        'breadcrumbs': ['Content']
                    }
                ]
            }
        ]

        table_outer = self.page.browser.find_element_by_css_selector('.course-home-table-outer')

        headings = table_outer.find_elements_by_css_selector('header .heading')
        table_elements = table_outer.find_elements_by_css_selector('.course-home-table')

        for i, item in enumerate(table_items):
            # Check the headings
            self.assertEqual(headings[i].text, item['heading'])

            table = table_elements[i]

            # Check the name and icon
            name = table.find_element_by_css_selector('.name')
            self.assertEqual(name.text, item['name'])

            # If this element doesn't exist an exception will be thrown
            name.find_element_by_css_selector('i.ico.fa.%s' % item['icon'])

            # Retrieve the individual table rows
            rows = table.find_elements_by_css_selector('.item')
            for j, row in enumerate(item['items']):
                if j <= 0:
                    # First element is the name (checked above)
                    continue

                element = rows[j + 1]

                # Check the title and link
                title = element.find_element_by_css_selector('.title')
                self.assertEqual(title.text, row['title'])
                expected = self._view_to_href(row['view'])
                actual = title.find_element_by_css_selector('a').get_attribute('href')
                self.assertTrue(actual.endswith(expected))

                # Check the breadcrumbs
                breadcrumbs = element.find_element_by_css_selector('.breadcrumbs')
                breadcrumbs.find_element_by_css_selector('i.ico.fa.%s' % item['icon'])
                self.assertEqual(breadcrumbs.text, ' '.join(row['breadcrumbs']))
