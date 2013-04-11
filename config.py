#This file contains the configuration options for the demo
#Please adjust them according to your needs

#Should be adjusted
RASQL_PATH = "/srv/enterprise/bin/rasql"                #path to the rasql executable e.g. /srv/rasdaman/bin/rasql or rasql if already in PATH for executing user
RASQL_ADMIN_USERNAME = "rasadmin"                       #admin username
RASQL_ADMIN_PASSWORD = "rasadmin"                       #admin password
SHOW_DEBUG = False                                      #shows debug information like query response, should be False in actual demos
VIEWER = "eog"                                          #any program that can be used to open tif/jpg files e.g. eog / okular
RASIMPORT = "/srv/enterprise/bin/rasimport"             #path to the rasimport executable, same as rasql

#Adjust only if needed
EARTH_COLLECTION_NAME = "earth"                         #the rasdaman collection name for the earth dataset. will be created automatically for the demo
VOLCANO_COLLECTION_NAME = "volcano"                     #the volcano collection name for the volcano dataset
VOLCANO_DB_COLLECTION_NAME = "volcanoInDb"              #the volcano collection name for the volcano dataset that will be inside db
VOLCANO_INFRARED_COLLECTION_NAME = "volcanoInfrared"    #the infrared volcano images collection needed for rasimport demo
WAITING_FOR_ACTION_MESSAGE = "Press enter to continue"  #this message will be displayed in the console when a wait period is needed, e.g. when displaying an image



