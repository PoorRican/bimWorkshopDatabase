from urllib.parse import urlparse


def strip_url(url: str) -> str:
    """ Strip URL down to the base URL

    Parameters:
        url: URL to strip

    Returns:
        URL with all paths, query parameters, fragments and path removed

    Examples:
        >>> strip_url('https://www.example.com/this/path/should/be/stripped?param1=1&param2=2#fragment')
        'https://www.example.com'

        No error is raised if the URL is already at the base:
        >>> strip_url('https://www.example.com')
        'https://www.example.com'
    """
    return (urlparse(url)
            ._replace(path='')
            ._replace(params='')
            ._replace(query='')
            ._replace(fragment='')
            .geturl())


def print_bar(text: str):
    length = len(text)
    bar = "=" * length

    print(bar)
    print(text)
    print(bar)
