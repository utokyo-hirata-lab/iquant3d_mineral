
from iquant3d_mineral import *

iq3t_m = iq3t_m("plesovice")
#iq3t_m.execlusion(offset = 7, length = 39,nb_line = 91,washout = 10)
iq3t_m.print_ccf(std = "91Zr", threshold = 1000000)
