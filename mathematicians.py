from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """

    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """log errors. be smart"""

    print(e)


def get_names():
    """Get names of mathematicians from url, list with strings of names, one per mathematician"""

    url = 'http://www.fabpedigree.com/james/mathmen.htm'
    response = simple_get(url)

    if response is not None:
        html = BeautifulSoup(response, 'html.parser')
        names = set()

        for li in html.select('li'):
            for name in li.text.split('\n'):
                if len(name) > 0:
                    names.add(name.strip())

        return list(names)

    # raise exception if we failed to extract any data
    raise Exception('Error. Failes to extract data from {} '.format(url))


def get_hits_on_name(name):
    """
    Accepts a 'name' of a mathematician and returns the number of hits that mathematician's
    Wikipedia page received in the past 60 days as an int.
    """
    # url_root is a template string that is used to build a URL.

    url_root = 'https://xtools.wmflabs.org/articleinfo/en.wikipedia.org/{}'
    response = simple_get(url_root.format(name))

    if response is not None:
        html = BeautifulSoup(response, 'html.parser')

        hit_link = [a for a in html.select('a')
                    if a['href'].find('latest-60') > -1]

        if len(hit_link) > 0:
            # Strip commas
            link_text = hit_link[0].text.replace(',', '')
            try:
                # convert to integer
                return int(link_text)
            except:
                log_error("couldn't parse {} as an 'int'".format(link_text))

    log_error('No pageviews found for {}'.format(name))
    return None

# Putting things together

if __name__ == '__main__':
    print('Getting list of names')
    names = get_names()
    print('..done.\n')

    results = []

    print('Getting stats for each name..')

    for name in names:
        try:
            hits = get_hits_on_name(name)
            if hits is None:
                hits = -1
            results.append((hits, name))

        except:
            results.append((-1, name))
            log_error('error encountered while processing '
                      '{}, skipping'.format(name))


    print('..done.\n')

    results.sort()
    results.reverse()

    if len(results) > 5:
        top_marks = results[:5]
    else:
        top_marks = results

    print('\nThe most popular mathematicians are:\n')
    for (mark, mathematician) in top_marks:
        print(' {} with {} pageviews'.format(mathematician, mark))

    no_results = len([res for res in results if res[0] == -1])
    print('\nBut we did not find results for {}'
          'mathematicians on the list'.format(no_results))
