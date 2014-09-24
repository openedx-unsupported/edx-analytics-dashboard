#! /usr/bin/env python

"""
This script generates a report containing the following details for each course:
 * HTTP status codes for every course page in Insights
 * Boolean indicating if the API has activity and enrollment data for the course

A live feed of the report can be tail'ed from <TIMESTAMP>-course_report.log. The final output CSV is available
in the file <TIMESTAMP>-course_report.csv. <TIMESTAMP> is the time, in UTC, at which this script was initialized.

To execute this script run the following command from the parent directory of acceptance_tests:

    $ python -m acceptance_tests.course_validation.generate_report
"""

import csv
import datetime
import logging
import time
from multiprocessing import Queue, Pool

import requests
from analyticsclient.client import Client

from acceptance_tests.course_validation import API_SERVER_URL, API_AUTH_TOKEN, DASHBOARD_SERVER_URL
from acceptance_tests.course_validation.course_reporter import CourseReporter, API_REPORT_KEYS, COURSE_PAGES


timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')
logging.basicConfig(filename='{}-course_report.log'.format(timestamp), format='%(levelname)s: %(message)s',
                    level=logging.INFO)

# Hide requests logs
logging.getLogger("requests").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

NUM_PROCESSES = 4

# TODO: Pull courses from LMS or elsewhere
COURSES = ["aaa/bbb/ccc", "ak/akSState/1T2014", "andya/AA101/2014_T1", "AndyA/AATC/1", "ANUx/ANU-ASTRO1x/1T2014",
           "ANUx/ANU-ASTRO2x/2T2014", "ANUx/ANU-ASTRO3x/4T2014", "ANUx/ANU-INDIA1x/1T2014", "arbi/cs205/1T2014",
           "BerkeleyX/APCS-A.1x/3T2015", "BerkeleyX/APCS-A.2x/3T2015", "BerkeleyX/APCS-A.3x/1T2016",
           "BerkeleyX/APCS-A.4x/1T2016", "BerkeleyX/BJC.1x/3T2015", "BerkeleyX/BJC.2x/3T2015",
           "BerkeleyX/BJC.3x/1T2016", "BerkeleyX/BJC.4x/1T2016", "BerkeleyX/ColWri.2.2x/1T2015",
           "BerkeleyX/ColWri2.1x/3T2013", "BerkeleyX/ColWri2.2x/1T2014", "BerkeleyX/ColWri2.3x/1T2014",
           "BerkeleyX/ColWri2.3x_2/1T2015", "BerkeleyX/ColWri_2.1x/3T2014", "BerkeleyX/CS-169.1x/2013_Summer",
           "BerkeleyX/CS-169.2x/2013_Summer", "BerkeleyX/CS-184.1x/2013_October",
           "BerkeleyX/CS-184x/Foundations_of_Computer_Graphics", "BerkeleyX/CS-191x/2013_August",
           "BerkeleyX/CS-CS169.1x/3T2014", "BerkeleyX/CS-CS169.2x/1T2015", "BerkeleyX/CS.169.2x/3T2013",
           "BerkeleyX/CS.CS169.1x/3T2013", "BerkeleyX/CS169.1/2013_Spring_SPOC_Binghamton",
           "BerkeleyX/CS169.1/2013_Spring_SPOC_HPU", "BerkeleyX/CS169.1/2013_Spring_SPOC_Mills",
           "BerkeleyX/CS169.1/2013_Spring_SPOC_UCCS", "BerkeleyX/CS169.1/2013_Spring_SPOC_UIowa",
           "BerkeleyX/CS169.1/2013_Spring_SPOC_UNCC", "BerkeleyX/CS169.1x/2012_Fall",
           "BerkeleyX/CS169.1x/2013_March", "BerkeleyX/CS169.1x/2013_Spring", "BerkeleyX/CS169.1X/3T2013",
           "BerkeleyX/CS169.2x/2012_Fall", "BerkeleyX/CS169.2x/2013_Spring",
           "BerkeleyX/CS169.2x/Software_as_a_Service", "BerkeleyX/CS169/fa12", "BerkeleyX/CS184.1x/2012_Fall",
           "BerkeleyX/CS184.1x/2013_Spring", "BerkeleyX/CS188.1x/2012_Fall", "BerkeleyX/CS188.1x/2013_Spring",
           "BerkeleyX/CS188/fa12", "BerkeleyX/CS188/sp13", "BerkeleyX/CS191x/2013_Spring",
           "BerkeleyX/CS_184.1x/3T2014", "BerkeleyX/CS_CS169.1x/1T2014", "BerkeleyX/CS_CS169.2x/1T2014",
           "BerkeleyX/EE40LX/1T2015", "BerkeleyX/EECS149.1x/2T2014", "BerkeleyX/GG101x/1T2014",
           "BerkeleyX/LUCS.1x/3T2015", "BerkeleyX/LUCS.2x/3T2015", "BerkeleyX/LUCS.3x/1T2016",
           "BerkeleyX/LUCS.4x/1T2016", "BerkeleyX/Stat2.1X/1T2014", "BerkeleyX/Stat2.1x/2013_Spring",
           "BerkeleyX/Stat2.2x/2013_April", "BerkeleyX/Stat2.3x/2013_SOND", "BerkeleyX/Stat_2.1x/1T2014",
           "BerkeleyX/Stat_2.2x/1T2014", "BerkeleyX/Stat_2.3...x/2T2014", "BerkeleyX/Stat_2.3..x/2T2014",
           "BerkeleyX/Stat_2.3.x/2T2014", "BerkeleyX/Stat_2.3x/2T2014", "BerkeleyX/Stats2.2x/1T2014",
           "BerkleeX/BCM-MB110x/1T2014", "BerkleeX/BMPR365x/2T2014", "BerkleeX/MB110x/3T2014",
           "bhwX/1.001x/Brian_s_Test_Course", "BUx/ARPO222x/3T2014", "BUx/ASTR105x/3T2014", "BUx/INTL301x/3T2014",
           "BUx/Math226.1x/1T2015", "BUx/PY1x/1T2015", "BUx/PYAP1x/1T2015", "BUx/SABR101x/2T2014",
           "CaltechX/Ay1001x/2T2014", "CaltechX/BEM1105x/1T2015", "CaltechX/CS1156x/Fall2013",
           "CaltechX/CS156/Fall2013", "CaltechX/CS_1156x/3T2014", "CaltechX/Ec1011x/1T2014",
           "CarrTest/Test101/2014_T1", "ColumbiaX/HIST1.1x/3T2014", "ColumbiaX/HIST1.2x/3T2014",
           "ColumbiaX/HIST1.3x/1T2015", "CooperUnion/APChem.1x/1T2015", "CooperUnion/APCSA.1x/1T2015",
           "CooperUnion/Chem.1x/1T2015", "CooperUnion/Chem.2x/1T2015", "CooperUnion/CS.1x/1T2015",
           "CooperUnion/CS.2x/1T2015", "CornellX/Astro2290x/1T2014", "CornellX/ENGRI1210x/1T2015",
           "CornellX/ENGRI1280x/1T2014", "CornellX/ENVSCI1500x/1T2015", "CornellX/HIST1514x/1T2014",
           "CornellX/HIST1514x_Fall2014/3T2014", "CornellX/INFO2040x/1T2014", "DartmouthX/DART.ENVS.01.X/2015_T1",
           "DavidsonX/001x/1T2014", "DavidsonX/D.001x/3T2014", "DavidsonX/D002/2014_T3", "DavidsonX/D003x.1/1T2015",
           "DavidsonX/D003x.2/2T2015", "DelftX/AE.1110x/3T2014", "DelftX/AE1110x/1T2014", "DelftX/Calc001x/2T2015",
           "DelftX/CTB3300WCx/2T2014", "DelftX/CTB3365DWx/3T2014", "DelftX/CTB3365STx/2T2015",
           "DelftX/CTB3365x/2013_Fall", "DelftX/DDA691x/3T2014", "DelftX/ET.3034TU/3T2014",
           "DelftX/ET3034TUx/2013_Fall", "DelftX/FP101x/3T2014", "DelftX/NGI101x/1T2014", "DelftX/NGI102x/3T2014",
           "DelftX/RI101x/3T2014", "DelftX/TBP01x/3T2014", "DelftX/TPM1x/3T2014", "DelftX/TW3421x/1T2014",
           "e0dX/10/e0dCourse", "edx/1/2014", "edX/1234/Teppo_Test", "edX/123x/Teppo_s_test_course",
           "edX/127/Humanities_Demo", "edX/1986/Krister_Test_Course", "edx/4.605/3T2013",
           "edx/4.605test/3t2013test", "edX/CHANG100/Mark_s_Test_Course", "edx/cp-test/Cale_s_Test_Course",
           "edX/CT101/2013_08_29", "edX/DemoX.1/2014", "edX/DemoX/Demo_Course", "edX/GWPx/2014_T1",
           "edX/JJ101x/2014_T3", "edX/LG101x/2015_T1", "edX/lyla_test/lyla_test", "EdX/NAA101/2014",
           "edX/Open_DemoX/edx_demo_course", "edX/STEVE101/2014_FOREVER", "edX/Test/3T2013",
           "edX/victor101/Victor_s_test_course", "edX_Learning_Sciences/XPhysics/2013_Winter",
           "EPFLx/BIO465.1x/4T2014", "EPFLx/BIO465x/2013_OND", "EPFLx/EE-100Bx/3T2014", "EPFLx/EE-102Bx/1T2014",
           "EPFLx/MF201x/1T2014", "EPFLx/PHYS-209x/4T2014", "ETHx/AMRx/1T2014", "ETHx/CAMSx/3T2014",
           "ETHx/FC-01x/3T2014", "GeorgetownX/GUIX-501-01/3T2014", "GeorgetownX/GUIX-501-01x/3T2014",
           "GeorgetownX/HUMX421-01x/3T2014", "GeorgetownX/HUMX422-01x/1T2015", "GeorgetownX/HUMX423-01x/1T2015",
           "GeorgetownX/INFX523-01/2013_Fall", "GeorgetownX/INFX523-02x/3T2014", "GeorgetownX/MEDX202-01/2014_SOND",
           "GeorgetownX/phlx101-01/1T2014", "GeorgetownX/PHYX152x/1T2015", "HamiltonX/RELST005.5x/1T2015",
           "HarvardX/1368.1x/3T2014", "HarvardX/1368.2x/2T2015", "HarvardX/1368.3x/2T2015",
           "HarvardX/1368.4x/2T2015", "HarvardX/AI12.1x./2014_T3", "HarvardX/AI12.1x/2013_SOND",
           "HarvardX/AI12.2x/2013_SOND", "HarvardX/AmPoX.1/2014_T3", "HarvardX/AmPoX.2/2014_T3",
           "HarvardX/AT1x/2T2014", "HarvardX/BUS5.1x/1T2014", "HarvardX/BUS5.1x_Application-Only/1T2014",
           "HarvardX/CB22.1x/2013_SOND", "HarvardX/CB22.2x/3T2014", "HarvardX/CB22x/2013_Spring",
           "HarvardX/CS50/2012H", "HarvardX/CS50x/2012", "HarvardX/CS50x/2014_T1", "HarvardX/CS50x_3/2015T1",
           "HarvardX/ER22.1x/1T2014", "HarvardX/ER22x/2013_Spring", "HarvardX/GSE1.1x/3T2014",
           "HarvardX/GSE1x/2014_JFMA", "HarvardX/GSE2x/2T2014", "HarvardX/HAA1x/1T2014",
           "HarvardX/HDS1544.1x/2013_SOND", "HarvardX/HKS-211.1x/3T2013", "HarvardX/HKS211.1x/3T2013",
           "HarvardX/HLS1.1x/1T2014", "HarvardX/HLS1x/2013_Spring", "HarvardX/HLS1xA/Copyright",
           "HarvardX/HLS1xB/Copyright", "HarvardX/HLS1xC/Copyright", "HarvardX/HLS1xD/Copyright",
           "HarvardX/HLS2x/1T2015", "HarvardX/HSPH-HMS214x/2013_SOND", "HarvardX/HUM2.1x/3T2014",
           "HarvardX/HUM2.2x/3T2014", "HarvardX/HUM2.3X/3T2014", "HarvardX/HUM2.4x/3T2014",
           "HarvardX/HUM2.5x/3T2014", "HarvardX/MCB80.1x/2013_SOND", "HarvardX/MCB80.2x/3T2014",
           "HarvardX/PH201x/2013_SOND", "HarvardX/PH207x/2012_Fall", "HarvardX/PH210x/1T2014",
           "HarvardX/PH278x/2013_Spring", "HarvardX/PH525x/1T2014", "HarvardX/PH555x/2014_T2",
           "HarvardX/SPU17x/3T2013", "HarvardX/SPU27x/2013_Oct", "HarvardX/SPU30x/2T2014",
           "HarvardX/SW12.10x/1T2015", "HarvardX/SW12.2x/1T2014", "HarvardX/SW12.3x/1T2014",
           "HarvardX/SW12.4x/1T2014", "HarvardX/SW12.5x/2T2014", "HarvardX/SW12.6x/2T2014",
           "HarvardX/SW12.7x/3T2014", "HarvardX/SW12.8x/3T2014", "HarvardX/SW12.9x/3T2014",
           "HarvardX/SW12x/2013_SOND", "HarvardX/SW25x/1T2014", "HarvardX/SW47.1x/2014_T3",
           "HarvardX/USW30x/2T2014", "HKUSTx/COMP102x/2T2014", "HKUSTx/EBA101x/3T2014", "HKUSTx/ELEC1200.1x/3T2014",
           "HKUx/HKU01x/3T2014", "HKUx/HKU02.1x/3T2014", "HKUx/HKU03x/1T2015", "IDBx/IDB1x/2T2014",
           "IDBx/IDB2x/3T2014", "IDBx/IDB_LSC101x/3T2014", "IITBombayX/CS101.1x/2T2014",
           "IITBombayX/CS101.2x/3T2014", "IITBombayX/EE210.1X/3T2015", "IITBombayX/EE210.2X/3T2015",
           "IITBombayX/ME209x/2T2014", "IMF/FPP.1x/2T2014", "IMFx/DSAx/3T2014", "IMFx/ESRx-June/2T2014",
           "IMFx/ESRx/2T2014", "IMFx/FPP.1x/1T2014", "IMFx/FPP.1x_fr/3T2014", "IMFx/FPPx/3T2013",
           "IMFx/OL14.01/2T2014", "KIx/KIBEHMEDx/3T2014", "KIx/KIexploRx/3T2014", "KIx/KIGlobalHx/2014_T3",
           "KIx/KIPractihx/3T2014", "KyotoUx/001x/1T2014", "KyotoX/001x/1T2014", "LinuxFoundationX/LFS101x/2T2014",
           "LouvainX/Louv1.01x/1T2014", "LouvainX/Louv1.1x/3T2014", "LouvainX/Louv1.2x/4T2014",
           "LouvainX/Louv2.01x/1T2014", "LouvainX/Louv3.01x/1T2014", "LouvainX/Louv3.02x/3T2014",
           "LouvainX/Louv4.01x/1T2014", "McGillX/ATOC185x/2T2014", "McGillX/ATOC185x_2/1T2015",
           "McGillX/CHEM181x/1T2014", "McGillX/CHEM181x_2/3T2014", "MITx/11.126x/3T2014", "MITx/11.132x/3T2014",
           "MITx/12.340x/1T2013", "MITx/12_340x/1T2014", "MITx/14.73x/2013_Spring", "MITx/14.73x/2014_Q1",
           "MITx/14_73x/1T2014", "MITx/15.071x/1T2014", "MITx/15.071x_2/1T2015", "MITx/15.390x/1T2014",
           "MITx/15.S23x/3T2014", "MITx/16.101x/2013_SOND", "MITx/16.110x/1T2014", "MITx/18.01.1x/2T2015",
           "MITx/18.01.2x/3T2015", "MITx/18.01.3x/1T2016", "MITx/2.01x/2013_Spring", "MITx/2.01x/2T2014",
           "MITx/2.03_2x/3T2014", "MITx/2.03x/3T2013", "MITx/21W.789x/1T2014", "MITx/24.00_1x/3T2014",
           "MITx/24.00x/2013_SOND", "MITx/3.032x/3T2014", "MITx/3.086-2x/1T2015", "MITx/3.086_2x/3T2014",
           "MITx/3.086x/2013_SOND", "MITx/3.091/MIT_2012_Fall", "MITx/3.091x/2012_Fall", "MITx/3.091X/2013_Fall",
           "MITx/3.091x/2013_Spring", "MITx/3.091x_2/1T2014", "MITx/3.091x_3/3T2014", "MITx/4.605x/2013_SOND",
           "MITx/4.605x_2/3T2014", "mitx/4605testx/8212013", "MITx/6.00.1-x/1T2014", "MITx/6.00.1_3x/2T2014",
           "MITx/6.00.1_4x/3T2014", "MITx/6.00.1x/3T2013", "MITx/6.00.2_2x/3T2014", "MITx/6.00.2x/1T2014",
           "MITx/6.00/MIT_2012_Fall", "MITx/6.00/MIT_2013_Spring", "MITx/6.002_4x/3T2014",
           "MITx/6.002x-EE98/2012_Fall_SJSU", "MITx/6.002x-NUM/2012_Fall_NUM", "MITx/6.002x/2012_Fall",
           "MITx/6.002x/2013_Spring", "MITx/6.00short/2013_IAP", "MITx/6.00x/2012_Fall", "MITx/6.00x/2013_Spring",
           "MITx/6.041x/1T2014", "MITx/6.341x/3T2014", "MITx/6.832x/3T2014", "MITx/6.SFMx/1T2014",
           "MITx/7.00x/2013_SOND", "MITx/7.00x/2013_Spring", "MITx/7.00x_2/2T2014", "MITx/7.012/MIT_2013_Spring",
           "MITx/7.QBWx/2T2014", "MITx/8.01x/2013_SOND", "MITx/8.02x/2013_Spring", "MITx/8.05x/1T2015",
           "MITx/8.851x/3T2014", "MITx/8.APx/1T2015", "MITx/8.EFTx/3T2014", "MITx/8.MechCx/1T2015",
           "MITx/8.MReV/2013_Summer", "MITx/8.MReVx/2T2014", "MITx/8.MReVx_T/2T2014", "MITx/9.01x/3T2014",
           "MITx/EECS.6.002x/3T2013", "MITx/EECS.6.00x/3T2013", "MITx/ESD.SCM1x/3T2014", "MITx/JPAL101_1x/3T2014",
           "MITx/JPAL101x/1T2014", "mitx/js001/1", "MITx/MAS.S69x/1T2014", "MITx/VJx/3T2014", "OECx/BP111x/3T2014",
           "OECx/Energy103/3T2014", "OECx/PH241x/3T2014", "ora2/1/1", "PekingX/00330280x/2015Q1",
           "PekingX/01034040x/3T2014", "PekingX/01339180X/3T2013", "PekingX/01718330x/1T2014",
           "PekingX/02030330x/3T2013", "PekingX/02030330X/3T2013", "PekingX/02030330x_1/3T2014",
           "PekingX/02132750x/2015Q1", "PekingX/02930106x/2015Q1", "PekingX/03131840x/3T2014",
           "PekingX/04332960X/3T2013", "PekingX/04830050.2x/2015Q3", "PekingX/04830050x/2T2014",
           "PekingX/04830260x/2015Q1", "PekingX/04832430X/3T2013", "PekingX/18000123x/2015Q1",
           "PekingX/18001001x/2015Q1", "PekingX/20000001x/2015Q1", "PekingX/532001x/3T2014",
           "PKUx/08254001X/3T2014", "PMx/PMs101x/1T2014", "RiceX/AdvBIOx/2014T3", "RiceX/AdvENVSCIx/3T2014",
           "RiceX/AdvPHY2/3T2014", "RiceX/APBIOx/3T2014", "RiceX/APESx/3T2014", "RiceX/APPH2x/3T2014",
           "RiceX/BIOC372.1x-F14/2T2014", "RiceX/BIOC372.1x/1T2014", "RiceX/BIOC372.1x_Build/2T2014",
           "RiceX/BIOC372.2x/2T2014", "RiceX/ELEC301x/T1_2014", "RiceX/ELEC301x_/2015Q3", "RiceX/PHYS102x/2013_Oct",
           "RiceX/PHYS201x/3T2014", "RiceX/PHYS_102x/1T2014", "RudnickX/MRR101x/1T2014",
           "SchoolYourself/AlgebraX/1T2015", "SchoolYourself/GeometryX/1T2015", "SMES/ASLCx/1T2015",
           "SMES/COL101x/1T2015", "SMES/PSYCH101x/1T2015", "SNUx/SNU034.005.1x/1T2014",
           "SNUx/SNU216B.226.1x/1T2014", "SNUx/SNU446.345.1x/1T2014", "SNUx/SNU446.345.2x/2T2014",
           "SPx/SRP225/infinity", "STUD-1452/STUD-1452/STUD-1452", "studentsupport/SS103/2014_T4",
           "TakaMOL/Train101x/3T2014", "TBRx/APEngCompx/1T2015", "TBRx/APSTATx/1T2015", "TBRx/EngCompX/1T2015",
           "TBRx/STATx/1T2015", "TenarisUniversityX/CNC.ETRRx/3T2014", "TestAK/AK101/2014_T1",
           "TsinghuaX/00690242_1x/1T2014", "TsinghuaX/00690242_2x/3T2014", "TsinghuaX/00720091X/3T2014",
           "TsinghuaX/20220214x/3T2014", "TsinghuaX/20220332_2x/1T2014", "TsinghuaX/20220332X/3T2013",
           "TsinghuaX/30240184.x/3T2014", "TsinghuaX/30240184x/1T2014", "TsinghuaX/60240013x/3T2014",
           "TsinghuaX/70167012x/3T2014", "TsinghuaX/80000901_1X/3T2013", "TsinghuaX/80000901_2x/1T2014",
           "TsinghuaX/80000901x/3T2014", "TsinghuaX/80512073.x/3T2014", "TsinghuaX/80512073x/1T2014",
           "TUMx/AUTONAVx/2T2014", "UAMx/Android301x/1T2015", "UAMx/Quijote501x/1T2015", "UAMx/QuiOrg101x/1T2015",
           "UAMx/TxEtj201x/1T2015", "UBCx/China300x/3T2014", "UBCx/Water201x/3T2014", "UC3Mx/CEH.1-ENx/1T2015",
           "UC3Mx/CEH.1-ESx/1T2015", "UC3Mx/HGA.1x/1T2015", "UC3Mx/MMC.1x/1T2015", "UC3Mx/PCA.1x/1T2015",
           "University_of_TorontoX/BE101x/2013_SOND", "University_of_TorontoX/BE101x_2/3T2014",
           "University_of_TorontoX/LA101x/1T2014", "University_of_TorontoX/OEE101x/3T2013", "UQx/BIOIMG101x/1T2014",
           "UQx/Crime101x/3T2014", "UQx/Denial101x/1T2015", "UQx/HYPERS301x/1T2014", "UQx/Sense101x/3T2014",
           "UQx/Think101x.2/1T2015", "UQx/Think101x/1T2014", "UQx/THINK101x/1T2014", "UQx/TROPIC101x/1T2014",
           "UQx/World101x/3T2014", "UQx/Write101x/3T2014", "usm/be1/winter", "UTArlingtonX/ENGR1.0x/2T2015",
           "UTArlingtonX/LINK5.10x/3T2014", "UTAustinX/Energy1.0x/3T2014", "UTAustinX/UT.1.01x/2013_Sept",
           "UTAustinX/UT.2.01x/2013_Sept", "UTAustinX/UT.2.02x/3T2014", "UTAustinX/UT.3.01x/2013_Sept",
           "UTAustinX/UT.3.02x/3T2014", "UTAustinX/UT.4.01x/2013_Sept", "UTAustinX/UT.5.01x/1T2014",
           "UTAustinX/UT.5.02x/1T2015", "UTAustinX/UT.6.01x/1T2014", "UTAustinX/UT.7.01x/3T2014",
           "UTAustinX/UT.8.01x/1T2014", "UTAustinX/UT.8.02x/1T2015", "UTAustinX/UT.9.01x/1T2014",
           "UTAustinX/UT.PreC.10.01x/3T2015", "UTokyoX/UTokyo001x/3T2014", "UTokyoX/UTokyo002x/3T2014",
           "UWashingtonX/AA432x/3T2014", "UWashingtonX/COMM220UWx/1T2014", "UWashingtonX/ECFS302x/2T2014",
           "UWashingtonX/ECFS311x/2T2014", "VJx/VJx/3T2014", "WageningenX/GFFCx/1T2015",
           "WageningenX/NUTR101x/1T2014", "WellesleyX/ANTH_207x/2013_SOND", "WellesleyX/ENG_112x/2014_SOND",
           "WellesleyX/HIST229x/2013_SOND", "WellesleyX/SOC108x/2014_SOND", "WestonHS/APCM101x/2T2015",
           "WestonHS/MechC101x/2T2015", "WestonHS/PFAP1x/3T2015", "WestonHS/PFLC1x/3T2015",
           "XuetangX/PerformanceTest101/2T2014", "XuetangX/X0001/2014_Fall", "y/y/y"]


def check_course(course_id):
    """
    Gather info on the given course.
    """
    course = check_course.api_client.courses(course_id)
    reporter = CourseReporter(course, check_course.http_client)
    report = reporter.report()
    logger.info(report)
    check_course.q.put(report)


def pool_init(q, api_client, http_client):
    """
    Initialize the variables needed by the mapping function.
    """
    check_course.q = q
    check_course.api_client = api_client
    check_course.http_client = http_client


def write_csv(reports):
    """
    Write the data from the Queue to a CSV.
    """
    keys = ['course_id'] + COURSE_PAGES + API_REPORT_KEYS
    f = open('{}-course_report.csv'.format(timestamp), 'wb')
    dict_writer = csv.DictWriter(f, keys)
    dict_writer.writer.writerow(keys)

    while not reports.empty():
        dict_writer.writerow(reports.get())


def main():
    start = time.time()
    api_client = Client(base_url=API_SERVER_URL, auth_token=API_AUTH_TOKEN, timeout=1000)
    http_client = requests.Session()

    # Login
    http_client.get(DASHBOARD_SERVER_URL + '/test/auto_auth/')

    # Collect the data
    reports = Queue()
    p = Pool(NUM_PROCESSES, pool_init, [reports, api_client, http_client])
    p.map(check_course, COURSES)

    # Write the data to an external file
    write_csv(reports)
    end = time.time()

    logger.info('Finished in {} seconds.'.format(end-start))


if __name__ == "__main__":
    main()
