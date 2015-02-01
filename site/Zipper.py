##
## Zipper.py
##
import distutils.archive_util 

def zipperFunction(target, source, env):
        """Function to use as an action which creates a ZIP file from the arguments"""
        targetName = str(target[0])
        sourceDir = str(source[0])
        distutils.archive_util.make_archive(targetName, 'zip', sourceDir)
