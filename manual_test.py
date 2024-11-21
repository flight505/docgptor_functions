from src.docgpt import docgpt


@docgpt
def format_date(date):
    """Format the date as yyyy-mm-dd"""


# And just like that, you have a new python function:

format_date("December 9, 1992.")  # returns '1992-12-09'
format_date("On May the 4th 1979")  # returns '1979-05-04'
format_date("12/31/2008.")  # returns '2008-12-31'
