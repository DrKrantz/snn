import argparse
import csv


def load_gdf(file):
    times = []
    neurons = []
    with open(file, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for row in reader:
            neurons.append(int(row[0]))
            times.append(float(row[1]))
    return neurons, times


parser = argparse.ArgumentParser()
parser.add_argument('file')
args = parser.parse_args()

neurons, times = load_gdf(args.file)
