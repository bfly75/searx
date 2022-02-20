# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 Seafile Pro using ElasticSearch
"""

from json import loads, dumps
from searx.exceptions import SearxEngineAPIException
from datetime import datetime

base_url = 'http://localhost:9200'
index = 'repofiles'
search_url = f"{base_url}/{index}/_search"
result_url = 'https://localhost'
categories = ['general']


def init(engine_settings):
    if index == '':
        raise ValueError('index cannot be empty')


def request(query, params):
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

    # TODO RC: evaluate query options
    return {
        'query': {
            'simple_query_string': {
                'query': query,
                'fields': ['content', 'filename'],
                'default_operator': 'and'
            }
        }
    }


def response(resp):
    results = []

    resp_json = loads(resp.text)
    if 'error' in resp_json:
        raise SearxEngineAPIException(resp_json['error'])

    # TODO RC: improve results, key-value is not the prefered way of presenting.      
    for result in resp_json['hits']['hits']:
        # TODO RC: what to do with folders?
        if result['_type'] == "file":
            url = f"{result_url}/lib/{result['_id']}"
            title = result['_source']['filename']
            content = result['_source']['content']
            # According to /templates/simple/macros.html publishedDate is written as part of the subheader.
            #   {% if result.publishedDate %}<time class="published_date" datetime="{{ result.pubdate }}" >{{ result.publishedDate }}</time>{% endif %}
            # Not clear though what result.pubdate is for. The other engines use publishedDate.
            publishedDate = datetime.fromtimestamp(result['_source']['mtime'])
            metadata = {
                'score': result['_score'],
                'size': result['_source']['size']
            }
            # TODO RC: consider to make a new template, because metadata are not shown otherwise? Although not that import. Look at merging Default and Torrent.
            template = 'default.html'

            results.append( {
                'template': template, 
                'url': url, 
                'title': title, 
                'content': content, 
                'publishedDate': publishedDate,
                'metadata': metadata
            } )

    return results
