import csv
import os
import string
from to_transims.TRANSIMS_defs import *



def centroid(vertexes):
    _x_list = [vertex[0] for vertex in vertexes]
    _y_list = [vertex[1] for vertex in vertexes]
    _len = len(vertexes)
    _x = sum(_x_list) / _len
    _y = sum(_y_list) / _len
    return _x, _y


def get_zone_centroids(transims_zone_dict):
    """
    Compute the centroids for each zone
    :param transims_zone_dict: a dictionary mapping zone id to a list of vertices [(x1, y1, z1), (x2, y2, z2)]
    :return: a list of zone records [(zone, x_cen, y_cen, z_cen, notes)]
    """

    return [(zone, *(centroid(vertices)), 0, "") for zone, vertices in transims_zone_dict.items()]


def write_transims_file(data, filename, definitions):

    with open(filename+'.def', mode='w', newline='', encoding='UTF-8') as def_file:
        writer = csv.writer(def_file)
        writer.writerow(('TRANSIMS70', 'COMMA_DELIMITED', 1))
        for d in definitions:
            writer.writerow(d)

    with open(filename, mode='w', newline='', encoding='UTF-8') as csv_file:
        fieldnames = [f[0] for f in definitions]
        writer = csv.writer(csv_file)
        writer.writerow(fieldnames)
        for i in data:
            writer.writerow(i)


def parse_node_data(node_data):
    """
    Parse the string to extract node data
    :param node_data: a list of strings [6001, 2907994.095, 13839674.320]
    :return: (node, x, y, z, notes ) with 1 decimal place for x and y. "node" is integer
    """

    node = int(node_data[0])
    x, y = round(float(node_data[1]), 1), round(float(node_data[2]), 1)
    z = 0
    notes = ""
    return node, x, y, z, notes


def to_transims_node(infile):
    """
    Convert Dynus-T node file to a TRANSIMS node file
    :param file:
    :return:
    """

    nodes = []
    nodes_dict = {}
    node_count = 0
    with open(infile) as dfile:
        for line in dfile:
            node_count += 1
            node_data = line.strip().split()
            if node_data:
                node = parse_node_data(node_data)
                nodes.append(node)
                nodes_dict[node[0]] = node[1:]

    print('Number of Node Records Processed = {0:d}'.format(node_count))
    return nodes, nodes_dict


def process_link_shape(dynust_shape_file, transims_shape_file, transims_links_dict, definitions):
    """

    :param dynust_shape_file:
    :param transims_shape_file:
    :param transims_links_dict: (anode, bnode) to all link attributes
    :return:
    """

    with open(transims_shape_file+'.def', mode='w', newline='', encoding='UTF-8') as def_file:
        writer = csv.writer(def_file)
        writer.writerow(('TRANSIMS70', 'COMMA_DELIMITED', 2, 'NESTED'))
        for d in definitions:
            writer.writerow(d)

    with open(transims_shape_file, mode='w', newline='', encoding='UTF-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(("LINK", "POINTS", "NOTES"))
        writer.writerow(("X_COORD", "Y_COORD"))

        with open(dynust_shape_file, 'r') as dy_shape_file:
            for line in dy_shape_file:
                record = line.strip()
                translator = str.maketrans('', '', string.punctuation)
                record = record.translate(translator).split()
                link = transims_links_dict[(int(record[0]), int(record[1]))][0]
                num_shape_points = int(record[2])
                writer.writerow((link, num_shape_points))
                for i in range(num_shape_points):
                    writer.writerow((int(record[2*i+3]), int(record[2*i+4])))


def to_transims_locations(dynust_origin_file, transims_links_dict):
    """
    Convert origins.dat to TRANSIMS locations
    Assign 1 location to each origin link. The transims data tuple (Location, link, dir, offset, setback, zone, weight)

    :param dynust_origin_file:
    :param transims_links_dict: (anode, bnode) to all link attributes
    :return: a list of tuples for location attributes
    """

    transims_locations = []
    with open(dynust_origin_file, 'r') as dy_origin_file:
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
                link_attributes = transims_links_dict[(from_node, to_node)]
                link, length = link_attributes[0], link_attributes[4]
                offset = length / 2.0
                setback = 30
                transims_locations.append((total_num_origins, link, 0, offset, setback, zone, weight))
    print("Number of Dynus-T Origin Records = {0:d}".format(total_num_origins))
    return transims_locations


def to_transims_parking(transims_locations):
    """
    Create parking lots associated with each location
    :param transims_locations:
    :return:
    """

    transims_parking = []
    for loc in transims_locations:
        transims_parking.append((loc[0], loc[1], loc[2], loc[3], 'LOT', 0, 0, 0, 0, ""))
    return transims_parking


def to_transims_network(dynust_network_file, dynust_nodes_file, dynust_shape_file, dynust_origin_file,
                        out_node_file, out_zone_file, out_link_file, out_shape_file, out_location_file,
                        out_parking_file):
    """

    :param dynust_network_file:
    :param dynust_nodes_file:
    :param out_node_file:
    :param out_zone_file:
    :param out_link_file:
    :return:

    network.dat
    Row 1: number of zones, number of nodes, number of links, number of shortest paths, user super zones
    Node data: Node ID, Zone ID

    Link data:
    0-From_ID, 1-To_ID, 2- #Left-turn bays,
    3-# Right-turn bays, 4-Length (ft.), 5-# lanes,
    6-tfm, 7-speed adj factor, 8-spd limit,
    9-max service flow rate, 10-saturation service flor rate, 11-link type, 12-grade

    """

    type_equiv = {
        1: ('Freeway', 'Freeway'),
        2: ('Freeway', 'Freeway'),
        3: ('On-Ramp', 'Ramp'),
        4: ('Off-Ramp', 'Ramp'),
        5: ('Arterial', 'Major'),
        6: ('HOT', 'Freeway'),
        7: ('Highway', 'Expressway'),
        8: ('HOV', 'Freeway'),
        9: ('Freeway HOT', 'Freeway'),
        10: ('Freeway HOV', 'Freeway')
    }

    num_nodes = 0
    transims_zones_dict = {}
    transims_links = []
    transims_links_dict = {}

    # read in the node coordinates
    transims_nodes, transims_nodes_dict = to_transims_node(dynust_nodes_file)

    # Parse the Dynus-T network file
    with open(dynust_network_file, 'r') as dy_network_file:
        line_count = 0
        processed_zones = 0
        processed_links = 0

        for line in dy_network_file:
            line_count += 1
            record = line.strip().split()

            if line_count == 1:
                # Parse the network dimension
                assert len(record) == 5
                num_zones, num_nodes, num_links = int(record[0]), int(record[1]), int(record[2])
                assert num_nodes == len(transims_nodes)

            if 1 < line_count <= num_nodes + 1 and int(record[1]):
                # Parse zone data
                processed_zones += 1
                node, zone = int(record[0]), int(record[1])
                if int(zone) in transims_zones_dict:
                    transims_zones_dict[int(zone)].append(transims_nodes_dict[node])
                else:
                    transims_zones_dict[int(zone)] = [transims_nodes_dict[node]]

            if line_count > num_nodes + 1:
                # Parse link data
                processed_links += 1
                from_node, to_node = int(record[0]), int(record[1])
                name = ""
                length, lanes = float(record[4]), int(record[5])
                spd_adj, spd_limit = int(record[7]), int(record[8])
                serv_rate, sat_rate = int(record[9]), int(record[10])
                link_type, grade = int(record[11]), int(record[12])

                setback_a, setback_b = 30.0, 30.0
                bearing_a, bearing_b = 0, 0
                divided = 0
                area_type = 0
                cap_ab = serv_rate * lanes
                spd_ab = fspd_ab = spd_limit
                d_link_type, t_link_type = type_equiv[link_type][0], type_equiv[link_type][1]

                spd_ba = fspd_ba = cap_ba = lanes_ba = 0

                if d_link_type in ('HOV', 'HOT', 'Freeway HOT', 'Freeway HOV'):
                    use = 'HOV2+'
                else:
                    use = 'ANY'

                notes = ""

                link_record = (
                    processed_links,
                    name,
                    from_node,
                    to_node,
                    length,
                    setback_a,
                    setback_b,
                    bearing_a,
                    bearing_b,
                    t_link_type,
                    divided,
                    area_type,
                    grade,
                    lanes,
                    spd_ab,
                    fspd_ab,
                    cap_ab,
                    lanes_ba,
                    spd_ba,
                    fspd_ba,
                    cap_ba,
                    use,
                    notes
                )

                transims_links.append(link_record)
                transims_links_dict[(from_node, to_node)] = link_record

    transims_zones = get_zone_centroids(transims_zones_dict)
    transims_zones = sorted(transims_zones, key=lambda x: x[0])
    transims_locations = to_transims_locations(dynust_origin_file, transims_links_dict)
    transims_parkings = to_transims_parking(transims_locations)

    write_transims_file(data=transims_nodes, filename=out_node_file, definitions=TRANSIMS_node_def)
    write_transims_file(data=transims_zones, filename=out_zone_file, definitions=TRANSIMS_zone_def)
    write_transims_file(data=transims_links, filename=out_link_file, definitions=TRANSIMS_link_def)
    process_link_shape(dynust_shape_file, out_shape_file, transims_links_dict, TRANSIMS_shape_def)
    write_transims_file(data=transims_locations, filename=out_location_file, definitions=TRANSIMS_location_def)
    write_transims_file(data=transims_parkings, filename=out_parking_file, definitions=TRANSIMS_parking_def)

    print("Number of Dynus-T Zone Records = {0:d}".format(processed_zones))
    print("Number of Dynus-T Link Records = {0:d}".format(processed_links))


if __name__ == '__main__':

    dynust_folder = '..\data\Dynus_T'
    transims_folder = '..\data\TRANSIMS'
    DynusT_network_file = os.path.join(dynust_folder, 'network.dat')
    DynusT_node_xy_file = os.path.join(dynust_folder, 'xy.dat')
    DynusT_shape_file = os.path.join(dynust_folder, 'linkxy.dat')
    DynusT_origin_file = os.path.join(dynust_folder, 'origin.dat')
    TRANSIMS_node_file = os.path.join(transims_folder, 'Node.csv')
    TRANSIMS_zone_file = os.path.join(transims_folder, 'Zone.csv')
    TRANSIMS_link_file = os.path.join(transims_folder, 'Link.csv')
    TRANSIMS_shape_file = os.path.join(transims_folder, 'Shape.csv')
    TRANSIMS_location_file = os.path.join(transims_folder, 'Location.csv')
    TRANSIMS_parking_file = os.path.join(transims_folder, 'Parking.csv')
    to_transims_network(DynusT_network_file, DynusT_node_xy_file, DynusT_shape_file, DynusT_origin_file,
                        TRANSIMS_node_file, TRANSIMS_zone_file, TRANSIMS_link_file, TRANSIMS_shape_file,
                        TRANSIMS_location_file, TRANSIMS_parking_file)
