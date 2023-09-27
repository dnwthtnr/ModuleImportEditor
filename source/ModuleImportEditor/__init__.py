import os, sys, re

from source import file_management
from source.ModuleImportEditor import keys

defaultConfigPath = "config.json"

def readConfig(path=None):
    """
    Reads the given config path
    Parameters
    ----------
    path

    Returns
    -------
    dict
        Data from config

    """
    if path is None:
        path = defaultConfigPath

    if not os.path.exists(path):
        raise FileNotFoundError(f'File: {path} does not exist.')

    data = file_management.read_json(path)
    return data


def writeConfig(data, outputPath=None):
    """
    Writes teh given config data

    Parameters
    ----------
    data
    outputPath

    """
    if outputPath is None:
        outputPath = defaultConfigPath


    if not isinstance(data, dict):
        raise TypeError(f'Given data must be dictionary')
    file_management.write_json(path=outputPath, data=data)


def readSubstitutionQueueDict(configPath=None):
    if configPath is None:
        configPath = defaultConfigPath

    _data = readConfig(configPath)

    _substitutionQueueDict = _data.get(keys.substitutionQueueDictKey)

    if _substitutionQueueDict is None:
        raise KeyError(f'Key: {keys.substitutionQueueDictKey} not in provided config.')

    return _substitutionQueueDict


def writeSubstitutionQueueDict(substitutionQueueDict, configPath=None):
    if configPath is None:
        configPath = defaultConfigPath
    _data = readConfig(configPath)
    _data[keys.substitutionQueueDictKey] = substitutionQueueDict
    writeConfig(_data, configPath)


# region Perform Replacement Actions

def parseAndReplace(targetString, regexPattern, replacementText):
    """
    Replaces text matching the given regex expression with the replacementText

    Parameters
    ----------
    targetString : str
        Text to run replacement on
    regexPattern : str
        Regex expression to match text in file to
    replacementText : str
        Text to replace matches with

    Returns
    -------
    str
        Resulting text after replacements

    """
    resultString = re.sub(
        pattern=regexPattern,
        repl=replacementText,
        string=targetString,
        count=0,
        flags=re.MULTILINE
    )
    return resultString


def isValidSubstitionList(substitutionList):
    """
    Checks if teh given list in a valid substitution list

    Parameters
    ----------
    substitutionList : list
        The list to check validity of

    Returns
    -------
    bool
        Whether or not the given list is a valid substitution list

    """
    if not isinstance(substitutionList, list):
        return False
    if len(substitutionList) != 2:
        return False
    if False in [isinstance(_item, str) for _item in substitutionList]:
        return False

    return True


def iteritiveParseAndReplace(targetString, substitutions):
    """
    Iterates over given substitution lists and runs the substituions on the given target string

    Parameters
    ----------
    targetString : str
        String to run substitutions on
    substitutions : list[list[str, str]]
        Substitutuions to run on target string

    Returns
    -------
    str
        The resulting string

    """
    resultString = targetString
    for substitutionList in substitutions:
        if not isValidSubstitionList(substitutionList):
            TypeError(f'Substitution list: {substitutionList} is not valid. Skipping')
            continue
        pattern = substitutionList[0]
        replacementText = substitutionList[1]

        resultString = parseAndReplace(targetString=resultString, regexPattern=pattern, replacementText=replacementText)

    return resultString


def parseAndReplaceModule(moduleDirectory, outputDirectory, substitutions, fileExtension=[".py"]):
    """
    Given a directory will search through and run the given substitutions on the files with the given extensions.

    Parameters
    ----------
    moduleDirectory : str
        The directory to run the substitutions on
    outputDirectory : str
        Directory to write the new files to
    substitutions : list[list[str, str]]
        A list containing lists defining a regex pattern and the text to replace that pattern with
    fileExtension : list[str]
        The file extensions to run substitutions on

    """

    if not os.path.exists(outputDirectory):
        os.mkdir(outputDirectory)


    # region Run Replacements on Files
    targetFiles = [
        _filename for _filename in os.listdir(moduleDirectory) if file_management.getFilepathSuffix(_filename) in fileExtension
    ]
    for filename in targetFiles:
        _filepath = os.path.join(moduleDirectory, filename)
        _outputFilepath = os.path.join(outputDirectory, filename)

        # if there have already been edits to the file it will be written here. Otherwise it will override past changes
        if os.path.exists(_outputFilepath):
            print('exists', _outputFilepath)
            _filepath = _outputFilepath


        try:
            _fileData = file_management.readFile(_filepath)
        except Exception as e:
            print(f'File cant be read: {_filepath}')
            continue

        if not isinstance(_fileData, str):
            continue

        _result = iteritiveParseAndReplace(targetString=_fileData, substitutions=substitutions)
        file_management.writeFile(_outputFilepath, _result)
    # endregion

    # region Run Recursively On Child Directories
    targetDirs = [_file for _file in os.listdir(moduleDirectory) if os.path.isdir(os.path.join(moduleDirectory, _file))]
    for dir in targetDirs:
        _fulldir = os.path.join(moduleDirectory, dir)
        _newOutputDir = os.path.join(outputDirectory, dir)
        if not os.path.exists(_newOutputDir):
            os.mkdir(_newOutputDir)
        parseAndReplaceModule(_fulldir, _newOutputDir, substitutions, fileExtension)
    # endregion
# endregion


if __name__ == "__main__":
    test = ("from pyqt_interface_elements import constants, buttons, icons\n"
	"from . import constants, buttons, icons\n"
	"from pyqt_interface_elements import constants, buttons, icons\n"
	"from pyqt_interface_elements import constants, buttons, icons\n"
	"from pyqt_interface_elements import constants, buttons, icons\n"
	"from pyqt_interface_elements import constants, buttons, icons\n"
	"from pyqt_interface_elements import constants, buttons, icons\n"
	"from pyqt_interface_elements import constants, buttons, icons\n"
	"from pyqt_interface_elements import constants, buttons, icons\n"
	"from pyqt_interface_elements import constants, buttons, icons\n"
	"from pyqt_interface_elements import constants, buttons, icons\n")

    # print(parseAndReplace(test, r"from pyqt_interface_elements ", "from . "))

    # print(os.listdir("Q:\__packages\_GitHub\ModuleImportEditor\source"))

    # print(isValidSubstitionList(["(from pyqt_interface_elements )", "from . "]))

    testpath = r"Q:\__packages\_GitHub\animation_exporter\lib\PySideWrapper\source\PySideWrappers"
    output = r"Q:\__packages\_GitHub\animation_exporter\lib\PySideWrapper\source\PySideWrappers"
    # parseAndReplaceModule(moduleDirectory=testpath, outputDirectory=output, substitutions=[
    #     ["(QtCore.Signal)", "QtCore.pyqtSignal"],
    #     ["(QtWidgets.QSizePolicy.)", "QtWidgets.QSizePolicy.Policy."],
    #     ["(QtWidgets.QStyle.SC)", "QtWidgets.QStyle.SubControl.SC"],
    #     ["(QtWidgets.QStyle.CC)", "QtWidgets.QStyle.ComplexController.CC"],
    #     ["(QtCore.Slot)", "QtCore.pyqtSlot"] ]
    #                       )
    parseAndReplaceModule(
        moduleDirectory=testpath,
        outputDirectory=output,
        substitutions=[
            ["(from . import)", "import"]
        ]
    )
