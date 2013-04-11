#!/usr/bin/python-2.7
import os
import subprocess

from config import RASQL_PATH, RASQL_ADMIN_PASSWORD, RASQL_ADMIN_USERNAME, SHOW_DEBUG, VIEWER, WAITING_FOR_ACTION_MESSAGE, EARTH_COLLECTION_NAME, VOLCANO_COLLECTION_NAME, VOLCANO_DB_COLLECTION_NAME, VOLCANO_INFRARED_COLLECTION_NAME, RASIMPORT

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def getDataPath(collection=""):
    demoPath = os.path.dirname(os.path.abspath(__file__))
    return demoPath + "/data/" + collection


def waitForAction():
    input("{}>#{}{}".format(Colors.OKGREEN, Colors.ENDC, WAITING_FOR_ACTION_MESSAGE))


def formatMessage(message, debug=False):
    retMess = "";
    if debug:
        retMess += "{}debug>#{}{}".format(Colors.WARNING, Colors.ENDC, message)
    else:
        retMess += "{}>#{}{}".format(Colors.OKGREEN, Colors.ENDC, message)
    return retMess + ""


def log(message, debug=False):
    if not debug or SHOW_DEBUG:
        print(formatMessage(message, debug))


def rasql(query, out="string", otherParams=[], admin=False, noOutput=False):
    cmdArgs = [RASQL_PATH];
    if admin:
        cmdArgs.append("--user")
        cmdArgs.append(RASQL_ADMIN_USERNAME)
        cmdArgs.append("--passwd")
        cmdArgs.append(RASQL_ADMIN_PASSWORD)
    cmdArgs.append("-q")
    cmdArgs.append(query)
    cmdArgs.append("--out")
    cmdArgs.append(out)
    if len(otherParams) > 0:
        cmdArgs += otherParams

    if not noOutput:
        log("Executing: `" + ' '.join(cmdArgs) + "`", True)
        log("Executed query: {blue}{query}{endBlue}".format(blue=Colors.OKBLUE, query=query, endBlue=Colors.ENDC))

    try:
        response = subprocess.check_output(cmdArgs, stderr=subprocess.STDOUT)
        if not noOutput:
            log("Response: " + str(response), True)
            if out == "csv":
                log("Response: " + str(response).replace("{", "]"))
    except subprocess.CalledProcessError as e:
        message = "Cmd={}\n;ReturnCode:{}\nOutput:{}".format(e.cmd, e.returncode, e.output)
        raise Exception(message)


def getEarthDemoInsertQuery():
    filesComponents = []
    offsetX = 0
    width = sliceWidth = 233
    height = 1023
    offsetY = 0
    for i in range(0, 10):
        fileId = '"{absPath}/earth_{index}.tif"[{offsetX}:{width},{offsetY}:{height}]'.format(
            absPath=getDataPath("earth"),
            index=i, offsetX=offsetX, width=width, offsetY=offsetY, height=height)
        filesComponents.append(fileId)
        offsetX = width + 1
        width = offsetX + sliceWidth
    query = "INSERT INTO {earth} REFERENCING (RGBImage) \n{files}".format(earth=EARTH_COLLECTION_NAME,
        files=',\n'.join(filesComponents))
    return query


def earthDemo():
    log("{}== Water salinity demo =={}".format(Colors.HEADER, Colors.ENDC))
    log("Inserting water salinity data for earth's oceans.")
    log("The data archive contains 10 files that compose the whole picture of earth.")
    log("For Example:")
    waitForAction();
    subprocess.call([VIEWER, "data/earth/earth_2.tif"])
    subprocess.call([VIEWER, "data/earth/earth_3.tif"])
    waitForAction()
    createCollQuery = "CREATE COLLECTION {earth} RGBSet".format(earth=EARTH_COLLECTION_NAME);
    rasql(query=createCollQuery, admin=True)
    log("Inserting data into the `earth` collection, one object with 10 tiles");
    rasql(getEarthDemoInsertQuery(), admin=True)
    log("Retrieving the whole image of the earth")
    rasql("SELECT tiff({earth}) FROM {earth}".format(earth=EARTH_COLLECTION_NAME), out="file",
        otherParams=["--outfile", "earth"])
    waitForAction()
    subprocess.call([VIEWER, "earth.tif"])


def earthDemoCleanup():
    subprocess.call(["rm", "-f", "earth.tif"]);
    rasql("DROP COLLECTION {earth}".format(earth=EARTH_COLLECTION_NAME), admin=True, noOutput=True)


def executeVolcanoInsertQueries():
    width = 1452
    height = 2299
    for i in range(0, 4):
        query = 'INSERT INTO {volcano} REFERENCING (RGBImage) "{absPath}/volcano_{index}.tif"[0:{width},0:{height}]'.format(
            volcano=VOLCANO_COLLECTION_NAME, absPath=getDataPath("volcano"),
            index=i, width=width, height=height);
        rasql(query=query, admin=True);


def volcanoDemo():
    log("{}== Volcano Particle Properties demo =={}".format(Colors.HEADER, Colors.ENDC));
    log("Inserting particle properties data for Eyjafjallajokull volcano")
    log("The data archive contains 4 image files each taken using a different wavelength")
    waitForAction()
    createCollQuery = "CREATE COLLECTION {volcano} RGBSet".format(volcano=VOLCANO_COLLECTION_NAME);
    rasql(createCollQuery, admin=True)
    log("Inserting data into the `volcano` collection, four objects each containing one tile");
    executeVolcanoInsertQueries()
    rasql("SELECT jpeg({volcano}) FROM {volcano}".format(volcano=VOLCANO_COLLECTION_NAME), out="file",
        otherParams=["--outfile", "volcano_%d"])
    waitForAction()
    subprocess.call([VIEWER, "volcano_1.jpg"])
    subprocess.call([VIEWER, "volcano_2.jpg"])
    subprocess.call([VIEWER, "volcano_3.jpg"])
    subprocess.call([VIEWER, "volcano_4.jpg"])


def volcanoDemoCleanup():
    subprocess.call(["rm", "-f", "volcano_1.jpg"]);
    subprocess.call(["rm", "-f", "volcano_2.jpg"]);
    subprocess.call(["rm", "-f", "volcano_3.jpg"]);
    subprocess.call(["rm", "-f", "volcano_4.jpg"]);
    rasql("DROP COLLECTION {volcano}".format(volcano=VOLCANO_COLLECTION_NAME), admin=True, noOutput=True)


def prepareMixDemo():
    createCollQuery = "CREATE COLLECTION {volcanoDb} RGBSet".format(volcanoDb=VOLCANO_DB_COLLECTION_NAME);
    rasql(createCollQuery, admin=True, noOutput=True)
    rasql("INSERT INTO {volcanoDb} VALUES inv_jpeg($1)".format(volcanoDb=VOLCANO_DB_COLLECTION_NAME), admin=True,
        otherParams=["--file", "data/volcano/volcanoInDb.jpg"], noOutput=True)


def mixDemo():
    log("{}== Mix storage demo =={}".format(Colors.HEADER, Colors.ENDC))
    prepareMixDemo()
    log(
        "Use Case: we have a stored image mask in the database (blob tile) and received a set of images (e.g. the volcano set)"
        " from which we should import only the ones that fulfill some certain properties when compared to the mask.")
    log("To avoid the overhead of inserting the whole set into the database, we will use the in-situ feature.")
    rasql("SELECT jpeg({volcano} AND {volcanoDb}) FROM {volcano},{volcanoDb}".format(volcano=VOLCANO_COLLECTION_NAME,
        volcanoDb=VOLCANO_DB_COLLECTION_NAME), otherParams=['--outfile', 'appliedVolcanoMask_%d'])
    waitForAction()
    subprocess.call([VIEWER, "appliedVolcanoMask_3.jpg"])
    subprocess.call([VIEWER, "appliedVolcanoMask_2.jpg"])
    log("Now that we confirmed that the second image is correct we can import it into the database")


def mixDemoCleanup():
    subprocess.call(["rm", "appliedVolcanoMask_1.jpg"]);
    subprocess.call(["rm", "appliedVolcanoMask_2.jpg"]);
    subprocess.call(["rm", "appliedVolcanoMask_3.jpg"]);
    subprocess.call(["rm", "appliedVolcanoMask_4.jpg"]);
    rasql("DROP COLLECTION {volcanoDb}".format(volcanoDb=VOLCANO_DB_COLLECTION_NAME), admin=True, noOutput=True)


def rasimportDemo():
    log("{}== rasimport demo =={}".format(Colors.HEADER, Colors.ENDC))
    log(
        "Use Case: the files that we want to import are spread over several subdirectories. Assuming the filenames are consistent "
        "we can use a regex expression to select the files that we need using the rasimport utility.\n Furthermore rasimport can "
        "detect the spatial domain of the images so we do not need to provide it ourselves.")
    waitForAction();
    createCollQuery = "CREATE COLLECTION {infraredVolcano} RGBSet".format(
        infraredVolcano=VOLCANO_INFRARED_COLLECTION_NAME);
    rasql(createCollQuery, admin=True)
    log(
        "{}rasimport -con rasimport.conf -referencing -coll {} -t RGBImage:RGBSet -d {} -regex \".*earth_infrared.*\" {}".format(
            Colors.OKBLUE, VOLCANO_INFRARED_COLLECTION_NAME, getDataPath("volcanoSlices"), Colors.ENDC))
    subprocess.call([RASIMPORT, "-conn", "rasimport.conf", "-coll", VOLCANO_INFRARED_COLLECTION_NAME, "-d",
                     getDataPath("volcanoSlices"), "-t", "RGBImage:RGBSet", "-referencing", "-regex",
                     ".*earth_infrared.*"])
    waitForAction()
    rasql("SELECT jpeg({volcanoInfrared}) FROM {volcanoInfrared}".format(volcanoInfrared=VOLCANO_INFRARED_COLLECTION_NAME), otherParams=["--outfile", "volcanoSlice_%d"])
    subprocess.call([VIEWER, "volcanoSlice_3.jpg"])

def rasimportCleanup():
    for i in range(1,10):
        subprocess.call(["rm", "volcanoSlice_{}.jpg".format(i)])
    rasql("DROP COLLECTION {volcanoInfrared}".format(volcanoInfrared=VOLCANO_INFRARED_COLLECTION_NAME), admin=True, noOutput=True)




def cleanup():
    earthDemoCleanup()
    volcanoDemoCleanup()
    mixDemoCleanup()
    rasimportCleanup()


def main():
    log("{}=== Demo for InSitu Feature ==={}".format(Colors.HEADER, Colors.ENDC))
    try:
        earthDemo()
        waitForAction()
        log("\n\n")
        rasimportDemo()
        waitForAction()
        log("\n\n")
        volcanoDemo()
        waitForAction()
        log("\n\n")
        mixDemo()
        log("{}=== Demonstration is finished. ==={}".format(Colors.HEADER, Colors.ENDC))
    except Exception as e:
        print("{red}ERROR{endRed}!\nException Message:\n {mess}".format(red=Colors.FAIL, endRed=Colors.ENDC,
            mess=e.args[0]))
    finally:
        cleanup()

if __name__ == "__main__":
    main()
