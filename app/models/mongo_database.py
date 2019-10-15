from __future__ import print_function
from mongoengine import connect
from .software import Software, QMFeatures, MMFeatures, create_software
from mongoengine.queryset.visitor import Q
import json
import re
import logging


'''
Search operators:
-----------------

a) Numbers:

Example: Libary.objects(name__ne='Python')
    ne: not equal to
    lt: less than
    lte: less than or equal to
    gt: greater than
    gte: greater than or equal to
    not: negate a standard check, may be used before other operators (e.g. Q(age__not__mod=5))
    in: value is in list (a list of values should be provided)
    nin: value is not in list (a list of values should be provided)
    mod: value % x == y, where x and y are two provided values
    all: every item in list of values provided is in array
    size: the size of the array is
    exists: value for field exists


b) Strings:

    exact: string field exactly matches value
    iexact: string field exactly matches value (case insensitive)
    contains: string field contains value
    icontains: string field contains value (case insensitive)
    startswith: string field starts with value
    istartswith: string field starts with value (case insensitive)
    endswith: string field ends with value
    iendswith: string field ends with value (case insensitive)
    match: performs an $elemMatch so you can match an entire document within an array


Query with:
Software.object(..) --> no exception, can return 0+, returns a queryset
Software.get(..) --> return exactly one, raises exception otherwise
                    (DoesNotExist, MultipleObjectsReturned)

queryset Functions:
.count()
.order_by('field_name')
.sum('field_name')


Create Objects:
---------------
Software.objects.insert(my_lib_object)
Software.objects.insert(  Software(**my_lib_json)  )

Multiple:
Software.objects.insert([mylib1, mylib2, mylib3])

my_Software.save()
my_Software.update(params)

Software.objects(..).delete()


json_list = Software.objects(..).to_json()
from_json??
'''

logger = logging.getLogger(__name__)


def get_connection(name='', host='localhost', port=27017, is_mock=False):
    """ Create MongoDB using mongoengine
        use is_mock to Create a mock empty DB for testing
    """
    if is_mock:
        # mock connection for testing
        return connect('mongoenginetest', host='mongomock://localhost')
    if name:
        return connect(name, host=host, port=port)

    return connect(host=host)


def clear_libraries():
    """Clear Libraries Collections"""
    Software.objects().delete()
    # db.drop_database('resources_website')


def load_collection_from_json(filename, lib_type=None):
    """Load DB from a Json file with list of JSON objects of libraries"""

    with open(filename) as f:
        json_list = json.load(f)

    for json_record in json_list:
        software = create_software(lib_type, **json_record)
        software.save(validate=False)

    # [Software(**json_record).save(validate=False) for json_record in json_list]

    # Software.objects.insert(software_list) # doesn't call override save


# ---------------------------   Query functions  ------------------------ #

def find_language(lang, verbose=False):
    results = Software.objects(languages_lower__in=lang.lower())
    if verbose:
        logger.debug('Num of results for {} is {}'.format(lang.lower(), results.count()))
        print_results(results)
    return results


def find_domain(domain, verbose=False):
    results = Software.objects(domain__in=domain)
    if verbose:
        print('Num of results for {} is {}'.format(domain, results.count()))
        print_results(results)

    return results


def search_description(keyword, verbose=False):
    """Search descrption """
    # TODO: fixme

    results = Software.objects(description__contains(keyword))
    if verbose:
        logger.debug('Num of results for {} is {}'.format(keyword, results.count()))
        print_results(results)

    return results


def search_text(query, verbose=False):
    """search indexed text fields (defined with $ in meta)"""
    results = Software.objects.search_text(query)

    if results:
        results = results.order_by('$text_score')

    if verbose:
        print_results(results)

    return results


def complex_query(languages=[], domains=[], verbose=False):
    languages_lower = [lang.lower() for lang in languages]
    results = Software.objects(Q(languages_lower__in=languages_lower) & Q(domain__in=domains))
    if verbose:
        print_results(results)

    return results


def full_search(exec_empty_sw=False, verbose=False, **kwargs):
    """Search the libraries collection using joint search of multiple fields
        any empty field will not be searched.
        if all fields are empty, then all documents are returned
        Note: fields must not be None
    """

    results = None
    query, qm_filters, mm_filters = {}, {}, {}
    arg_query = ()

    query_text = kwargs.pop('query_text', '')

    if kwargs.get('qm_filters'):
        qm_filters = json.loads(kwargs.pop('qm_filters', ''))
    if kwargs.get('mm_filters'):
        mm_filters = json.loads(kwargs.pop('mm_filters', ''))

    # ----------- MM filters ------------
    if 'qm_mm' in mm_filters:
        if mm_filters['qm_mm'] == 'Yes':
            query['mm_features__qm_mm__exists'] = True
        else:
            query['mm_features__qm_mm__exists'] = False

    if 'ensembles' in mm_filters:
        query['mm_features__ensembles'] = get_compiled_regex(mm_filters['ensembles'], sep='&')

    if 'file_formats' in mm_filters:
        query['mm_features__file_formats'] = get_compiled_regex(mm_filters['file_formats'], sep='|')

    if 'tags' in mm_filters:
        query['mm_features__tags__in'] = [tag.lower().replace(' ', '_') for tag in mm_filters['tags']]

    # ----------- QM filters ------------
    if 'basis' in qm_filters:
        query['qm_features__basis__icontains'] = qm_filters['basis']
    if 'element_coverage' in qm_filters:
        query['qm_features__element_coverage__icontains'] = qm_filters['element_coverage']
    if 'tags' in qm_filters:
        query['qm_features__tags__in'] = [tag.lower().replace(' ', '_') for tag in qm_filters['tags']]

    # ------------ other filters -----------
    languages = json.loads(kwargs.pop('languages', ''))
    if len(languages) != 0:
        query['languages_lower__in'] = [lang.lower() for lang in languages]

    price = kwargs.pop('price', '')
    if price == 'free':
        query['price__icontains'] = price
    elif price == 'non-free':
        query['price__nin'] = ['free']
        query['price__exists'] = True
    elif price == 'unknown':
        query['price__exists'] = False

    # add the rest of the keywords
    for key, val in kwargs.items():
        if val:
            query[key] = val

    if exec_empty_sw: # exclude empty sw
        # non_empty = {'$or': [{'description__ne': ''}, {'long_description__ne': ''}]}
        arg_query += (Q(description__ne='') | Q(long_description__ne=''),)

    # exclude pending sw
    query['is_pending'] = False

    logger.info('MongoDB Search query: %s', query)
    results = Software.objects(*arg_query, **query)

    logger.info('Results length: %s', len(results))

    # if len(languages_lower) != 0 and len(domain) != 0:
    #     results = Software.objects(Q(languages_lower__in=languages_lower) & Q(domain__in=domain))
    # elif len(languages_lower) != 0:
    #     results = Software.objects(languages_lower__in=languages_lower)
    # elif len(domain) != 0:
    #     results = Software.objects(domain__in=domain)
    # print(results)

    if len(query_text) != 0 and results:
        logger.debug('Sorting results by test_score')
        results = results.search_text(query_text)
        if results:
            results = results.order_by('$text_score')
    elif len(query_text) == 0 and results:
        logger.debug('Sorting results by name')
        results = results.order_by('software_name')
    else:
        logger.debug('No sorting!! len(query_text): ')

    if verbose:
        print_results(results)

    logger.info('Final results length: %s', len(results))

    return results


def get_compiled_regex(search_keys, sep='|'):
    """Returns a complied regular expression string
    from a query string of space-separated terms"""

    if isinstance(search_keys, str) or isinstance(search_keys, unicode):
        w_list = ['.*' + term + '.*' for term in search_keys.split()]
    elif isinstance(search_keys, list):
        w_list = ['.*' + term + '.*' for term in search_keys]
    else:
        w_list = []
    print('w_list: ', w_list)
    regex = re.compile(sep.join(w_list), re.IGNORECASE)

    return regex


def get_json(verbose=False):
    """Get json data of the DB"""

    json_data = Software.objects().to_json()
    if verbose:
        print(json_data)

    return json_data


def get_software(lib_id):
    libs = Software.objects(id=lib_id)
    if libs:    # return first result
        return libs[0]
    else:
        return None


def get_lib_features():
    """Get different values for Software properties values
        Used for search queries."""
    lib = {
        'mm_props': {},
        'qm_props': {}
    }
    lib['mm_props']['TAG_NAMES'] = MMFeatures.TAG_NAMES
    lib['mm_props']['FORCEFIELD_TYPES'] = MMFeatures.FORCEFIELD_TYPES
    lib['qm_props']['TAG_NAMES'] = QMFeatures.TAG_NAMES

    return lib

# ----------------------- Printing and Utils ------------------------- #


def add_one(name, description='', languages='', domain='', verbose=False):
    my_lib = Software(
        name=name,
        description=description,
        languages=languages,
        domain=domain
    )

    my_lib.save()
    if verbose:
        print('Added: ', my_lib)

    return my_lib


def print_results(results):
    """For testing"""
    if results:
        for res in results:
            print(res)
    print('........')


def print_all():
    """Print all Documents in the Libraries collection"""

    all_libs = Software.objects
    print('Currently in DB: ', all_libs.count())
    print_results(all_libs)


def get_DB_size():
    return Software.objects.count()
