# -*- coding: utf-8 -*-

import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

G10 = 10.0 ** (3.0/10.0)
G2 = 2.0

G = G10
b = 3.0

f1000 = 1000.0
fmid = {}
fmin = {}
fmax = {}

for i in range(-31, 14, 1):
    fmid[i] = (G ** (i / b)) * f1000
    fmax[i] = (G ** (1 / (2 * b))) * fmid[i]
    fmin[i] = (G ** (- 1 / (2 * b))) * fmid[i]

#    print "%s ; fmin: %s; fmid: %s; fmax: %s" % (x, fmin[x], fmid[x], fmax[x])

g_spec = [0, 1, 2, 3, 4, 4, 8, 16, 24, 32]
y_max_spec = [-75.0, -62.0, -42.5, -18, -2.3, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, -2.3, -18.0, -42.5, -62.0, -75.0]
y_min_spec = [None, None, None, None, -4.5, -4.5, -1.1, -0.4, -0.2, -0.15, -0.2, -0.4, -1.1, -4.5, -4.5, None, None, None, None]

x_norm = []

for i in range(0, 19):
    x_norm.append(None)
    
for i in range(0, 10):

    Q = G ** (g_spec[i] / 8.0)
    Qh = 1.0 + ((G ** (1 / (2.0 * b)) - 1.0) / (G ** (1 / 2.0) - 1.0 )) * (Q - 1.0)
    Ql = 1 / Qh
    
    x_norm[i + 9] = Qh
    x_norm[9 - i] = Ql
    
x = []
for i in range(0, 19):
    x.append(None)

fig, ax = plt.subplots()
ax.grid()

fs = 48000.0
Nqst = fs / 2.0

ORDER = 10

sos = {}

filter_names = ["0p8", "1", "12p5", "1p6", "2", "2p5", "3p15", "4", "5", "6p3", "8", "10", "12p5", "16", "20"]

output = "\n// FILTER COEFFICIENTS DESIGNED IN PYTHON\n\n"
output += "const int NB_FILTERS = 10;\n"
output += "const int NB_SOS = %s;\n\n" % (ORDER)

for i in range(-1, 14, 1):
    
    output += "const double SOS_%skHz[%s][6] = {\n" % (filter_names[i+1], ORDER)

    sos[i] = signal.butter(ORDER, [fmin[i] / Nqst, fmax[i] / Nqst], 'bandpass', False, output='sos') 
    
    for j in range(ORDER-1):
        output += "\t{%s, %s, %s, %s, %s, %s},\n" % (sos[i][j][0], sos[i][j][1], sos[i][j][2], sos[i][j][3], sos[i][j][4], sos[i][j][5])
    j = ORDER-1
    output += "\t{%s, %s, %s, %s, %s, %s}\n" % (sos[i][j][0], sos[i][j][1], sos[i][j][2], sos[i][j][3], sos[i][j][4], sos[i][j][5])
    output += "};\n"
    
    w, h = signal.sosfreqz(sos[i], worN=15000)
    db = 20*np.log10(np.abs(h))
    
    for j in range(0, 19):
        x[j] = (x_norm[j] * fmid[i])
    ax.semilogx(x, y_min_spec, 'r--', x, y_max_spec, 'r:', w/np.pi*Nqst, db)
#    ax.semilogx(x, y_min_spec, 'r--', x, y_max_spec, 'r:')
        
aliasing_sos = signal.butter(20, 0.1, 'low', False, output='sos') 
w, h = signal.sosfreqz(aliasing_sos, worN=15000)
db = 20*np.log10(np.abs(h))
ax.semilogx(w/np.pi*Nqst, db)

ORDER = len(aliasing_sos)

output += "const double SOS_ALIASING[%s][6] = {\n" % (ORDER)
for j in range(ORDER-1):
    output += "\t{%s, %s, %s, %s, %s, %s},\n" % (aliasing_sos[j][0], aliasing_sos[j][1], aliasing_sos[j][2], aliasing_sos[j][3], aliasing_sos[j][4], aliasing_sos[j][5])
j = ORDER-1
output += "\t{%s, %s, %s, %s, %s, %s}\n" % (aliasing_sos[j][0], aliasing_sos[j][1], aliasing_sos[j][2], aliasing_sos[j][3], aliasing_sos[j][4], aliasing_sos[j][5])
output += "};\n"
    
print(output)
