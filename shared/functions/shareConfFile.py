import configparser
config = configparser.ConfigParser()
config.read("config.ini")
def getConfigFile(section , part ):
    return config.get(section, part)
   
    