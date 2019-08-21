import sys

syspath = '/Users/winand.hulleman/Documents/trait-geo-diverse-angiosperms/script/python'

if syspath not in sys.path:
    sys.path += [syspath]

from predict_global_distribution import predict_global_distribution

def predict (path):
    predict_global_distribution(path)