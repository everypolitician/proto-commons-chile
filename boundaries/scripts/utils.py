# import pprint
import itertools
import difflib
# import re
from shapely.geometry import MultiPolygon  # Polygon,  LinearRing
# import shapely
from shapely.geometry import shape, mapping
from copy import deepcopy
# from shapely.geometry.polygon import orient
from shapely.ops import unary_union
import fiona
# import fiona.crs
# import fiona.transform
# import itertools
# from requests_html import HTMLSession


def add_name_of_district(feature, lookup_key, name_field, lookup,
                         name_of_lookup='your lookup table', suggestion=False):
    feature = deepcopy(feature)
    f_key = feature['properties'][lookup_key].title()
    try:
        feature['properties'].update(
            {name_field: lookup[f_key]}
        )
        # print('feature updated')
        return feature
    except KeyError as e:
        if suggestion:
            closest = difflib.get_close_matches(str(e), lookup.keys(), 1, 0.6)
            print('Failed to feature {} with value: {} in {}...'.format(
                  feature['id'], e, name_of_lookup),
                  ' Did you mean: {}'.format(closest))
        else:
            print('Failed to feature {} with value: {} in {}'.format(
                feature['id'], e, name_of_lookup))
        feature['properties'].update({name_field: 'UNKNOWN'})
        return feature
    # finally:
    #     if name_field in feature['properties'].items():
    #         return feature
    #     else:
    #         feature['properties'].update({name_field: 'UNKNOWN'})
    #         return feature


def dissolve_by_attribute(collection, attr, verbose=0, simplify=0):
    """
    Takes an open fiona collection of features and the name of an attribute.
    Returns a list of features dissolved based on common values of attr.
    """
    dissolved_features = []
    count = 0
    feat_sorted = sorted(collection,
                         key=lambda k: k['properties'][attr])
    for key, group in itertools.groupby(feat_sorted,
                                        key=lambda k: k['properties'][attr]):
        # attr_value = key

        group = list(group)
        group_attrs = deepcopy(group[0]['properties'])

        count += len(group)
        print('{} Features merged'.format(count))

        # This could be improved by only buffering invalid geoms.
        if simplify:
            geoms = [shape(f['geometry']).simplify(
                simplify, preserve_topology=True).buffer(0.0) for f in group]
        else:
            geoms = [shape(feature['geometry']) for feature in group]

        # clean_geoms = [zero_buffer(s) for s in geoms]
        if verbose:
            print('dissolving {} features into {}'.format(len(geoms), key))
        dissolved_geom = mapping(unary_union(geoms))
        if dissolved_geom['type'] == 'Polygon':
            dissolved_geom = mapping(MultiPolygon([shape(dissolved_geom)]))

        dissolved_feature = {'geometry': dissolved_geom,
                             # 'properties': {attr: attr_value}}
                             'properties': group_attrs}
        dissolved_features.append(dissolved_feature)

    return dissolved_features


def simplify_layer(src_path, out_path, tolerance):
    with fiona.open(src_path, 'r') as src:
        with fiona.open(out_path, 'w', **src.meta) as out:
            for f in src:
                geom = shape(f['geometry']).simplify(tolerance,
                                                     preserve_topology=True)
                f['geometry'] = mapping(geom)
                out.write(f)


def make_and_write_constituencies(dissolve_field, out_path, src, features):
    print('writing features to {}'.format(out_path))
    constituencies = dissolve_by_attribute(features, dissolve_field)
    out_schema = deepcopy(src.schema)
    out_schema['properties'].update({dissolve_field: 'str:100'})
    with fiona.open(out_path, 'w',
                    crs=src.crs,
                    encoding='UTF-8',
                    driver=src.driver,
                    schema=out_schema) as out:
        for f in constituencies:
            out.write(f)
