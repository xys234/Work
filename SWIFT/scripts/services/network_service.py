


def parse_origins(origin_file, zones=5263, logger=None):
    """
    Parse dynus-T origin file to get a dictionary of all origins
    :param origin_file: full path to the origin file
    :type  string
    :return:  zone -> [(from_node, to_node, weight)]
    :type: dict
    """

    origins = {}
    with open(origin_file, 'r') as dy_origin_file:
        total_num_origins = 0
        pos = 0
        zone = num_origins = -1
        for j, line in enumerate(dy_origin_file):
            record = line.strip().split()
            if j == 0 or j == pos:
                zone, num_origins = int(record[0]), int(record[1])
                pos = pos + num_origins + 1
            else:
                total_num_origins += 1
                from_node, to_node, weight = int(record[0]), int(record[1]), int(record[2])
                if zone not in origins:
                    origins[zone] = [(from_node, to_node, weight)]
                else:
                    origins[zone].append((from_node, to_node, weight))

    # Scan the origins to find the zones without origins
    zones_without_origin = []
    for i in range(zones):
        if i+1 not in origins:
            zones_without_origin.append(i+1)

    if zones_without_origin:
        logger.warning('{0:d} zones do not have origins: {1}'.format(len(zones_without_origin), zones_without_origin))
    logger.info("Number of Dynus-T Origin Records = {0:d}".format(total_num_origins))
    return origins