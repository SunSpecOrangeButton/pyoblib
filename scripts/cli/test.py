import sys
import os
import pprint

pprint.pprint(sys.path)
# sys.path.insert(0, os.path.abspath('../../'))
# print(sys.path)

from oblib import parser, taxonomy

taxonomy = taxonomy.Taxonomy()
p = parser.Parser(taxonomy)
print(p)
