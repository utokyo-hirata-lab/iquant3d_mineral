
from iquant3d_mineral import *

iq3t_m = iq3t_m("plesovice")
#iq3t_m.execlusion(offset = 7, length = 39,nb_line = 91,washout = 10)
#iq3t_m.execlusion_quantum(offset = 7, length = 39,nb_line = 91,washout = 10)
#iq3t_m.print_ccf(std = "91Zr", threshold = 1000000)
iq3t_m.normalize(element = "232Th",base = "238U")
iq3t_m.normalize(element = "206Pb",base = "238U")
iq3t_m.normalize(element = "207Pb",base = "206Pb")
iq3t_m.normalize(element = "140Ce",base = "172Yb")
