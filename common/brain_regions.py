from enum import Enum


class BRAINREGIONNAMES(Enum):
    Am = "amygdala"
    C = "cortex"
    BG = "basalganglia"
    BS = "brainstem"
    Me = "medullaoblongata"
    P = "pons"
    M = "midbrain"
    SCP = "superiorcerebellarpeduncle"
    WM = "whitematter"
    CC = "corpuscallosum"
    NC = "nucleuscaudatus"
    Pu = "putamen"
    Pa = "pallidum"
    CB = "cerebellum"
    cWM = "cerebellum1"
    cN = "cerebellum2"
    Th = "thalamus"
    Hi = "hippocampus"
    V = "ventricles"
    FC = "frontallobe"
    MC = "motorcortex"
    PL = "parietallobe"
    TL = "temporallobe"
    VC = "occipital"
    CL = "cingulate"
    CI = "cortexinsula"
    CR = "coronaradiata"

class NINEREGIONNUMBERS(Enum):
    Am = 18
    C = 3
    BG = 26
    BS = 16
    CR = 2
    CC = 251
    CB = 7
    M = 10
    Hi = 17

class BRAINREGIONNUMBERS(Enum):
    Am = 18
    C = 3
    BG = 26
    BS = 16
    Me = 175
    P = 174
    M = 173
    SCP = 178
    WM = 2
    CC = 251
    NC = 11
    Pu = 12
    Pa = 13
    CB = 7
    cWM = 7
    cN = 7
    Th = 10
    Hi = 17
    V = 4
    FC = 1028
    MC = 1024
    PL = 1029
    TL = 1030
    OL = 1011
    CL = 1026
    CI = 1035
