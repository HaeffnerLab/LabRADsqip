# Copyright (C) 2007  Matthew Neeley
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
labrad.node

Provides an interface to manage multiple labrad servers running on a particular
computer. The node runs each server in a separate process, so that they can not
interfere with each other. Information such as the manager host, port and
password are passed to the child process in environment variables or via
command line arguments. The startup process for each child server is controlled
by an associated .ini file.

The node name is read either from the LABRADNODE environment variable,
or failing that the system's hostname.

The node running on a particular computer is configured via the registry, at
the path ['', 'Nodes', node_name]. Defaults values can be configured to be
used whenever a new node connects, at ['', 'Nodes', '__default__']. The
configuration keys are:

  directories (*s): file directories to be scanned for servers. Any subdirs
                    that contain a file called '.nodeignore' will be skipped,
                    along with all their subdirs.
  extensions (*s): what files to look at, e.g. ['.ini', '.py', '.exe']
  autostart (*s): list of servers to be autostarted

Changes required on the server:

See "launchable-server.ini" for a description of how to have a server appear in
the node. See labrad-servers/Qubit Server/ for an example of a java server.

Another option is to have this configuration in the file itself, set off by
### BEGIN NODE INFO and ### END NODE INFO. See servers/gpibMockDeviceServer.py
in this repository for an example.

***N.B.*** The name given in the server's [info] section MUST MATCH the name
given as a class variable in the server class itself. That is, note that the
name string "GPIB Mock Device Server" appears _twice_. If this is not the case,
then while the node will still start the server, it will not register that the
server has been started and you will have to drop the server connection manually
to restart it.

Bonus: The node will also open up compiled executable files to look for
this information. This is how it works for the Direct Ethernet server, for
example.

The node can log to a file or via the syslog fascility.  Syslog can be
configured to filter messages generated by the node and its servers.
For rsyslogd on ubuntu, create the following file:

/etc/rsyslog.d/71-labrad.conf
:syslogtag,contains,"labrad"			/var/log/labrad.log;RSYSLOG_TraditionalFileFormat
"""

from __future__ import with_statement

from ConfigParser import SafeConfigParser
from datetime import datetime
import logging
import logging.handlers
import os
import shlex
import socket
import StringIO
import sys
import zipfile

from twisted.application.service import MultiService
from twisted.application.internet import TCPClient
from twisted.internet import defer, reactor
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.protocol import ProcessProtocol
from twisted.internet.error import ProcessDone, ProcessTerminated
from twisted.python import usage
from twisted.python.runtime import platformType

import labrad
from labrad import protocol, util, types as T, constants as C
from labrad.server import LabradServer, setting
import labrad.support
from labrad.util import dispatcher, findEnvironmentVars, interpEnvironmentVars


LOG_LENGTH = 1000 # maximum number of lines of stdout to keep per server


class ServerProcess(ProcessProtocol):
    """A class to represent a running server instance."""

    timeout = 20
    shutdownTimeout = 5

    def __init__(self, env):
        self.env = os.environ.copy()
        self.env.update(env, DIR=self.path, FILE=self.filename)
        cls = self.__class__
        self.name = interpEnvironmentVars(cls.instancename, self.env)
        self.args = shlex.split(self.cmdline)
        self.args = [interpEnvironmentVars(a, self.env) for a in self.args]
        self.starting = False
        self.started = False
        self.stopping = False
        self.output = []
        self._lock = defer.DeferredLock()
        logname = 'labrad.' + labrad.support.mangle(self.name)
        self.logger = logging.getLogger(logname)

    @property
    def status(self):
        if self.starting:
            return 'STARTING'
        elif self.started:
            return 'STARTED'
        elif self.stopping:
            return 'STOPPING'
        else:
            return 'STOPPED'

    def start(self):
        """Start this server instance."""
        return self._lock.run(self._start)

    def stop(self):
        """Stop this server instance."""
        return self._lock.run(self._stop)

    def restart(self):
        """Restart this server instance."""
        return self._lock.run(self._restart)

    @inlineCallbacks
    def _start(self):
        if self.started:
            return
        print "starting '%s'..." % self.name
        print "path:", self.path
        print "args:", self.args
        self.starting = True
        self.startup = defer.Deferred()
        dispatcher.connect(self.serverConnected, 'serverConnected')
        self.emitMessage('server_starting')
        # This looks crazy.  On Unix, spawnProcess calls fork() and then
        # execvpe which expects an executable name and a series of arguments,
        # and tries to resolve the executable using PATH.  On windows,
        # it calls createProcess, which expects a command string and an
        # optional executable.  If the executable argument is present,
        # it must be an absolute path including .exe suffix.  If executable
        # is not present, the first part of the command string is used,
        # and invokes the %PATH% and extension search.
        #
        # Twisted spawnProcess only supports posix (including Mac) and
        # win32, so we just abandon anything else.
        # Relevant code is in twisted/internet/process.py:_BaseProcess and
        # twisted/internet/dumbwin32proc.py:Process. The twisted docs for
        # spawnProcess say that the full executable path is required, but
        # this is not in fact the case. See:
        # http://twistedmatrix.com/documents/current/api/twisted.internet.interfaces.IReactorProcess.spawnProcess.html
        if platformType == 'posix':
            executable = self.args[0]
        elif platformType == 'win32':
            executable = None
        else:
            raise RuntimeError("Unsupported platform %s" % platformType)

        self.proc = reactor.spawnProcess(self, executable, self.args,
                                         env=self.env, path=self.path)
        timeoutCall = reactor.callLater(self.timeout, self.kill)
        try:
            yield self.startup
            self.emitMessage('server_started')
        except:
            self.emitMessage('server_stopped')
            raise
        finally:
            self.starting = False
            if timeoutCall.active():
                timeoutCall.cancel()
            try:
                dispatcher.disconnect(self.serverConnected, 'serverConnected')
            except Exception, e:
                print 'Error while disconnecting signal:', e

    @inlineCallbacks
    def _stop(self):
        if not self.started:
            return
        print "stopping '%s'..." % self.name
        self.stopping = True
        self.shutdown = defer.Deferred()
        self.emitMessage('server_stopping')
        # hack: marker to tell the kill func that it worked
        finished = [False]
        self.kill(finished)
        yield self.shutdown
        finished[0] = True
        self.stopping = False
        self.emitMessage('server_stopped')

    @inlineCallbacks
    def _restart(self):
        yield self._stop()
        yield self._start()

    def emitMessage(self, msg):
        """Emit a message to other parts of this application."""
        dispatcher.send(msg,
                        sender=self,
                        server=self.__class__.name,
                        instance=self.name)

    def serverConnected(self, ID, name):
        """Called when a server connects to LabRAD.

        If the name matches our name, we'll assume this server
        started successfully.  This may not be the case (e.g. if
        two nodes are trying to start the same server simultaneously),
        but there's no way to find out from LabRAD which node
        a given server is running on, so this will have to do.
        """
        if name == self.name:
            self.ID = ID
            if self.starting:
                self.started = True
                self.startup.callback(self)

    def processEnded(self, reason):
        """Called when the server process ends.

        We check to see the reason why this process failed, and then
        call the appropriate deferred, depending on the current state.
        """
        if isinstance(reason.value, ProcessDone):
            print "'%s': process closed cleanly." % self.name
        elif isinstance(reason.value, ProcessTerminated):
            print "'%s': process terminated: %s" % (self.name, reason.value)
        else:
            print "'%s': process ended: %s" % (self.name, reason)
        self.started = False
        if self.starting:
            err = T.Error('Startup failed.', payload=self.output)
            self.startup.errback(err)
        elif self.stopping:
            self.shutdown.callback(None)
        else:
            # looks like this thing died on its own
            self.emitMessage('server_stopped')

    @inlineCallbacks
    def kill(self, finished=None):
        """Kill the server process."""
        if not self.started:
            return
        try:
            servers = self.client.servers
            if hasattr(self, 'shutdownMode') and self.name in servers:
                mode, ID = self.shutdownMode
                if mode == 'message':
                    # try to shutdown by sending a message
                    servers[self.name].sendMessage(ID)
                elif mode == 'setting':
                    # try to shutdown by calling a setting
                    try:
                        yield servers[self.name][ID]()
                    except:
                        pass
                yield util.wakeupCall(self.shutdownTimeout)

            # hack to let us know that we did indeed finish killing the server
            if finished is not None:
                if finished[0]:
                    return

            # if we're not dead yet, kill with a vengeance
            if self.started:
                self.proc.signalProcess('KILL')
        except Exception:
            logging.error('Error while trying to kill server process for "%s":' % self.name,
                          exc_info=True)

    def outReceived(self, data):
        """Called when the server prints to stdout."""
        self.output.append((datetime.now(), data))
        self.output = self.output[-LOG_LENGTH:]
        self.logger.info(data.strip())

    def errReceived(self, data):
        """Called when the server prints to stderr."""
        self.output.append((datetime.now(), data))
        self.output = self.output[-LOG_LENGTH:]
        self.logger.warning(data.strip())

    def clearOutput(self):
        """Clear the log of stdout."""
        self.output = []


def findConfigBlock(path, filename):
    """Find a Node configuration block embedded in a file."""
    # markers to delimit node info block
    BEGIN = "### BEGIN NODE INFO"
    END = "### END NODE INFO"
    with open(os.path.join(path, filename), 'rb') as file:
        foundBeginning = False
        lines = []
        for line in file:
            if line.upper().strip().startswith(BEGIN):
                foundBeginning = True
            elif line.upper().strip().startswith(END):
                break
            elif foundBeginning:
                line = line.replace('\r', '')
                line = line.replace('\n', '')
                lines.append(line)
        return '\n'.join(lines) if lines else None


def createGenericServerCls(path, filename, conf):
    """Create a ServerProcess class representing a generic server.

    Options for this server are passed in as a string in standard
    .ini format.  We use a string rather than a file to allow this
    configuration to be extracted from a larger file if necessary.
    """
    class cls(ServerProcess):
        pass

    scp = SafeConfigParser()
    scp.readfp(StringIO.StringIO(conf))

    # general information
    cls.name = scp.get('info', 'name', raw=True)
    cls.__doc__ = scp.get('info', 'description', raw=True)
    if scp.has_option('info', 'version'):
        cls.version = scp.get('info', 'version', raw=True)
    else:
        cls.version = '0.0'
    try:
        cls.instancename = scp.get('info', 'instancename', raw=True)
    except:
        cls.instancename = cls.name
    cls.environVars = findEnvironmentVars(cls.instancename)
    cls.isLocal = len(cls.environVars) > 0

    # startup
    platform_cmdline_option = 'cmdline_{}'.format(sys.platform)
    if scp.has_option('startup', platform_cmdline_option):
        # use platform-specific command line
        cls.cmdline = scp.get('startup', platform_cmdline_option, raw=True)
    else:
        # use generic command line
        cls.cmdline = scp.get('startup', 'cmdline', raw=True)
    cls.path = path
    cls.filename = filename
    try:
        cls.timeout = float(scp.getint('startup', 'timeout'))
    except:
        pass

    # shutdown
    if scp.has_option('shutdown', 'message'):
        cls.shutdownMode = 'message', int(scp.get('shutdown', 'message', raw=True))
    elif scp.has_option('shutdown', 'setting'):
        cls.shutdownMode = 'setting', scp.get('shutdown', 'setting', raw=True)
    try:
        cls.shutdownTimeout = float(scp.getint('shutdown', 'timeout'))
    except:
        pass

    return cls


def version_tuple(version):
    """Get a tuple from a version string that can be used for comparison.

    Version strings are typically of the form A.B.C-X where A, B and C
    are numbers, and X is extra text denoting dev status (e.g. alpha or beta).
    Given this structure, we cannot just use string comparison to get the order
    of versions; instead we parse the version into a tuple

    ((int(A), int(B), int(C)), version)

    If we cannot parse the numeric part, we just use the empty tuple for the
    first entry, and for such tuples the comparison will just fall back to
    alphabetic comparison on the full versions string.
    """
    numstr, _, _extra = version.partition('-')
    try:
        nums = tuple(int(n) for n in numstr.split('.'))
    except Exception:
        nums = ()
    return (nums, version)


class Node(object):
    """Parent class that keeps the node running.

    If the manager is stopped or we lose the network connection,
    this service attempts to restart it so that we will come
    back online when the manager is back up.
    """
    reconnectDelay = 10

    def __init__(self, nodename, host, port, password, tls_mode=C.MANAGER_TLS):
        self.nodename = nodename
        self.host = host
        self.port = port
        self.password = password
        self.tls_mode = tls_mode

    @inlineCallbacks
    def run(self):
        """Run the node in a loop, reconnecting after connection loss."""
        log = logging.getLogger('labrad.node')
        while True:
            print 'Connecting to {}:{}...'.format(self.host, self.port)
            try:
                p = yield protocol.connect(self.host, self.port, self.tls_mode)
                yield p.authenticate(self.password)
                node = NodeServer(self.nodename, self.host, self.port,
                                  self.password)
                yield node.startup(p)
            except Exception:
                log.error('Node failed to start', exc_info=True)
            else:
                try:
                    yield node.onShutdown()
                except Exception:
                    log.error('Error during node shutdown', exc_info=True)

            ## hack: manually clear the internal message dispatcher
            dispatcher.connections.clear()
            dispatcher.senders.clear()
            dispatcher._boundMethods.clear()

            yield util.wakeupCall(0)
            print 'Will try to reconnect in {} seconds...'.format(self.reconnectDelay)
            yield util.wakeupCall(self.reconnectDelay)


class NodeConfig(object):
    """Load configuration from the registry and monitor it for changes.

    Attributes:
        dirs (list(string)): a list of directories that will be searched for
            runnable servers.
        exts (list(string)): a list of file extensions that will be included
            when searching for servers.
        autostart (list(string)): a list of servers that will be automatically
            started when the node launches.
    """

    @classmethod
    @inlineCallbacks
    def create(cls, parent):
        """Loads node configuration from the registry."""
        instance = cls(parent)
        yield instance._init()
        returnValue(instance)

    def __init__(self, parent):
        self.parent = parent
        self.nodename = parent.nodename
        cxn = parent.client
        self._cxn = cxn
        self._reg = cxn.registry
        self._ctx = cxn.context()

    @inlineCallbacks
    def _init(self):
        """Initialize by loading from the registry.

        Copy from the default directory, creating it if necessary.
        Also, set up messages to monitor the config directory for
        changes.
        """
        p = self._packet()
        p.cd(['', 'Nodes'], True)
        p.dir()
        ans = yield p.send()
        dirs, keys = ans.dir

        # load defaults (creating them if necessary)
        create = '__default__' not in dirs
        defaults = ([], ['.ini', '.py'], [])
        defaults = yield self._load('__default__', create, defaults)

        # load this node (creating config if necessary)
        create = self.nodename not in dirs
        config = yield self._load(self.nodename, create, defaults)
        self._update(config, False)

        # setup messages when registry changes
        self._reg.addListener(self._handleMessage, context=self._ctx)
        p = self._packet()
        p.notify_on_change(2345, True)
        yield p.send()

    def _packet(self):
        """Create a packet to the registry server in our context."""
        return self._reg.packet(context=self._ctx)

    def _update(self, config, triggerRefresh=True):
        """Update instance variables from loaded config."""
        self.dirs, self.extensions, self.autostart = config
        print 'config updated: dirs={}, extensions={}, autostart={}'.format(
                self.dirs, self.extensions, self.autostart)
        if triggerRefresh:
            self.parent.refreshServers()

    @inlineCallbacks
    def _load(self, nodename=None, create=False, defaults=None):
        """Load the current configuration out of the registry."""
        p = self._packet()
        if nodename is not None:
            p.cd(['', 'Nodes', nodename], True)
        if create:
            p.set('directories', defaults[0])
            p.set('extensions', defaults[1])
            p.set('autostart', defaults[2])
        p.get('directories', '*s', key='dirs')
        p.get('extensions', '*s', key='exts')
        p.get('autostart', '*s', True, [], key='autostart')
        ans = yield p.send()
        def remove_empties(strs):
            return [s for s in strs if s]
        dirs = remove_empties(ans.dirs)
        exts = remove_empties(ans.exts)
        autostart = sorted(remove_empties(ans.autostart))
        returnValue((dirs, exts, autostart))

    def _save(self):
        """Save the current configuration to the registry."""
        p = self._packet()
        p.set('directories', self.dirs)
        p.set('extensions', self.extensions)
        return p.send()

    @inlineCallbacks
    def _handleMessage(self, c, msg):
        """Reload when we get a message from the registry."""
        try:
            config = yield self._load()
            self._update(config)
        except Exception:
            logging.error('Error in _handleMessage', exc_info=True)

    @inlineCallbacks
    def update_autostart(self, autostart):
        """Update the list of servers to be autostarted.

        Args:
            autostart (list(string)): New list of autostart server names. This
                will completely replace the current list.
        """
        p = self._packet()
        p.cd(['', 'Nodes', self.nodename])
        p.set('autostart', sorted(autostart))
        yield p.send()


class NodeServer(LabradServer):
    """Start and stop LabRAD servers remotely.

    The node server allows you to control and
    monitor servers running on a remote machine.
    """

    name = 'node %LABRADNODE%'

    def __init__(self, nodename, host, port, password):
        LabradServer.__init__(self)
        self.nodename = nodename
        self.name = 'node %s' % nodename
        self.host = host
        self.port = port
        self.password = password
        self.servers = {}
        self.instances = {}
        self.starters = {}
        self.runners = {}
        self.stoppers = {}
        self.initMessages(True)

    @inlineCallbacks
    def initServer(self):
        """Initialize this server."""
        self.config = yield NodeConfig.create(self)
        self.refreshServers()
        self.autostart(None)

    def stopServer(self):
        """Stop this node by killing all subprocesses."""
        self.initMessages(False)
        stoppages = [srv.stop() for srv in self.runners.values()]
        return defer.DeferredList(stoppages)


    # message handling

    def initMessages(self, connect=True):
        """Set up message dispatching."""
        attr = 'connect' if connect else 'disconnect'
        method = getattr(dispatcher, attr)
        def f(receiver, signal):
            try:
                method(receiver, signal)
            except dispatcher.DispatcherError as e:
                msg = 'Error while setting up message dispatching. receiver={0}, method={1}, signal={2}.'
                print msg.format(receiver, attr, signal), e
        # set up messages to be relayed out over LabRAD
        messages = ['server_starting', 'server_started',
                    'server_stopping', 'server_stopped',
                    'status']
        for message in messages:
            f(self._relayMessage, message)
        # set up message handlers for subprocess events
        f(self.subprocessStarting, 'server_starting')
        f(self.subprocessStarted, 'server_started')
        f(self.subprocessStopping, 'server_stopping')
        f(self.subprocessStopped, 'server_stopped')

    def _relayMessage(self, signal, sender, **kw):
        """Send messages out to LabRAD."""
        kw['node'] = self.name
        mgr = self.client.manager
        mgr.send_named_message('node.' + signal, tuple(kw.items()))

    def serverConnected(self, ID, name):
        """Called when a server connects to LabRAD."""
        dispatcher.send('serverConnected', ID=ID, name=name)

    def subprocessStarting(self, sender):
        """Called when a subprocess begins connecting."""
        self.starters[sender.name] = sender

    def subprocessStarted(self, sender):
        """Called when a subprocess successfully connects."""
        if sender.name in self.starters:
            del self.starters[sender.name]
        self.runners[sender.name] = sender

    def subprocessStopping(self, sender):
        """Called when a subprocess successfully disconnects."""
        if sender.name in self.runners:
            del self.runners[sender.name]
        self.stoppers[sender.name] = sender

    def subprocessStopped(self, sender):
        """Called when a subprocess successfully disconnects."""
        if sender.name in self.runners:
            del self.runners[sender.name]
        if sender.name in self.stoppers:
            del self.stoppers[sender.name]


    # status information

    def status(self):
        """Get information about all servers on this node."""
        def serverInfo(cls):
            instances = [n for n, s in self.runners.items()
                                    if s.__class__.name == cls.name]
            return (cls.name, cls.__doc__ or '', cls.version,
                    cls.instancename, cls.environVars, instances)
        return [serverInfo(item[1])
                for item in sorted(self.servers.items())]


    # server refresh

    def refreshServers(self):
        """Refresh the list of available servers."""
        # configs is a nested map from name to version to list of classes.
        #
        # This allows us to deal with cases where there are many definitions
        # for different server versions, and possibly also redundant defitions
        # for the same version.
        configs = {}

        # look for .ini files
        for dirname in self.config.dirs:
            for path, dirs, files in os.walk(dirname):
                if '.nodeignore' in files:
                    del dirs[:] # clear dirs list so we don't visit subdirs
                    continue
                for f in files:
                    try:
                        _, ext = os.path.splitext(f)
                        if ext.lower() not in self.config.extensions:
                            continue
                        if ext.lower() == '.ini':
                            with open(os.path.join(path, f)) as file:
                                conf = file.read()
                        elif ext.lower() in ['.war', '.jar']:
                            zf = zipfile.ZipFile(os.path.join(path, f))
                            found = False
                            for info in zf.infolist():
                                if 'node.ini' in info.filename:
                                    found = True
                                    member = zf.open(info.filename)
                                    conf = member.read()
                                    member.close()
                                    break
                            zf.close()
                        else:
                            conf = findConfigBlock(path, f)
                            if conf is None:
                                continue
                        s = createGenericServerCls(path, f, conf)
                        s.client = self.client
                        if s.name not in configs:
                            configs[s.name] = {}
                        versions = configs.setdefault(s.name, {})
                        classes = versions.setdefault(s.version, [])
                        classes.append(s)
                    except Exception:
                        fname = os.path.join(path, f)
                        logging.error('Error while loading config file "%s":' % fname,
                                  exc_info=True)

        servers_dict = {}
        for versions in configs.values():
            for servers in versions.values():
                if len(servers) > 1:
                    conflicting_files = [s.filename for s in servers]
                    s = servers[0]
                    logging.warning(
                        'Found redundant server configs with same name and '
                        'version; will use {}. name={}, version={}, '
                        'conflicting_files={}'
                        .format(s.filename, s.name, s.version,
                                conflicting_files))

            servers = [ss[0] for ss in versions.values()]
            servers.sort(key=lambda s: version_tuple(s.version))
            if len(servers) > 1:
                # modify server name for all but the latest version
                for s in servers[:-1]:
                    s.name = '{}-{}'.format(s.name, s.version)

            for s in servers:
                servers_dict[s.name] = s
        self.servers = servers_dict
        # send a message with the current server list
        dispatcher.send('status', servers=self.status())


    # LabRAD settings

    @setting(1, name='s', environ='*(ss)', returns='s')
    def start(self, c, name, environ={}):
        """Start an instance of a server."""
        if name not in self.servers:
            raise Exception("Unknown server: '%s'." % name)
        environ = dict(environ) # copy context environment
        environ.update(LABRADNODE=self.nodename,
                       LABRADHOST=self.host,
                       LABRADPORT=str(self.port),
                       LABRADPASSWORD=self.password,
                       PYTHON=sys.executable)
        srv = self.servers[name](environ)
        # TODO check whether an instance with this name already exists
        self.instances[name] = srv
        yield srv.start()
        returnValue(srv.name)

    @setting(2, name='s', returns='s')
    def stop(self, c, name):
        """Stop a running server instance."""
        if name not in self.runners:
            raise Exception("'%s' is not running." % name)
        srv = self.runners[name]
        yield srv.stop()
        returnValue(srv.name)

    @setting(3, name='s', returns='s')
    def restart(self, c, name):
        """Restart a running server instance."""
        if name not in self.runners:
            raise Exception("'%s' is not running." % name)
        srv = self.runners[name]
        yield srv.restart()
        returnValue(srv.name)

    @setting(10, returns='*s')
    def available_servers(self, c):
        """Get a list of available servers."""
        return sorted(self.servers.keys())

    @setting(11, returns='*(ss)')
    def running_servers(self, c):
        """Get a list of running server instances.

        Returns a list of tuples of server name and instance name.
        """
        return sorted((s.__class__.name, n) for n, s in self.runners.items())

    @setting(12, returns='*s')
    def local_servers(self, c):
        """Get a list of local servers."""
        return sorted(n for n, s in self.servers.items() if s.isLocal)

    @setting(13, returns='')
    def refresh_servers(self, c):
        """Refresh the list of available servers."""
        yield self.refreshServers()

    @setting(14, 'status',
             returns='*(s{name} s{desc} s{ver} s{instname} *s{vars} *s{running})')
    def get_status(self, c):
        """Get information about all servers on this node."""
        return self.status()

    @setting(100, name='s', returns='*(ts)')
    def server_output(self, c, name):
        """Get output from a server's stdout."""
        if name not in self.runners:
            raise Exception("'%s' is not running." % name)
        return self.runners[name].output

    @setting(101, name='s', returns='')
    def clear_output(self, c, name):
        """Clear the stdout buffer of a server."""
        if name not in self.runners:
            raise Exception("'%s' is not running." % name)
        self.runners[name].clearOutput()

    @setting(102, name='s', returns='s')
    def server_version(self, c, name):
        """Get version information for a server."""
        if name not in self.servers:
            raise Exception("'%s' not found." % name)
        return self.servers[name].version

    @setting(103, name='s', enable='b', returns='')
    def stream_output(self, c, name, enable):
        """Enable or disable server output messages.

        This allows you to receive messages whenever a server
        outputs something on its stdout, effectively giving a
        remote view of the server's console window.
        """
        pass

    @setting(200, returns='')
    def autostart(self, c):
        """Start all servers from the configured autostart list.

        Any servers that are already running will be left as is, while those
        that are not yet running will be started. Autostart is triggered when
        the node first starts up, but can be invoked manually at any time
        thereafter.
        """
        running = set(s.__class__.name for s in self.runners.values())
        to_start = [name for name in self.config.autostart
                         if name not in running]
        deferreds = [(name, self.start(c, name)) for name in to_start]
        for name, deferred in deferreds:
            try:
                yield deferred
            except Exception:
                logging.error('Failed to autostart "%s"', name, exc_info=True)

    @setting(201, returns='*s')
    def autostart_list(self, c):
        """Get the list of servers that are configured to be autostarted."""
        return self.config.autostart

    @setting(202, name='s', returns='')
    def autostart_add(self, c, name):
        """Add a server to the autostart list."""
        if name not in self.servers:
            raise Exception("Unknown server: '%s'." % name)
        autostart = set(self.config.autostart)
        autostart.add(name)
        yield self.config.update_autostart(sorted(autostart))

    @setting(203, name='s', returns='')
    def autostart_remove(self, c, name):
        """Remove a server from the autostart list."""
        autostart = set(self.config.autostart)
        try:
            autostart.remove(name)
        except KeyError:
            pass
        yield self.config.update_autostart(sorted(autostart))

    @setting(1000, returns='*(ss)')
    def node_version(self, c):
        """Return a list of key-value tuples containing info about this node."""
        info = {
            'hostname': socket.gethostname(),
            'nodename': self.nodename,
            'python version': sys.version,
            'labrad version': labrad.__version__,
            'labrad revision': labrad.__revision__,
            'labrad date': labrad.__date__,
            }
        return list(info.items())


class NodeOptions(usage.Options):
    optParameters = [
            ['name', 'n', util.getNodeName(), 'Node name.'],
            ['port', 'p', C.MANAGER_PORT, 'Manager port.'],
            ['host', 'h', C.MANAGER_HOST, 'Manager location.'],
            ['tls', '', C.MANAGER_TLS,
             'TLS mode for connecting to manager (on/starttls/off)'],
            ['logfile', 'l', None, 'Enable logging to a file'],
            ['syslog_socket', 'x', None,
             'Override default syslog socket. Absolute path or host[:port]']]
    optFlags = [['syslog', 's', 'Enable syslog'],
                ['verbose', 'v', 'Enable debug output']]


def makeService(options):
    """Construct a TCPServer from a LabRAD node."""
    name = options['name']
    host = options['host']
    port = int(options['port'])
    password = labrad.support.get_password(host, port)
    tls_mode = C.check_tls_mode(options['tls'])
    return Node(name, host, port, password, tls_mode)


def setup_logging(options):
    logging.basicConfig()
    node_log = logging.getLogger('labrad')
    if options['syslog']:
        # We need to find the path to the system log socket, which varies by
        # platform. Linux and OS/X defaults are listed below. On windows the
        # only option is UDP logging, but since UDP is connectionless there is
        # no way to tell if there is actually a syslog daemon listening.
        # https://docs.python.org/2/library/logging.handlers.html#sysloghandler
        if options['syslog_socket']:
            if '/' in options['syslog_socket']:
                address = options['syslog_socket']
            else:
                host, _, port = options['syslog_socket'].partition(':')
                if port == '':
                    address = (host, 514)
                else:
                    address = (host, int(port))
        elif sys.platform.startswith('linux'):
            address = '/dev/log'
        elif sys.platform.startswith('darwin'):
            address = '/var/run/syslog'
        else:
            node_log.critical(
                    'Syslog specified, but default socket not known for '
                    'platform {}. Use -s option'.format(sys.platform))
            sys.exit(1)
        syslog_handler = logging.handlers.SysLogHandler(address=address)
        syslog_handler.setFormatter(logging.Formatter('%(name)s: %(message)s'))
        node_log.addHandler(syslog_handler)
    if options['logfile']:
        file_handler = logging.handlers.RotatingFileHandler(
                options['logfile'], maxBytes=800000, backupCount=5)
        formatter = logging.Formatter('%(asctime)s - %(name)s: %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        node_log.addHandler(file_handler)
    if options['verbose']:
        node_log.setLevel(logging.DEBUG)
    else:
        node_log.setLevel(logging.INFO)

def main():
    config = NodeOptions()
    config.parseOptions()
    setup_logging(config)
    logging.getLogger('labrad.node').info('Starting')
    service = makeService(config)
    service.run()
    reactor.run()

if __name__ == '__main__':
    main()