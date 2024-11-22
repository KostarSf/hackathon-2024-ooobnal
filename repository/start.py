import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__)))

from Master_block.master import Master

if __name__ == '__main__':
    master = Master("engineer")