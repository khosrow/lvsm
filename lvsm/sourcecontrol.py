"""
Source control classes used for managing the configuration
"""
import subprocess
import logging
import getpass
import utils

logger = logging.getLogger('lvsm')


class Subversion(object):
    def __init__(self):
        super(SourceControl, self).__init()

    def commit(self, filename):
        # ask for username and passwd so user isn't bugged on each server
        self.username = raw_input("Enter SVN username: ")
        self.password = getpass.getpass("Enter SVN password: ")

        # prepare the svn commit command
        cmd = ['svn', 'commit']
        cmd.append('--username')
        cmd.append(self.username)
        cmd.append('--password')
        cmd.append(self.password)
        cmd.append(filename)

        # call the svn command
        try:
            logger.info("Running command: %s" % " ".join(cmd))
            ret = subprocess.call(cmd)
            if ret:
                logger.error("svn returned an error!")
        except IOError as e:
            logger.error(e)

    def status(self, filename):
        """Check the status of the file and if modified return True"""
        # prepare the svn command
        cmd = ['svn', 'status', filename]

        # call the svn command
        try:
            logger.info("Running the command: %s" % " ".join(cmd))
            ret = utils.check_output(cmd)
            if ret and ret.startswith('M'):
                return True
        except IOError as e:
            logger.error(e)
        except subprocess.CalledProcessError as e:
            logger.error(e.output)
        return False

    def update(self, filename):
        # prepare the svn command
        cmd = ['svn', 'update',
               '--username', self.username,
               '--password', self.password,
               filename]

        # call the svn command
        try:
            logger.info("Running the command: %s" % " ".join(cmd))
            ret = subprocess.call(cmd)
            if ret:
                logger.error("svn return an error!")
        except IOError as e:
            logger.error(e)


class Git(object):
    """
    Git class handles storing the configuration in a git repository
    The assumption is that the repositories are already setup.
    """
    def __init__(self):
        super(SourceControl, self).__init()

    def commit(self, filename):
        cmd = ['git', 'commit', filename]
        try:
            logger.info("Running command: %s" % " ".join(cmd))
            ret = subprocess.call(cmd)
            if ret:
                logger.error("git returned an error!")
        except IOError as e:
            logger.error(e)

    def status(self, filename):
        """Verifies that a file was modified. Returns True if it was"""
        # prepare the command
        cmd = ['git', 'status', '-s', filename]

        # call the command
        try:
            logger.info("Running the command: %s" % " ".join(cmd))
            ret = utils.check_output(cmd)
            if ret and ret.startswith('M'):
                return True
        except IOError as e:
            logger.error(e)
        except subprocess.CalledProcessError as e:
            logger.error(e.output)
        return False

    def update(self, filename):
        """
        Check the status of the file and if modified return True.
        Assumption is that a 'remote' named 'cluster' is created and
        points to the matching git repo on each opposite node.
        ex.
        remote.lvsm.url=user@node1:/etc/lvsm/
        """
        # prepare the git command
        cmd = ['git', 'pull', 'lvsm']

        # call the command
        try:
            logger.info("Running the command: %s" % " ".join(cmd))
            ret = subprocess.call(cmd)
            if ret:
                logger.error("git returned an error!")
        except IOError as e:
            logger.error(e)


class SourceControl(object):
    """
    Factory class for the scm objects. Only this class should be instantiated.
    """
    scm = {'subversion': Subversion, 'git': Git}

    def __new__(self, name):
        return SourceControl.scm[name]
