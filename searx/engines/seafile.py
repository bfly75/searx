# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 Seafile Pro using ElasticSearch
"""

from json import loads, dumps
from searx.exceptions import SearxEngineAPIException


base_url = 'http://localhost:9200'
username = ''
password = ''
index = ''
search_url = base_url + '/' + index + '/_search'
show_metadata = False
categories = ['general']


def init(engine_settings):
    if index == '':
        raise ValueError('index cannot be empty')


def request(query, params):
    if username and password:
        params['auth'] = (username, password)

    params['url'] = search_url
    params['method'] = 'GET'
    params['data'] = dumps(_simple_query_string_query(query))
    params['headers']['Content-Type'] = 'application/json'

    return params

   
def _simple_query_string_query(query):
    """
    Accepts query strings, but it is less strict than query_string
    The field used can be specified in index.query.default_field in Elasticsearch.
    REF: https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-simple-query-string-query.html
    """

    #TODO RC: evaluate query options
    return {'query': {'simple_query_string': {'query': query}}}


def response(resp):
    results = []

    resp_json = loads(resp.text)
    if 'error' in resp_json:
        raise SearxEngineAPIException(resp_json['error'])

    #TODO RC: improve results, key-value is not the prefered way of presenting.  
    for result in resp_json['hits']['hits']:
        r = {key: str(value) if not key.startswith('_') else value for key, value in result['_source'].items()}
        r['template'] = 'key-value.html'

        if show_metadata:
            r['metadata'] = {'index': result['_index'],
                             'id': result['_id'],
                             'score': result['_score']}

        results.append(r)

    return results
