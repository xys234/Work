
TRANSIMS_node_def = [
    ('NODE'   , 'INTEGER', 1, 10),
    ('X_COORD', 'DOUBLE' , 2, 14.1, 'FEET'),
    ('Y_COORD', 'DOUBLE' , 3, 14.1, 'FEET'),
    ('Z_COORD', 'DOUBLE' , 4, 14.1, 'FEET'),
    ('NOTES'  , 'STRING' , 5, 128),
]

TRANSIMS_zone_def = [
    ('ZONE', 'INTEGER', 1, 10),
    ('X_COORD', 'DOUBLE', 2, 14.1, 'FEET'),
    ('Y_COORD', 'DOUBLE', 3, 14.1, 'FEET'),
    ('Z_COORD', 'DOUBLE', 4, 14.1, 'FEET'),
    ('NOTES', 'STRING', 5, 128),
]

TRANSIMS_link_def = [
    ('LINK',        'INTEGER',  1, 10),
    ('NAME',        'STRING',   2, 10),
    ('NODE_A',      'INTEGER',  3, 10),
    ('NODE_B',      'INTEGER',  4, 10),
    ('LENGTH',      'DOUBLE',   5, 10.1),
    ('SETBACK_A',   'DOUBLE',   6, 10.1),
    ('SETBACK_B',   'DOUBLE',   7, 10.1),
    ('BEARING_A',   'INTEGER',  8, 10),
    ('BEARING_B',   'INTEGER',  9, 10),
    ('TYPE',        'STRING',   10, 10),
    ('DIVIDED',     'UNSIGNED', 11, 10),
    ('AREA_TYPE',   'UNSIGNED', 12, 10),
    ('GRADE',       'DOUBLE',   13, 10),
    ('LANES_AB',    'UNSIGNED', 14, 10),
    ('SPEED_AB',    'DOUBLE',   15, 10.1),
    ('FSPD_AB',     'DOUBLE',   16, 10.1),
    ('CAP_AB',      'UNSIGNED', 17, 10),
    ('LANES_BA',    'UNSIGNED', 18, 10),
    ('SPEED_BA',    'DOUBLE',   19, 10.1),
    ('FSPD_BA',     'DOUBLE',   20, 10.1),
    ('CAP_BA',      'UNSIGNED', 21, 10),
    ('USE',         'STRING',   22, 10),
    ('NOTES',       'STRING',   23, 50)
]

TRANSIMS_shape_def = [
    ('LINK',    'INTEGER',  1, 10),
    ('POINTS',  'INTEGER',  2, 4, 'NEST_COUNT'),
    ('NOTES',   'STRING',   3, 128),
    ('X_COORD', 'DOUBLE',   1, 14.1, 'FEET', 'NESTED'),
    ('Y_COORD', 'DOUBLE',   2, 14.1, 'FEET', 'NESTED')
]

TRANSIMS_location_def = [

    ('LOCATION', 'INTEGER', 1, 10),
    ('LINK', 'INTEGER', 2, 10),
    ('DIR', 'INTEGER', 3, 1),
    ('OFFSET', 'DOUBLE', 4, 8.1, 'FEET'),
    ('SETBACK', 'DOUBLE', 5, 8.1, 'FEET'),
    ('ZONE', 'INTEGER', 6, 10),
    ('WEIGHT', 'DOUBLE', 7, 8.1)

]

TRANSIMS_parking_def = [

    ('PARKING', 'INTEGER', 1, 10),
    ('LINK', 'INTEGER', 2, 10),
    ('DIR', 'INTEGER', 3, 1),
    ('OFFSET', 'DOUBLE', 4, 8.1, 'FEET'),
    ('TYPE', 'STRING', 5, 10, 'PARKING_TYPE'),
    ('CAPACITY', 'INTEGER', 6, 6, 'VEHICLES'),
    ('COST', 'INTEGER', 7, 6, 'CENTS'),
    ('NUM_NEST', 'INTEGER', 8, 2, 'NEST_COUNT'),
    ('NOTES', 'STRING', 9, 128)
    # ('USE', 'STRING', 1, 128, 'USE_TYPE', 'NESTED'),
    # ('START', 'TIME', 2, 16, 'HOUR_CLOCK', 'NESTED'),
    # ('END', 'TIME', 3, 16, 'HOUR_CLOCK', 'NESTED'),
    # ('SPACE', 'UNSIGNED', 4, 5, 'VEHICLES', 'NESTED'),
    # ('TIME_IN', 'TIME', 5, 12, 'SECONDS', 'NESTED'),
    # ('TIME_OUT', 'TIME', 6, 12, 'SECONDS', 'NESTED'),
    # ('HOURLY', 'UNSIGNED', 7, 5, 'CENTS', 'NESTED'),
    # ('DAILY', 'UNSIGNED', 8, 5, 'CENTS', 'NESTED')
]

