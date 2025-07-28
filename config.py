import yaml
from munch import munchify
config = munchify(yaml.load(open("./config.yaml"), Loader=yaml.FullLoader))