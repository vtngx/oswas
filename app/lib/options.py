from optparse import OptionParser

class Options:

  def __init__(self):
    self._init_parser()
  
  def _init_parser(self):
    usage = 'bin/oswas'
    self.parser = OptionParser(usage=usage)

    self.parser.add_option(
      '-s', '--simple',
      action="store_true",
      default=False,
      dest='simple',
      help='simple mode'
    )

  def parse(self, args=None):
    return self.parser.parse_args(args)