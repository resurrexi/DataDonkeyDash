"""DLeeCious module."""
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


def quotify(item):
    """Wrap string in quotes.

    Args:
        item (str): string to wrap quotes in

    Returns:
        string: string with quotes wrapping it
    """
    return "'{}'".format(item)


def clausify(clause, tab=1):
    """Return a string as a SQL clause with tabs.

    Args:
        clause (str): string to clause
        tab (int): number of tabs to prefix [Default=1]

    Returns:
        string: claused string
    """
    return '\n' + tab * '    ' + clause


def PurrtySQL(code, linenos=False):
    """Purrtify SQL code.

    Args:
        code (str): piece of code to purrtify
        linenos (bool): boolean to insert line numbers [Default=False]

    Returns:
        string: formatted code
    """
    lexer = get_lexer_by_name('sql', stripall=True)
    formatter = HtmlFormatter(linenos=linenos, lineseparator="<br>", cssclass='hll')
    return highlight(code, lexer, formatter)


def PurrtyJSON(code, linenos=False):
    """Purrify JSON code.

    Args.
        code (str): piece of code to purrtify
        linenos (bool): boolean to insert line numbers [Default=False]

    Returns:
        string: formatted code
    """
    lexer = get_lexer_by_name('json', stripall=True)
    formatter = HtmlFormatter(linenos=linenos, lineseparator="<br>", cssclass='hll')
    return highlight(code, lexer, formatter)
