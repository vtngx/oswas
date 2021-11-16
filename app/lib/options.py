from optparse import OptionParser

class Options:

  def __init__(self):
    self._init_parser()
  
  def _init_parser(self):
    usage = 'bin/oswas'
    self.parser = OptionParser(usage=usage)

    self.parser.add_option(
      '-s', '--single',
      action="store_true",
      default=False,
      dest='single',
      help='single mode - crawl & scan only with 1 browser'
    )

  def parse(self, args=None):
    return self.parser.parse_args(args)