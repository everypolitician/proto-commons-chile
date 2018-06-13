import re
from requests_html import HTMLSession


def get_table_rows(table):
    return [[cell.text for cell in row.find('td')] for row in table.find('tr')]


def get_region(panel):
    return panel.find('div.panel-heading')[0].text


def process_table(table):
    chamber = {}
    senate = {}
    core = {}

    rows = get_table_rows(table)
    chamber_start = rows.index(['', 'Distrito', 'Comunas'])
    senate_start = rows.index(['', 'Circunscripción senatorial', 'Comunas'])
    core_start = rows.index(['', 'Circunscripción provincial', 'Comunas'])

    chamber_rows = rows[chamber_start + 1:senate_start]
    senate_rows = rows[senate_start + 1:core_start]
    core_rows = rows[core_start + 1:]

    for row in chamber_rows:
        if row[0] == 'Elección Diputados' or row[0] == '':
            chamber.update({
                'Distrito {}'.format(row[1][:-1]): list_comunas(row[2])
            })
        else:
            chamber.update({
                'Distrito {}'.format(row[0][:-1]): list_comunas(row[1])
            })

    for row in senate_rows:
        if row[0] == 'Elección Senadores':
            senate.update({
                'Circunscripción {}'.format(row[1][:-1]): list_comunas(row[2])
            })
        else:
            senate.update({
                'Circunscripción {}'.format(row[0][:-1]): list_comunas(row[1])
            })

    for row in core_rows:
        if row[0] == 'Elección CORES':
            core.update({
                'Circunscripción {}'.format(row[1]): list_comunas(row[2])
            })
        else:
            core.update({
                'Circunscripción {}'.format(row[0]): list_comunas(row[1])
            })

    return chamber, senate, core


def get_districts(panel):
    table = panel.find('table', first=True)
    # return process_table_old(table)
    return process_table(table)


def list_comunas(comunas_str):
    comunas_str = re.sub('\s(y|e)\s', ' , ', comunas_str)

    subs = {u'.': u'',
            u'Antogasta': u'Antofagasta',
            u'Ollague': u'Ollagüe',
            u'Paihuano': u'Paiguano',
            u'Llay Llay': u'Llaillay',
            u'La Calera': u'Calera',
            u'Coínco': u'Coinco',
            u'Marchigue': u'Marchihue',
            u'Marchigüe': u'Marchihue',
            u'Perlarco': u'Pelarco',
            u'Los Alamos': u'Los Álamos',
            u'Los Angeles': u'Los Ángeles',
            u'Quillaco': u'Quilaco',
            u'Alto Bío Bío': u'Alto Biobío',
            u'Porteuelo': u'Portezuelo',
            u'Aisén': u'Aysén',
            u'Coihaique': u'Coyhaique',
            u'O’Higgins': u"O'Higgins",
            u'O´Higgins': u"O'Higgins",
            u'Río Ibañez': u'Río Ibáñez'}

    for old, new in subs.items():
        comunas_str = comunas_str.replace(old, new)

    comunas = [c.strip().title() for c in comunas_str.split(',')]
    return comunas


def create_comuna_to_district_lookup(districts_dict):
    comunas_lookup = {}
    for district, comunas in districts_dict.items():
        for comuna in comunas:
            comunas_lookup.update({comuna: district})
    return comunas_lookup


def get_comuna_lookup():
    session = HTMLSession()

    r = session.get('https://www.servel.cl/territorios-electorales/')

    panels = r.html.find('div.panel')

    chamber = {}
    senate = {}
    core = {}

    for panel in panels:
        cha, sen, cor = get_districts(panel)
        chamber.update(cha)
        senate.update(sen)
        core.update(cor)

    comuna_lookup = {
        'chamber': create_comuna_to_district_lookup(chamber),
        'senate': create_comuna_to_district_lookup(senate),
        'core': create_comuna_to_district_lookup(core)
    }
    return comuna_lookup
