from typing import List


def write_to_file(name, data):

    """Writes a sequence of data to a file, with each item on a new line.
    Parameters:
    name (str): The name of the file to which data will be written.
    data (Iterable): A sequence of data items to be written to the file.
    """
    outF = open(name, "w", encoding="utf-8")

    for line in data:
        # write line to output file
        outF.write(str(line))
        outF.write("\n")
    outF.close()


def read_csv_list(path: str) -> List[str]:
    """read from a csv list to a python list

    Args
      path (str): path to find csv list

    Returns
      Python list from csv
    """
    with open(path, "r", encoding="latin-1") as fh:
        result = [line.rstrip() for line in fh]

    return result
