#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2009-2010 Rosen Diankov (rosen.diankov@gmail.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import with_statement # for python 2.5
__author__ = 'Rosen Diankov'
__copyright__ = 'Copyright (C) 2009-2010 Rosen Diankov (rosen.diankov@gmail.com)'
__license__ = 'Apache License, Version 2.0'

import sys,time
try:
    from openravepy import *
except ImportError:
    print "openravepy is not set into PYTHONPATH env variable, attempting to add"
    # use openrave-config to get the correct install path
    from subprocess import Popen, PIPE
    try:
        openravepy_path = Popen(['openrave-config','--python-dir'],stdout=PIPE).communicate()
        sys.path.append(openravepy_path[0].strip())
    except OSError:
        import platform
        if sys.platform.startswith('win') or platform.system().lower() == 'windows':
            # in windows so add the default openravepy installation
            sys.path.append("C:\\Program Files\\openrave\\share\\openrave")
    from openravepy import *

from types import ModuleType
from numpy import *
from optparse import OptionParser

def vararg_callback(option, opt_str, value, parser):
    assert value is None
    value = parser.rargs[:]
    del parser.rargs[:len(value)]
    setattr(parser.values, option.dest, value)

if __name__ == "__main__":
    parser = OptionParser(description='OpenRAVE %s'%openravepy.__version__,version=openravepy.__version__,
                          usage='%prog [options] [loadable openrave xml/robot files...]')
    OpenRAVEGlobalArguments.addOptions(parser)
    parser.add_option('--database', action="callback",callback=vararg_callback, dest='database',default=None,
                      help='If specified, the next arguments will be used to call a database generator from the openravepy.databases module. The first argument is used to find the database module. For example:     %s --database grasping --robot=robots/pr2-beta-sim.robot.xml'%(sys.argv[0]))
    parser.add_option('--example', action="callback",callback=vararg_callback, dest='example',default=None,
                      help='If specified, the next arguments will be used to call an example from the openravepy.examples module. The first argument is used to find the example moduel. For example:     %s --example graspplanning --scene=data/lab1.env.xml'%(sys.argv[0]))
    parser.add_option('--ipython', '-i',action="store_true",dest='ipython',default=False,
                      help='if true will drop into the ipython interpreter rather than spin')
    parser.add_option('--pythoncmd','-p',action='store',type='string',dest='pythoncmd',default=None,
                      help='Execute a python command after all loading is done and before the drop to interpreter check. The variables available to use are: "env","robots","robot". It is possible to quit the program after the command is executed by adding a "sys.exit(0)" at the end of the command.')
    parser.add_option('--listinterfaces', action="store",type='string',dest='listinterfaces',default=None,
                      help='List the provided interfaces of a particular type from all plugins. Possible values are: %s.'%(', '.join(type.name for type in InterfaceType.values.values())))
    parser.add_option('--listplugins', action="store_true",dest='listplugins',default=False,
                      help='List all plugins and the interfaces they provide.')
    parser.add_option('--listdatabases',action='store_true',dest='listdatabases',default=False,
                      help='Lists the available core database generators')
    parser.add_option('--listexamples',action='store_true',dest='listexamples',default=False,
                      help='Lists the available examples.')
    parser.add_option('--robotmanipulators',action='store_true',dest='robotmanipulators',default=False,
                      help='Lists the manipulator information of a single robot.')
    parser.add_option('--robotsensors',action='store_true',dest='robotsensors',default=False,
                      help='Lists the attached sensor information of a single robot.')
    (options, args) = parser.parse_args()
    if options.listdatabases:
        for name in dir(databases):
            if not name.startswith('__'):
                try:
                    m=__import__('openravepy.databases.'+name)
                    if type(m) is ModuleType:
                        print ' ' + name
                except ImportError:
                    pass
        sys.exit(0)
    if options.listexamples:
        for name in dir(examples):
            if not name.startswith('__'):
                try:
                    m=__import__('openravepy.examples.'+name)
                    if type(m) is ModuleType:
                        print ' ' + name
                except ImportError:
                    pass
        sys.exit(0)
    if options.database is not None:
        args = options.database[0].split() + options.database[1:] # the first arg might also include the options
        try:
            database=getattr(databases,args[0])
        except (AttributeError,IndexError):
            print 'bad database generator, current list of executable generators are:'
            for name in dir(databases):
                if not name.startswith('__'):
                    try:
                        m=__import__('openravepy.databases.'+name)
                        if type(m) is ModuleType:
                            print ' ' + name
                    except ImportError:
                        pass
            sys.exit(1)
        database.run(args=args)
        sys.exit(0)
    if options.example is not None:
        args = options.example[0].split() + options.example[1:] # the first arg might also include the options
        try:
            example = getattr(examples,args[0])
        except (AttributeError,IndexError):
            print 'bad example, current list of executable examples are:'
            for name in dir(examples):
                if not name.startswith('__'):
                    try:
                        m=__import__('openravepy.examples.'+name)
                        if type(m) is ModuleType:
                            print ' ' + name
                    except ImportError:
                        pass
            sys.exit(1)
        example.run(args=args)
        sys.exit(0)

    level = DebugLevel.Info
    if options.listinterfaces is not None or options.listplugins:
        level = DebugLevel.Error
    RaveInitialize(True,level=level)
    if options.listinterfaces is not None:
        interfaces = RaveGetLoadedInterfaces()
        for type,names in interfaces:
            if options.listinterfaces.lower() == str(type).lower():
                for name in names:
                    print name
                break
        sys.exit(0)
    if options.listplugins:
        plugins = RaveGetPluginInfo()
        interfacenames = dict()
        for type in InterfaceType.values.values():
            interfacenames[type] = []
        for pluginname,info in plugins:
            for type,names in info.interfacenames:
                interfacenames[type] += [(n,pluginname) for n in names]
        print 'Number of plugins: %d'%len(plugins)
        for type,names in interfacenames.iteritems():
            print '%s: %d'%(str(type),len(names))
            names.sort()
            for interfacename,pluginname in names:
                print '  %s - %s'%(interfacename,pluginname)
        sys.exit(0)
    env = OpenRAVEGlobalArguments.parseAndCreate(options,defaultviewer=False)
    try:
        # load files after viewer is loaded since they may contain information about where to place the camera
        for arg in args:
            if arg.endswith('.xml') or arg.endswith('.dae') or arg.endswith('.zae'):
                env.Load(arg)
        with env:
            robots=env.GetRobots()
            robot=None if len(robots) == 0 else robots[0]
            if options.robotmanipulators:
                rows = [['name','base','end','arm-dof','gripper-dof','arm','gripper']]
                for m in robot.GetManipulators():
                    armindices = ','.join(str(i) for i in m.GetArmIndices())
                    gripperindices = ','.join(str(i) for i in m.GetGripperIndices())
                    rows.append([m.GetName(),m.GetBase().GetName(),m.GetEndEffector().GetName(),str(len(m.GetArmIndices())),str(len(m.GetGripperIndices())),armindices,gripperindices])
                colwidths = [max([len(row[i]) for row in rows]) for i in range(len(rows[0]))]
                for i,row in enumerate(rows):
                    print ' '.join([row[j].ljust(colwidths[j]) for j in range(len(colwidths))])
                    if i == 0:
                        print '-'*(sum(colwidths)+len(colwidths)-1)
                sys.exit(0)
            if options.robotsensors:
                rows = [['name','type','link']]
                for s in robot.GetAttachedSensors():
                    rows.append([s.GetName(),str(s.GetSensor()),s.GetAttachingLink().GetName()])
                colwidths = [max([len(row[i]) for row in rows]) for i in range(len(rows[0]))]
                for i,row in enumerate(rows):
                    print ' '.join([row[j].ljust(colwidths[j]) for j in range(len(colwidths))])
                    if i == 0:
                        print '-'*(sum(colwidths)+len(colwidths)-1)
                sys.exit(0)
        if options.pythoncmd is not None:
            eval(compile(options.pythoncmd,'<string>','exec'))
        if options._viewer is None:
            env.SetViewer('qtcoin')
        if options.ipython:
            from IPython.Shell import IPShellEmbed
            ipshell = IPShellEmbed(argv='',banner = 'OpenRAVE Dropping into IPython, variables: env, robot',exit_msg = 'Leaving Interpreter and closing program.')
            ipshell(local_ns=locals())
            sys.exit(0)
        while True:
            time.sleep(1.0)
    finally:
        env.Destroy()
        RaveDestroy()