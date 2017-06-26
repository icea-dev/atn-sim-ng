# ------------------------------------------------------------------------------+
# solve the inverse Vincenty's formulae
# https://en.wikipedia.org/wiki/Vincenty%27s_formulae
# ------------------------------------------------------------------------------+

#--- IMPORT DEPENDENCIES ------------------------------------------------------+

from __future__ import division

import math

# --- MAIN ---------------------------------------------------------------------+

def vincenty(coord1, coord2, maxIter=200, tol=10**-12):

    #--- CONSTANTS ------------------------------------+
    
    a = 6378137.0              # radius at equator in meters (WGS-84)
    f = 1 / 298.257223563      # flattening of the ellipsoid (WGS-84)
    b = (1 - f) * a

    phi_1, L_1, = coord1       # coordinate pair #1
    phi_2, L_2, = coord2       # coordinate pair #2

    U_1 = math.atan((1 - f) * math.tan(math.radians(phi_1)))
    U_2 = math.atan((1 - f) * math.tan(math.radians(phi_2)))

    L = math.radians(L_2 - L_1)

    Lambda = L                 # set initial value of lambda to L

    sinU1 = math.sin(U_1)
    cosU1 = math.cos(U_1)
    sinU2 = math.sin(U_2)
    cosU2 = math.cos(U_2)

    #--- BEGIN ITERATIONS -----------------------------+
    iters = 0

    for i in xrange(maxIter):
        iters += 1
        
        cosLambda = math.cos(Lambda)
        sinLambda = math.sin(Lambda)
        sinSigma = math.sqrt((cosU2 * math.sin(Lambda)) ** 2 + (cosU1 * sinU2 - sinU1 * cosU2 * cosLambda) ** 2)
        cosSigma = sinU1 * sinU2 + cosU1 * cosU2 * cosLambda
        sigma = math.atan2(sinSigma, cosSigma)

        sin_alpha = (cosU1 * cosU2 * sinLambda) / sinSigma
        cosSq_alpha = 1 - sin_alpha ** 2
        cos2Sig_m = cosSigma - ((2 * sinU1 * sinU2) / cosSq_alpha)

        C = (f / 16) * cosSq_alpha * (4 + f * (4 -3 * cosSq_alpha))

        Lambda_prev = Lambda
        Lambda = L + (1 - C) * f * sin_alpha * (sigma + C * sinSigma * (cos2Sig_m + C * cosSigma * (-1 + 2 * cos2Sig_m ** 2)))

        # successful convergence
        diff = abs(Lambda_prev - Lambda)
        if diff <= tol:
            break
        
    uSq = cosSq_alpha * ((a ** 2 - b ** 2) / b ** 2)
    A = 1 + (uSq / 16384) * (4096 + uSq * (-768 + uSq * (320 - 175 * uSq)))
    B = (uSq / 1024) * (256 + uSq * (-128 + uSq * (74 - 47 * uSq)))
    deltaSig = B * sinSigma * (cos2Sig_m + 0.25 * B * (cosSigma * (-1 + 2 * cos2Sig_m ** 2) - (1 / 6) * B * cos2Sig_m * (-3 + 4 * sinSigma ** 2) * (-3 + 4 *cos2Sig_m ** 2)))

    # output distance in meters     
    return b * A * (sigma - deltaSig)
    