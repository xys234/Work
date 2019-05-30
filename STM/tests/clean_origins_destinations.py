"""

Remove origins and destinations on freeways


"""


import logging
import sys
from enum import IntEnum
from services.file_service import NetworkHeaderRecord, NetworkLinkRecord, NetworkNodeZoneRecord
from services.file_service import File

FORMATTER = logging.Formatter("%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(FORMATTER)
logger.addHandler(stream_handler)


class FacilityType(IntEnum):
    FREEWAY = 1
    FREEWAY_DETECTOR = 2
    ON_RAMP = 3
    OFF_RAMP = 4
    ARTERIAL = 5
    HOT = 6
    HIGHWAY = 7
    HOV = 8
    FREEWAY_HOT = 9
    FREEWAY_HOV = 10


def parse_origins(number_of_zones, origin_file):
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
        zone = -1
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
    for i in range(number_of_zones):
        if i + 1 not in origins:
            zones_without_origin.append(i + 1)

    if zones_without_origin:
        logger.warning(
            '{0:d} zones do not have origins: {1}'.format(len(zones_without_origin), zones_without_origin))
    logger.info("Number of Dynus-T Origin Records = {0:d}".format(total_num_origins))
    return origins


def write_origins(origins, origin_file):
    number_records = 0
    with open(origin_file, mode='w') as output_origin:
        for zone, orgs in origins.items():
            output_origin.write("{:8d} {:8d} {:1d}\n".format(zone, len(orgs), 0))
            for org in orgs:
                output_origin.write("{:8d} {:8d} {:1d}\n".format(*org))
                number_records += 1
                sys.stdout.write("\rNumber of Origin Records Written = {:,d}".format(number_records))
    sys.stdout.write("\n")
    logger.info("Number of Origin Records Written = {:,d}\n".format(number_records))


def read_network(network_file):
    """
    Read the link records

    :param network_file:
    :return:
    """
    link_records = File(name='links')

    with open(network_file, buffering=10_000_000, mode='r') as input_network:
        data = next(input_network)
        record = NetworkHeaderRecord()
        record.from_string(data.strip().split())
        number_of_zones, number_of_links, number_of_nodes = \
            record.number_of_zones, record.number_of_links, record.number_of_nodes

        logger.info("Input Network File -- %d Nodes, %d Zones, %d Links" %
                         (number_of_nodes, number_of_zones, number_of_links))

        number_of_nodes_read, number_of_links_read = 0, 0
        for line in input_network:
            line = line.strip().split()
            if number_of_nodes_read < number_of_nodes:
                # record = NetworkNodeZoneRecord()
                # record.from_string(line)
                number_of_nodes_read += 1

            elif number_of_nodes_read == number_of_nodes and number_of_links_read < number_of_links:
                record = NetworkLinkRecord()
                record.from_string(line)
                link_records.append(record)
                number_of_links_read += 1
                # sys.stdout.write("\rNumber of Link Records Read = {:,d}".format(number_of_links_read))

    # sys.stdout.write("\n")
    logger.info("Number of Link Records Read = {:,d}\n".format(number_of_links_read))
    return link_records


def check_origins(origins, link_records, external_zones):
    """
    Check origins against link records. Remove origins on freeways
    :param origins:
    :param link_records:
    :return:
    """
    invalid_ftypes = (
        FacilityType.FREEWAY, FacilityType.FREEWAY_DETECTOR, FacilityType.FREEWAY_HOT, FacilityType.FREEWAY_HOV,
        FacilityType.OFF_RAMP, FacilityType.ON_RAMP
    )
    indexed_links = {(link_record.Anode, link_record.Bnode): link_record for link_record in link_records}

    for zone, orgs in origins.items():
        if zone >= external_zones:
            continue
        number_origins = len(orgs)
        number_invalid_origins = 0
        invalid_origins = []

        for i, org in enumerate(orgs):
            from_node, to_node = org[0], org[1]
            ftype = indexed_links[(from_node, to_node)].ftype
            if ftype in invalid_ftypes:
                number_invalid_origins += 1
                invalid_origins.append(i)

        if number_invalid_origins == number_origins:
            logger.warning("{:d} Origins for Zone {:d} are ALL invalid".format(number_origins, zone))
            number_deletions = number_invalid_origins - 1
            orgs = [orgs[-1]]       # keep the last one

        else:
            number_deletions = number_invalid_origins
            orgs = [orgs[i] for i in range(len(orgs)) if i not in invalid_origins]
        if number_deletions > 0:
            print("{:d} Origins Removed for Zone {:d}".format(number_deletions, zone))
        origins[zone] = orgs
    return origins


if __name__ == '__main__':
    import os
    project_directory = r'L:\DCS\Projects\_Legacy\60563434_SWIFT\400_Technical\SWIFT_Workspace\Scenarios\Scenario_S2\STM\STM_A\01_DynusT\03_Model'
    network_file = os.path.join(project_directory, 'network.dat')
    origin_file = os.path.join(project_directory, 'origin.dat')
    new_origin_file = os.path.join(project_directory, 'origin_cleaned.dat')
    number_zones, external_zones = 5263, 5218

    origins = parse_origins(number_zones, origin_file)
    link_records = read_network(network_file)
    origins = check_origins(origins, link_records, external_zones)
    write_origins(origins, new_origin_file)



