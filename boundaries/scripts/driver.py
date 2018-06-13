# import pprint
import fiona
import fiona.crs
import json

from chile import get_comuna_lookup
from copy import deepcopy
from utils import dissolve_by_attribute, add_name_of_district, make_and_write_constituencies


comuna_shp = '../source/comuna-source.shp'
chamber_shp = '../build/chamber-constituencies/chamber-constituencies.shp'
core_shp = '../build/regional-constituencies/regional-constituencies.shp'

comuna_lookup = get_comuna_lookup()
with open('../source/lookup.json', 'w') as outfile:
    json.dump(comuna_lookup, outfile, sort_keys=True, indent=2)


with fiona.open(comuna_shp, 'r') as src:
    print(len(src))
    chamber = []
    senate = []
    core = []
    for f in src:
        c = add_name_of_district(f, 'NOM_COMUNA',
                                 'chamb_con', comuna_lookup['chamber'],
                                 name_of_lookup='chamber', suggestion=True)
        s = add_name_of_district(f, 'NOM_COMUNA',
                                 'sen_con', comuna_lookup['chamber'],
                                 name_of_lookup='senate')
        cr = add_name_of_district(f, 'NOM_COMUNA',
                                  'reg_con', comuna_lookup['core'],
                                  name_of_lookup='core')

        chamber.append(c)
        senate.append(s)
        core.append(cr)

    # pprint.pprint([f['properties'] for f in chamber])
    print('Chamber has {} features'.format(len(chamber)))
    print('Core has {} features'.format(len(core)))

    make_and_write_constituencies(dissolve_field='chamb_con',
                                  out_path=chamber_shp,
                                  src=src, features=chamber)
    make_and_write_constituencies(dissolve_field='reg_con',
                                  out_path=core_shp,
                                  src=src, features=core)
