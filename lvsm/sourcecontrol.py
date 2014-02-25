"""
Source control classes used for managing the configuration
"""
import subprocess
import logging
import getpass
import utils

logger = logging.getLogger('lvsm')


class Subversion(object):
    def __init__(self, args):
        super(Subversion, self).__init__()

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

    def modified(self, filename):
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

    def update(self, filename, node):
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
    def __init__(self, args):
        super(Git, self).__init__()

        try:
            self.remote = args['git_remote']
        except KeyError:
            logger.error("git remote not defined!")
            import sys
            sys.exit(1)

        self.branch = args['git_branch']

    def commit(self, filename):
        try:    
            cmd = ['dirname', filename]
            wd = utils.check_output(cmd, silent=True).rstrip('\n')

            cmd = ['basename', filename]
            name = utils.check_output(cmd, silent=True).rstrip('\n')

            args = ['git', 'commit', name]
            logger.info("Running command: %s" % " ".join(args))            
            subprocess.call(args, cwd=wd)

        except (OSError, subprocess.CalledProcessError) as e:
            logger.error(e)  

    def modified(self, filename):
        """Verifies that a file was modified. Returns True if it was"""
        try:    
            cmd = ['dirname', filename]
            wd = utils.check_output(cmd, silent=True).rstrip('\n')

            cmd = ['basename', filename]
            name = utils.check_output(cmd, silent=True).rstrip('\n')

            args = ['git', 'status', '-s', name]
            stdout = utils.check_output(args, cwd=wd)
            
        except (OSError, subprocess.CalledProcessError) as e:
            logger.error(e)
            return False

        output = stdout.strip(' \n')
        if output and output.startswith('M'):
            logger.debug('%s was modified' % filename)
            return True
        else:
            return False
        
    def update(self, filename, node):
        """
        Check the status of the file and if modified return True.
        Assumption is that a 'remote' named 'lvsm' is created and
        points to the matching git repo on each opposite node.
        ex.
        remote.lvsm.url=user@node1:/etc/lvsm/
        """
        
        try:
            cmd = ['dirname', filename]
            logger.debug('Updating %s' % filename)
            wd = utils.check_output(cmd, silent=True).rstrip('\n')
            logger.debug('working directory used by git: %s' % wd)

            # remote = 'lvsm'
            args = ['ssh', node, 'cd', wd, ';', 'git', 'pull', self.remote, self.branch]
            logger.info('Running command: %s' % " ".join(args))
            subprocess.call(args)

        except (OSError, subprocess.CalledProcessError) as e:
            logger.error(e)
            return False

class SourceControl(object):
    """
    Factory class for the scm objects. Only this class should be instantiated.
    """
    scm = {'subversion': Subversion, 'git': Git}

    def __new__(self, name, args=dict()):
        return SourceControl.scm[name](args)
