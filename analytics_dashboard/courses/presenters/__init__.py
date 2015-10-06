import abc
import datetime
import logging
from urlparse import urljoin

from django.conf import settings
from django.core.cache import cache
from analyticsclient.client import Client
from common.clients import CourseStructureApiClient
from common.course_structure import CourseStructure
from core.utils import sanitize_cache_key

from courses.exceptions import BaseCourseError


logger = logging.getLogger(__name__)


class BasePresenter(object):
    """
    This is the base class for the pages and sets up the analytics client
    for the presenters to use to access the data API.
    """

    def __init__(self, course_id, timeout=10):
        self.client = Client(base_url=settings.DATA_API_URL,
                             auth_token=settings.DATA_API_AUTH_TOKEN,
                             timeout=timeout)
        self.course_id = course_id
        self.course = self.client.courses(self.course_id)

    def get_current_date(self):
        return datetime.datetime.utcnow().strftime(Client.DATE_FORMAT)

    @staticmethod
    def parse_api_date(s):
        """ Parse a string according to the API date format. """
        return datetime.datetime.strptime(s, Client.DATE_FORMAT).date()

    @staticmethod
    def parse_api_datetime(s):
        """ Parse a string according to the API datetime format. """
        return datetime.datetime.strptime(s, Client.DATETIME_FORMAT)

    @staticmethod
    def strip_time(s):
        return s[:-7]

    @staticmethod
    def sum_counts(data):
        return sum(datum['count'] for datum in data)


class CourseAPIPresenterMixin(object):
    """
    This mixin provides access to the course structure API and processes the hierarchy
    for sections, subsections, modules, and leaves (e.g. videos, problems, etc.).
    """
    __metaclass__ = abc.ABCMeta

    _last_updated = None

    def __init__(self, access_token, course_id, timeout=10):
        super(CourseAPIPresenterMixin, self).__init__(course_id, timeout)
        self.course_api_client = CourseStructureApiClient(settings.COURSE_API_URL, access_token)

    def _get_structure(self):
        """ Retrieves course structure from the course API. """
        key = self.get_cache_key('structure')
        structure = cache.get(key)

        if not structure:
            logger.debug('Retrieving structure for course: %s', self.course_id)
            structure = self.course_api_client.course_structures(self.course_id).get()
            cache.set(key, structure)

        return structure

    @abc.abstractproperty
    def section_type_template(self):
        """ Template for key generation to store/retrieve and cached structure data. E.g. "video_{}_{}" """
        pass

    @abc.abstractproperty
    def all_sections_key(self):
        """ Cache key for storing/retrieving structure for all sections. """
        pass

    @abc.abstractproperty
    def module_type(self):
        """ Module type to retrieve structure for. E.g. video, problem. """
        pass

    @property
    def module_graded_type(self):
        """
        Property used to filter modules by.  True/False will include only modules with
        that grade field.  Set to None if not filtering by the graded value.
        """
        return None

    def get_cache_key(self, name):
        """ Returns sanitized key for caching. """
        return sanitize_cache_key(u'{}_{}'.format(self.course_id, name))

    def course_structure(self, section_id=None, subsection_id=None):
        """
        Returns course structure from cache.  If structure isn't found, it is fetched from the
        course structure API.  If no arguments are provided, all sections and children are returned.
        If only section_id is provided, that section is returned.  If both section_id and
        subsection_id is provided, the structure for the subsection is returned.
        """
        if section_id is None and subsection_id is not None:
            raise ValueError('section_id must be specified if subsection_id is specified.')

        structure_type_key = self.get_cache_key(self.section_type_template.format(section_id, subsection_id))
        found_structure = cache.get(structure_type_key)

        if not found_structure:
            all_sections_key = self.get_cache_key(self.all_sections_key)
            found_structure = cache.get(all_sections_key)

            if not found_structure:
                structure = self._get_structure()
                found_structure = CourseStructure.course_structure_to_sections(structure, self.module_type,
                                                                               graded=self.module_graded_type)
                cache.set(all_sections_key, found_structure)

            for section in found_structure:
                self.add_child_data_to_parent_blocks(section['children'],
                                                     self.build_module_url_func(section['id']))
                self.attach_data_to_parents(section['children'],
                                            self.build_subsection_url_func(section['id']))
                section['num_modules'] = sum(child.get('num_modules', 0) for child in section['children'])

            self.attach_data_to_parents(found_structure, self.build_section_url)

            if found_structure:
                if section_id:
                    found_structure = [section for section in found_structure if section['id'] == section_id]

                    if found_structure and subsection_id:
                        found_structure = \
                            [section for section in found_structure[0]['children'] if section['id'] == subsection_id]

            cache.set(structure_type_key, found_structure)

        return found_structure

    def attach_data_to_parents(self, parents, url_func=None):
        """ Convenience method for adding aggregated data from children."""
        for index, parent in enumerate(parents):
            self.attach_aggregated_data_to_parent(index, parent, url_func)

    @abc.abstractmethod
    def attach_aggregated_data_to_parent(self, index, parent, url_func=None):
        """ Adds aggregate data from the child modules to the parent. """
        pass

    @abc.abstractproperty
    def default_block_data(self):
        """
        Returns a dictionary of default data for a block.  Typically, this would be the expected fields
        with empty/zero values.
        """
        pass

    @abc.abstractmethod
    def fetch_course_module_data(self):
        """
        Fetch course module data from the data API.  Use _course_module_data() for cached data.
        """
        pass

    @abc.abstractmethod
    def attach_computed_data(self, module_data):
        """
        Called by _course_module_data() to attach computed data (e.g. percentages, new IDs, etc.) to
        data returned from the analytics data api.
        """
        pass

    def _course_module_data(self):
        """ Retrieves course problems (from cache or course API) and calls process_module_data to attach data. """

        key = self.get_cache_key(self.module_type)
        module_data = cache.get(key)

        if not module_data:
            module_data = self.fetch_course_module_data()

            # Create a lookup table so that submission data can be quickly retrieved by downstream consumers.
            table = {}
            last_updated = datetime.datetime.min

            for datum in module_data:
                self.attach_computed_data(datum)
                table[datum['id']] = datum

                # Set the last_updated value
                created = datum.pop('created', None)
                if created:
                    created = self.parse_api_datetime(created)
                    last_updated = max(last_updated, created)

            if last_updated is not datetime.datetime.min:
                _key = self.get_cache_key('{}_last_updated'.format(self.module_type))
                cache.set(_key, last_updated)
                self._last_updated = last_updated

            module_data = table
            cache.set(key, module_data)

        return module_data

    def module_id_to_data_id(self, module):
        """ Translates the course structure module to the ID used by the analytics data API. """
        return module['id']

    def add_child_data_to_parent_blocks(self, parent_blocks, url_func=None):
        """ Attaches data from the analytics data API to the course structure modules. """
        try:
            module_data = self._course_module_data()
        except BaseCourseError as e:
            logger.warning(e)
            module_data = {}

        for parent_block in parent_blocks:
            parent_block['num_modules'] = len(parent_block['children'])
            for index, child in enumerate(parent_block['children']):
                data = module_data.get(self.module_id_to_data_id(child), self.default_block_data)

                # map empty names to None so that the UI catches them and displays as '(empty)'
                if len(child['name']) < 1:
                    child['name'] = None
                data['index'] = index + 1
                self.post_process_adding_data_to_blocks(data, parent_block, child, url_func)
                child.update(data)

    def post_process_adding_data_to_blocks(self, data, parent_block, child, url_func=None):
        """
        Override this if additional data is needed on the child block (e.g. problem part data).

        Arguments:
            data: Data for data API.
            parent_block: Parent of the child .
            child: Block that will be processed.
            url_func: URL generating function if needed to attach a URL to the child.
        """
        pass

    def build_section_url(self, _section):
        return None

    def build_subsection_url_func(self, _section_id):
        """
        Optionally override to return a function for creating the subsection URL.
        """
        return None

    def build_module_url_func(self, _section_id):
        """ Returns a function for generating a URL to the module (subsection child). """
        return None

    def sections(self):
        return self.course_structure()

    def section(self, section_id):
        section = None
        if section_id:
            section = self.course_structure(section_id)
            section = section[0] if section else None
        return section

    def subsections(self, section_id):
        sections = self.section(section_id)
        if sections:
            return sections.get('children', None)
        return None

    def subsection(self, section_id, subsection_id):
        subsection = None
        if section_id and subsection_id:
            subsection = self.course_structure(section_id, subsection_id)
            subsection = subsection[0] if subsection else None
        return subsection

    def subsection_children(self, section_id, subsection_id):
        """ Returns children (e.g. problems, videos) of a subsection. """
        subsections = self.subsection(section_id, subsection_id)
        if subsections:
            return subsections.get('children', None)
        return None

    def subsection_child(self, section_id, subsection_id, child_id):
        """ Return the specified child of a subsection (e.g. problem, video). """
        found_child = None
        children = self.subsection_children(section_id, subsection_id)
        if children:
            found_children = [child for child in children if child['id'] == child_id]
            found_child = found_children[0] if found_children else None
        return found_child

    def block(self, block_id):
        """ Retrieve a specific block (e.g. problem, video). """
        block = self._get_structure()['blocks'][block_id]
        block['name'] = block.get('display_name')
        return block

    def sibling_block(self, block_id, sibling_offset):
        """
        Returns a sibling block of the same type as the one denoted by
        `block_id`, where order is course ordering.  The sibling is chosen by
        `sibling_offset` which is the difference in index between the block and
        its requested sibling.  Returns `None` if no such sibling is found.
        Only siblings with data are returned.
        """
        sections = self.sections()
        siblings = [
            component
            for section in sections
            for subsection in section['children']
            for component in subsection['children']
            if component.get('url')  # Only consider siblings with data, hence with URLs
        ]
        try:
            block_index = (index for index, sibling in enumerate(siblings) if sibling['id'] == block_id).next()
            sibling_index = block_index + sibling_offset
            if sibling_index < 0:
                return None
            else:
                return siblings[sibling_index]
        except (StopIteration, IndexError):
            # StopIteration: requested video not found in the course structure
            # IndexError: No such video with the requested offset
            return None

    def next_block(self, block_id):
        """
        Get the next block in the course with the same block type as the block
        denoted by `block_id`.
        """
        return self.sibling_block(block_id, 1)

    def previous_block(self, block_id):
        """
        Get the previous block in the course with the same block type as the
        block denoted by `block_id`.
        """
        return self.sibling_block(block_id, -1)

    @abc.abstractmethod
    def blocks_have_data(self, blocks):
        """ Returns whether blocks contains any displayable data. """
        pass

    @property
    def last_updated(self):
        """ Returns when data was last updated according to the data api. """
        if not self._last_updated:
            key = self.get_cache_key('{}_last_updated'.format(self.module_type))
            self._last_updated = cache.get(key)

        return self._last_updated

    def build_view_live_url(self, base_url, module_id):
        """ Returns URL to view the module on the LMS. """
        view_live_url = None
        if base_url:
            view_live_url = u'{0}/{1}/jump_to/{2}'.format(base_url, self.course_id, module_id)
        return view_live_url

    def build_render_xblock_url(self, base_url, module_id):
        xblock_url = None
        if base_url:
            xblock_url = self._build_url(base_url, module_id)
        return xblock_url

    def _build_url(self, *args):
        """
        Removes trailing slashes from urls.  urllib.urljoin doesn't work because
        paths in our urls can include module IDs (e.g. i4x://edx/demo/video/12345ab2).
        """
        return '/'.join(str(arg).rstrip('/') for arg in args)
