"""
Script that produces min-max-avg for problem counts across all courses.
"""

from elasticsearch import Elasticsearch

es = Elasticsearch(retry_on_timeout=True)
index = 'course_reports_stage'

body = {
    'size': 1000,
    'query': {'match_all': {}},
    "fields": [
        "course_id",
        "num_problems"
    ],
    "script_fields": {
        "num_problems": {
            "script": "if (_source.assignment_types) { result=0; for (element in _source.assignment_types.results) { "
                      "result = result + element.problems.number_in_structure; }; result;} else { 0 }",
            "type": "number"
        }
    }
}
res = es.search(index=index, doc_type='course_performance', body=body)

num_courses = res['hits']['total']

print "Courses: %d" % num_courses

data = {}
for hit in res['hits']['hits']:
    fields = hit['fields']
    data[fields['course_id'][0]] = fields['num_problems'][0]

sum_counts = sum(data.values())

print 'Max: %d' % max(data.values())
print 'Avg: %d' % (sum_counts / num_courses)
print 'Min: %d' % min(data.values())
print 'Sum: %d' % sum_counts
