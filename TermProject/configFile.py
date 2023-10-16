import csv
import string
from enum import Enum
import sys
from operator import add
import datetime
import math
 
class PartitioningType(Enum):
    TERMBASED = 0
    DOCUMENTBASED = 1
