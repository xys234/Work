### Copyright  RST International Inc., Bellevue, WA, USA. rst2 Thu 12/28/2017 08:58:58 ###
import sys, shutil
import numpy as np
import os
import random
import h5py
import math

ZONES = 5263

vod_folder = "Q:\\Houston8_DTA_Interim\\INPUTS\\2017\\"

AM = ["OD AM3HR HBNW Vehicles", "OD AM3HR HBW Vehicles", "OD AM3HR NHB Vehicles", "OD AM3HR Other VEHICLEs"]
MD = ["OD MD6HR HBNW Vehicles", "OD MD6HR HBW Vehicles", "OD MD6HR NHB Vehicles", "OD MD6HR Other VEHICLEs"]
PM = ["OD PM4HR HBNW Vehicles", "OD PM4HR HBW Vehicles", "OD PM4HR NHB Vehicles", "OD PM4HR Other VEHICLEs"]
OV = ["OD OV8HR HBNW Vehicles", "OD OV8HR HBW Vehicles", "OD OV8HR NHB Vehicles", "OD OV8HR Other VEHICLEs"]

PURP = ["hnw", "hbw", "nh", ""]
TOD = ["am", "md", "pm", "ov"]
TOD2 = ["AM3", "MD6", "PM4", "OV8"]

Tab = [["i12da", "i3da", "i45da", "i12a2", "ai3a2", "i45a2", "i12a3", "i3a3", "i45a3"],
       ["i1da", "i2da", "i3da", "i4da", "i5da", "i12a2", "ai3a2", "i45a2", "i12a3", "i3a3", "i45a3"],
       ["odai12", "odai3", "odai453", "os2i12", "os2i3", "os2i45", "os3i12", "os3i3", "os3i45", "wdai1", "wdai2",
        "wdai3", "wdai4", "wdai5", "ws2i12", "ws2i3", "ws2i45", "ws3i12", "ws3i3", "ws3i45"],
       ["Cargo", "Serv", "taxi", "exta"]
       ]

tod_24h = [0.0010, 0.0010, 0.0010, 0.0020, 0.0050, 0.0150, 0.0501, 0.1022, 0.0581, 0.0411, 0.0481, 0.0571, 0.0571,
           0.0521, 0.0651, 0.0982, 0.0852, 0.0832, 0.0651, 0.0451, 0.0301, 0.0220, 0.0100, 0.0050]

VOT = {"hbwi1da": 9.6, "hbwi2da": 15.04, "hbwi3da": 20.48, "hbwi4da": 27.52, "hbwi5da": 37.12, "hbwi12a2": 21.56,
       "hbwai3a2": 35.84, "hbwi45a2": 56.56, "hbwi12a3": 30.8, "hbwi3a3": 51.2, "hbwi45a3": 80.8,
       "hnwi12da": 7.03, "hnwi3da": 13.44, "hnwi45da": 23.65, "hnwi12a2": 12.3, "hnwai3a2": 23.52, "hnwi45a2": 41.39,
       "hnwi12a3": 17.57, "hnwi3a3": 33.6, "hnwi45a3": 59.12,
       "nhodai12": 7.03, "nhodai3": 13.44, "nhodai453": 23.65, "nhos2i12": 12.3, "nhos2i3": 23.52, "nhos2i45": 41.39,
       "nhos3i12": 17.57, "nhos3i3": 33.6, "nhos3i45": 59.12,
       "nhwdai1": 9.6, "nhwdai2": 15.04, "nhwdai3": 20.48, "nhwdai4": 27.52, "nhwdai5": 37.12, "nhws2i12": 21.56,
       "nhws2i3": 35.84, "nhws2i45": 56.56, "nhws3i12": 30.8, "nhws3i3": 51.2, "nhws3i45": 80.8,
       "Cargo": 64.0, "Serv": 40.0, "taxi": 18.94, "exta": 18.94}

ORIGIN = np.zeros((ZONES + 1, 200, 2), 'i')

YEAR = 2017

tmp_f1 = "vlist.tmp"
tmp_f2 = "dtime.tmp"


###
def startNI1(vid0):
    global VLIST, DTIME, tab

    # early AM
    VLIST = []
    DTIME = []

    PP = OV

    fac_tot = 0
    for i in range(19, 24):
        fac_tot += tod_24h[i]
    for i in range(0, 6):
        fac_tot += tod_24h[i]

    # TOT = np.zeros((ZONES,ZONES),'d')

    vot_keys = VOT.keys()

    TVEH = 0

    for h in range(0, 6):

        VLIST = []
        DTIME = []

        fac = tod_24h[h] / fac_tot

        print("NI1 Hour=" + str(h))

        # OD = np.zeros((ZONES,ZONES),'d')

        for f in PP:

            infile = vod_folder + f + ".omx"

            h5 = h5py.File(infile, 'r')

            tables = h5['/matrices/'].keys()

            vclass = 0
            vtype = 0
            purp = 0
            vot = 0
            k = 0

            for tab in tables:
                k += 1
                # if k>1:continue

                if tab.find("all") >= 0: continue
                print("NI1 Hour=" + str(h) + " Table=" + tab)

                if tab.find("da") >= 0:
                    vtype = 1
                elif tab.find("s2") >= 0 or tab.find("a2") >= 0:
                    vtype = 2
                elif tab.find("s3") >= 0 or tab.find("a3") >= 0:
                    vtype = 3
                elif tab.find("Cargo") >= 0:
                    vtype = 6
                elif tab.find("Serv") >= 0:
                    vtype = 5
                elif tab.find("taxi") >= 0:
                    vtype = 4
                elif tab.find("exta") >= 0:
                    vtype = 1

                if vtype == 1:
                    vclass = 0
                elif vtype == 2 or vtype == 3 or vtype == 4:
                    vclass = 2
                elif vtype == 5 or vtype == 6:
                    vclass = 1

                if tab.find("hbw") >= 0:
                    purp = 1
                elif tab.find("hnw") >= 0:
                    purp = 2
                elif tab.find("nhw") >= 0:
                    purp = 3
                elif tab.find("nho") >= 0:
                    purp = 4
                else:
                    purp = 5

                for key in vot_keys:
                    if tab.find(key) >= 0:
                        vot = VOT[key]
                        break

                OD = h5['/matrices/' + tab][:] * fac

                print(tab, np.sum(OD))

                # OD = TOT*fac

                # OD = OD.reshape(ZONES,ZONES)

                # fratar(OD,OD)
                vlist2(OD, h * 60, h * 60 + 59.9, purp, vot, vtype)

                del OD
                # del TOT

            h5.close()

        outf = "vehicle_hr" + str(h) + "_" + str(YEAR) + ".dat"

        ff = open(outf, 'w')
        tveh = output_vehicle(ff, vid0)
        ff.close()

        TVEH += tveh

    return TVEH


###
def startNI2(vid0):
    global VLIST, DTIME, tab

    PP = OV

    TVEH = 0

    fac_tot = 0
    for i in range(19, 24):
        fac_tot += tod_24h[i]
    for i in range(0, 6):
        fac_tot += tod_24h[i]

    vot_keys = VOT.keys()

    for h in range(19, 24):

        VLIST = []
        DTIME = []

        fac = tod_24h[h] / fac_tot

        print("NI1 Hour=" + str(h))

        for f in PP:

            infile = vod_folder + f + ".omx"

            h5 = h5py.File(infile, 'r')

            tables = h5['/matrices/'].keys()

            vclass = 0
            vtype = 0
            purp = 0
            vot = 0
            k = 0

            for tab in tables:
                k += 1
                # if k>1:continue

                if tab.find("all") >= 0: continue

                if tab.find("da") >= 0:
                    vtype = 1
                elif tab.find("s2") >= 0 or tab.find("a2") >= 0:
                    vtype = 2
                elif tab.find("s3") >= 0 or tab.find("a3") >= 0:
                    vtype = 3
                elif tab.find("Cargo") >= 0:
                    vtype = 6
                elif tab.find("Serv") >= 0:
                    vtype = 5
                elif tab.find("taxi") >= 0:
                    vtype = 4
                elif tab.find("exta") >= 0:
                    vtype = 1

                if vtype == 1:
                    vclass = 0
                elif vtype == 2 or vtype == 3 or vtype == 4:
                    vclass = 2
                elif vtype == 5 or vtype == 6:
                    vclass = 1

                if tab.find("hbw") >= 0:
                    purp = 1
                elif tab.find("hnw") >= 0:
                    purp = 2
                elif tab.find("nhw") >= 0:
                    purp = 3
                elif tab.find("nho") >= 0:
                    purp = 4
                else:
                    purp = 5

                for key in vot_keys:
                    if tab.find(key) >= 0: vot = VOT[key]

                OD = h5['/matrices/' + tab][:] * fac
                print(tab, np.sum(OD))

                # OD = TOT*fac

                vlist2(OD, h * 60, h * 60 + 59.9, purp, vot, vtype)

                del OD
                # del TOT

            h5.close()

        outf = "vehicle_hr" + str(h) + "_" + str(YEAR) + ".dat"

        ff = open(outf, 'w')
        tveh = output_vehicle(ff, vid0)
        ff.close()

        TVEH += tveh

    return TVEH


def startAM(vid0):
    global VLIST, DTIME, tab, ff1

    PP = AM

    fac_tot = 0
    for i in range(6, 9):
        fac_tot += tod_24h[i]

    vot_keys = VOT.keys()

    TVEH = 0

    for h in range(6, 9):

        # VLIST=[]
        # DTIME=[]

        ff1 = open(tmp_f1, 'w')
        # f2 = open(tmp_f2,'w')

        fac = tod_24h[h] / fac_tot

        print("AM Hour=" + str(h))

        for f in PP:

            infile = vod_folder + f + ".omx"

            h5 = h5py.File(infile, 'r')

            tables = h5['/matrices/'].keys()

            vclass = 0
            vtype = 0
            purp = 0
            vot = 0
            k = 0

            for tab in tables:
                k += 1
                # if k>1:continue

                if tab.find("all") >= 0: continue

                if tab.find("da") >= 0:
                    vtype = 1
                elif tab.find("s2") >= 0 or tab.find("a2") >= 0:
                    vtype = 2
                elif tab.find("s3") >= 0 or tab.find("a3") >= 0:
                    vtype = 3
                elif tab.find("Cargo") >= 0:
                    vtype = 6
                elif tab.find("Serv") >= 0:
                    vtype = 5
                elif tab.find("taxi") >= 0:
                    vtype = 4
                elif tab.find("exta") >= 0:
                    vtype = 1

                if vtype == 1:
                    vclass = 0
                elif vtype == 2 or vtype == 3 or vtype == 4:
                    vclass = 2
                elif vtype == 5 or vtype == 6:
                    vclass = 1

                if tab.find("hbw") >= 0:
                    purp = 1
                elif tab.find("hnw") >= 0:
                    purp = 2
                elif tab.find("nhw") >= 0:
                    purp = 3
                elif tab.find("nho") >= 0:
                    purp = 4
                else:
                    purp = 5

                for key in vot_keys:
                    if tab.find(key) >= 0: vot = VOT[key]

                OD = h5['/matrices/' + tab][:] * fac

                print(tab, np.sum(OD))

                # OD = TOT*fac

                vlist2(OD, h * 60, h * 60 + 59.9, purp, vot, vtype)

                del OD
                # del TOT

            h5.close()
            del tables

        ff1.close()

        outf = "vehicle_hr" + str(h) + "_" + str(YEAR) + ".dat"

        ff = open(outf, 'w')
        tveh = output_vehicle(ff, vid0)
        ff.close()

        TVEH += tveh

        ###
    return TVEH
    ###


def startMD(vid0):
    global VLIST, DTIME, tab

    PP = MD

    VLIST = []
    DTIME = []

    fac_tot = 0
    for i in range(9, 15):
        fac_tot += tod_24h[i]

    vot_keys = VOT.keys()

    TVEH = 0

    for h in range(12, 15):

        VLIST = []
        DTIME = []

        fac = tod_24h[h] / fac_tot

        print("MD Hour=" + str(h))

        for f in PP:

            infile = vod_folder + f + ".omx"

            h5 = h5py.File(infile, 'r')

            tables = h5['/matrices/'].keys()

            vclass = 0
            vtype = 0
            purp = 0
            vot = 0
            k = 0

            for tab in tables:
                k += 1
                # if k>1:continue

                if tab.find("all") >= 0: continue

                if tab.find("da") >= 0:
                    vtype = 1
                elif tab.find("s2") >= 0 or tab.find("a2") >= 0:
                    vtype = 2
                elif tab.find("s3") >= 0 or tab.find("a3") >= 0:
                    vtype = 3
                elif tab.find("Cargo") >= 0:
                    vtype = 6
                elif tab.find("Serv") >= 0:
                    vtype = 5
                elif tab.find("taxi") >= 0:
                    vtype = 4
                elif tab.find("exta") >= 0:
                    vtype = 1

                if vtype == 1:
                    vclass = 0
                elif vtype == 2 or vtype == 3 or vtype == 4:
                    vclass = 2
                elif vtype == 5 or vtype == 6:
                    vclass = 1

                if tab.find("hbw") >= 0:
                    purp = 1
                elif tab.find("hnw") >= 0:
                    purp = 2
                elif tab.find("nhw") >= 0:
                    purp = 3
                elif tab.find("nho") >= 0:
                    purp = 4
                else:
                    purp = 5

                for key in vot_keys:
                    if tab.find(key) >= 0: vot = VOT[key]

                OD = h5['/matrices/' + tab][:] * fac

                print(tab, np.sum(OD))

                # OD = TOT*fac

                vlist2(OD, h * 60, h * 60 + 59.9, purp, vot, vtype)

                del OD
                # del TOT

            h5.close()

        outf = "vehicle_hr" + str(h) + "_" + str(YEAR) + ".dat"

        ff = open(outf, 'w')
        tveh = output_vehicle(ff, vid0)
        ff.close()

        TVEH += tveh
        ###
    return TVEH


def startPM(vid0):
    global VLIST, DTIME, tab

    PP = PM

    VLIST = []
    DTIME = []

    fac_tot = 0
    for i in range(15, 19):
        fac_tot += tod_24h[i]

    vot_keys = VOT.keys()

    TVEH = 0

    for h in range(15, 19):

        VLIST = []
        DTIME = []

        fac = tod_24h[h] / fac_tot

        print("PM Hour=" + str(h))

        for f in PP:

            infile = vod_folder + f + ".omx"

            h5 = h5py.File(infile, 'r')

            tables = h5['/matrices/'].keys()

            vclass = 0
            vtype = 0
            purp = 0
            vot = 0
            k = 0

            for tab in tables:
                k += 1
                # if k>1:continue

                if tab.find("all") >= 0: continue

                if tab.find("da") >= 0:
                    vtype = 1
                elif tab.find("s2") >= 0 or tab.find("a2") >= 0:
                    vtype = 2
                elif tab.find("s3") >= 0 or tab.find("a3") >= 0:
                    vtype = 3
                elif tab.find("Cargo") >= 0:
                    vtype = 6
                elif tab.find("Serv") >= 0:
                    vtype = 5
                elif tab.find("taxi") >= 0:
                    vtype = 4
                elif tab.find("exta") >= 0:
                    vtype = 1

                if vtype == 1:
                    vclass = 0
                elif vtype == 2 or vtype == 3 or vtype == 4:
                    vclass = 2
                elif vtype == 5 or vtype == 6:
                    vclass = 1

                if tab.find("hbw") >= 0:
                    purp = 1
                elif tab.find("hnw") >= 0:
                    purp = 2
                elif tab.find("nhw") >= 0:
                    purp = 3
                elif tab.find("nho") >= 0:
                    purp = 4
                else:
                    purp = 5

                for key in vot_keys:
                    if tab.find(key) >= 0: vot = VOT[key]

                OD = h5['/matrices/' + tab][:] * fac

                print(tab, np.sum(OD))

                # OD = TOT*fac

                vlist2(OD, h * 60, h * 60 + 59.9, purp, vot, vtype)

                del OD
                # del TOT

            h5.close()

        outf = "vehicle_hr" + str(h) + "_" + str(YEAR) + ".dat"

        ff = open(outf, 'w')
        tveh = output_vehicle(ff, vid0)
        ff.close()

        TVEH += tveh

    return TVEH


###
def vlist(T, ST1, ST2, PURP, VOT, VT):
    global VLIST, DTIME

    tot = int(np.sum(T) + 0.5)

    T2 = T

    # for r in range(ZONES):
    # for c in range(ZONES):
    # T2[r,c] = round(T[r,c],4)

    print("Tot-0=", tot, np.sum(T2))

    rowtot = 0
    coltot = 0

    for i in range(1, ZONES + 1):
        rowtot += np.sum(T2[i - 1, :])
        coltot += np.sum(T2[:, i - 1])
        print(i, np.sum(T2[i - 1, :]), np.sum(T2[:, i - 1]))

    print(rowtot, coltot)
    return 0

    T2 = T.reshape(ZONES, ZONES)

    sum0 = 0
    sum1 = 0

    for i in range(1, ZONES + 1):

        if sum0 >= tot: break

        t0 = np.sum(T2[i - 1, :])

        sum1 += int(t0 + 0.5)

        if t0 <= 0: continue

        X = []
        Y = []

        for j in range(1, ZONES + 1):
            if T2[i - 1, j - 1] <= 0: continue

            # if T2[i-1,j-1]>1:print i,j,T2[i-1,j-1]

            X.append(0 - T2[i - 1, j - 1])
            Y.append(j)
        X2 = np.argsort(X)

        orig = i

        sum = 0
        for j in range(len(X2)):  # 1,ZONES+1):

            if sum0 >= tot: break

            if sum >= t0: break

            idx = X2[j]

            dest = Y[idx]

            v = max(1, int(abs(X[idx]) + 0.5))  # T2[orig-1,dest-1])))

            # print "O=",orig,"D=",dest,v
            for jj in range(int(v)):
                link1 = random.randint(1, ORIGIN[orig, 0, 0])
                dtime = float(random.randint(int(ST1 * 10), int(ST2 * 10))) / 10
                ipos = float(random.randint(1, 10000)) / 10000

                s = '%d %d %d %d %d %.1f %.4f %.2f' % (orig, dest, link1, VT, PURP, dtime, ipos, VOT)
                VLIST.append(s)
                DTIME.append(dtime)

                sum0 += 1
                sum += 1

                if sum >= t0: break

        del X, Y, X2

    del T2

    return


###

def output_vehicle(f1, vid0):
    global VLIST, DTIME

    # if len(DTIME)==0: return 0

    f = open(tmp_f1, 'r')
    VLIST = f.readlines()
    f.close()

    for s in VLIST:
        v = s.split(',')
        DTIME.append(float(v[5]))

    # A = np.array(DTIME)
    # X = np.argsort(A)
    X = np.argsort(DTIME)

    tveh = len(X)
    vid = 0

    s = '%12d           1    # of vehicles in the file, Max # of STOPs\n' % (tveh)
    f1.write(s)

    s = "        #   usec   dsec   stime vehcls vehtype ioc #ONode #IntDe info ribf    comp   izone Evac InitPos    VoT  tFlag pArrTime TP IniGas\n"
    f1.write(s)

    print("Total Vehicles=", tveh)

    nettotal = 0
    for i in range(tveh):

        # if i%1000==0:
        #     print("Prepare vehicle.dat",int(float(i)/float(tveh)*100+1))
        try:

            j = X[i]
            vid = vid0 + i + 1

            s = VLIST[j].split()

            orig = int(s[0])
            dest = int(s[1])
            link1 = int(s[2])
            vtype = int(s[3])
            purp = int(s[4])

            dtime = float(s[5])

            ipos = float(s[6])
            vot = float(s[7])

            anode = ORIGIN[orig, link1, 0]
            bnode = ORIGIN[orig, link1, 1]

            s = '%9d%7d%7d%8.1f%6d%6d%6d%6d%6d%6d%8.4f%8.4f%6d%6d%12.8f%8.2f%5d%7.1f%5d%5.1f\n' % (
            vid, anode, bnode, dtime, 3, vtype, 0, 0, 1, 0, 0.2, 0, orig, 0, ipos, vot, 0, 0, purp, 0)
            f1.write(s)

            s1 = '%12d%7.2f\n' % (dest, 0)
            f1.write(s1)

            nettotal += 1
        except:
            print("Error=", i, j, s)

    del X, VLIST, DTIME
    return vid


###
###
def vlist2(T, ST1, ST2, PURP, VOT, VT):
    global VLIST, DTIME, tab, ff1

    tot = int(np.sum(T) + 0.5)

    print("Total Input=", tot)

    rowtot = 0
    coltot = 0

    for i in range(1, ZONES + 1):
        rowtot += np.sum(T[i - 1, :])
        coltot += np.sum(T[:, i - 1])
        # print "TAZ=",i, "RowSum=",np.sum(T[i-1,:]), "ColSum=",np.sum(T[:,i-1])

    print("TotRowSum=", rowtot, "TotColSum=", coltot)

    T2 = np.zeros((ZONES, ZONES), 'i')

    sum0 = 0
    sum1 = 0

    i = -1

    # U.Progress("DTIME="+str(ST1),"Purpose="+str(PURP),0)

    while i < ZONES - 1:

        i += 1

        # if i%100==0:U.Status(tab+"  Time="+str(ST1)+" Zone="+str(i))
        # if i%100==0:U.Progress("DTIME="+str(ST1),"Purpose="+str(PURP),int(float(i)/float(ZONES)*100)+1)

        if np.sum(T[i, :]) <= 0: continue

        j = -1

        residual = 0

        while j < ZONES - 1:

            j += 1

            if T[i, j] == 0: continue

            v = round(T[i, j] + residual)

            residual = (T[i, j] + residual) - v

            T2[i, j] = v
            '''
            for j2 in range(j+1,ZONES): 

                if T[i,j2] <=0: continue
                else:
                    T[i,j2] = T[i,j2] + residual
                    j = j2-1
                    break
            '''

    tot2 = int(np.sum(T2))

    if tot2 > 0 and tot2 != tot:
        x = []
        y = []

        for i in range(ZONES):
            if T2[i, i] > 0:
                x.append(0 - T2[i, i])
                y.append(i)
        x2 = np.argsort(x)

        # if len(x2)==0:pass

        gap = tot2 - tot

        if gap > 0:
            for j in range(gap):
                if j >= ZONES: continue

                try:
                    k = y[x2[j]]
                    T2[k, k] = max(0, T2[k, k] - 1)
                except:
                    continue
        else:

            for j in range(abs(gap)):
                if j >= ZONES: continue

                if len(x2) > 0 and j < len(x2):
                    try:
                        k = y[x2[j]]
                    except:
                        continue
                else:
                    k = j

                T2[k, k] = max(0, T2[k, k] + 1)

        del x, y, x2

    print("Total Output=", np.sum(T2))

    ###
    for i in range(ZONES):
        orig = i + 1
        if np.sum(T2[i, :]) == 0: continue
        for j in range(ZONES):
            dest = j + 1
            if T2[i, j] == 0: continue
            for k in range(int(T2[i, j])):
                link1 = random.randint(1, ORIGIN[orig, 0, 0])
                dtime = float(random.randint(int(ST1 * 10), int(ST2 * 10))) / 10
                ipos = float(random.randint(1, 10000)) / 10000

                s = '%d %d %d %d %d %.1f %.4f %.2f\n' % (orig, dest, link1, VT, PURP, dtime, ipos, VOT)
                # VLIST.append(s)
                # DTIME.append(dtime)
                ff1.write(s)

    del T2

    return


###
def origins():
    inf = r"..\data\origin.dat"

    f = open(inf, 'r')
    data = f.readlines()
    f.close()

    n = len(data)

    k = 0

    while (k < n):
        s = data[k].split()
        k += 1

        zon = int(s[0])
        x = int(s[1])

        ORIGIN[zon, 0, 0] = x

        for i in range(x):
            s = data[k].split()
            a = int(s[0])
            b = int(s[1])
            j = i + 1

            try:
                ORIGIN[zon, j, 0] = a
                ORIGIN[zon, j, 1] = b
            except:
                print(zon, i, a)

            k += 1

    return


###


###
if __name__ == '__main__':
    origins()

    tveh2 = startAM(0)
    print("AM=", tveh2)

    # tveh1 = startNI1(0)
    # print("NI1=", tveh1)

    #
    # tveh3 = startMD(0)
    # print("MD=", tveh3)
    #
    # tveh4 = startPM(0)
    # print("PM=", tveh4)
    #
    # tveh5 = startNI2(0)
    # print("NI2=", tveh5)

    del ORIGIN

    ###
