#!/bin/env python
# github.com/blindly
# 5/29/2022
import os
import sys
import commands
import argparse

from os.path import dirname, abspath, exists

def cmd(cmd):
    cmd = cmd.split()
    code = os.spawnvpe(os.P_WAIT, cmd[0], cmd, os.environ)
    if code == 127:
        sys.stderr.write('{0}: command not found\n'.format(cmd[0]))
    return code

def init():
    if not exists('%s/.requirements.env'):
        commands.getoutput('touch .requirements.env')

def find_requirement(variable):
    command = "grep %s .requirements.env | tr '=' ' ' | awk '{ print $2 }'" % variable
    return commands.getoutput( command )

def start():

    init()
    
    port_var = find_requirement('PORT')
    if not port_var:
        port_var = args.port

    print "Port is %s" % port_var

    command = 'podman run -d -it --name %s -v %s:/app -p %s %s %s' % ( name, cwd, port_var, args.image, args.command )
    if args.verbose:
        print command
    print commands.getoutput( command )

    node_needed = commands.getoutput("grep node_modules %s" % cwd)
    if node_needed:
        update = "podman exec -it %s bash -c 'apt update -y && apt install curl -y && curl https://get.volta.sh | bash'" % name
        if args.verbose:
                print update
        print commands.getoutput(update)

        node_version = find_requirement('NODE_VERSION')
        if not node_version:
            node_version = 14

        print "Node version is %s" % node_version

        install = "podman exec -it %s bash -c '/root/.volta/bin/volta install node@%s'" % (name, node_version)
        if args.verbose:
                print install
        print commands.getoutput(install)

def stop():
    command = "podman stop %s && podman rm %s" % ( name, name )    
    if args.verbose:
        print command
    commands.getoutput( command )

def status():
    command = "podman ps --noheading"
    if args.verbose:
        print command
    print commands.getoutput( command )

def run():
    running_port_command = "podman ps|grep %s|sed 's/.*0.0.0.0://g'|sed 's/->.*//g'" % name

    if args.verbose:
        print running_port_command
    
    running_port = commands.getoutput( running_port_command )
    
    if (running_port):
        print "Exposed port at http://localhost:%s" % running_port

    command = "podman exec -it %s bash" % ( name )
    
    if args.verbose:
        print command
    
    cmd( command )

def clean():
    running_clean_command = "podman system prune -a -f"
    if args.verbose:
        print running_clean_command
    cmd( running_clean_command )

try:
    parser = argparse.ArgumentParser(description='podman helper')
    # parser.add_argument('-action', help='Action', default="status", required=False)
    parser.add_argument('action', help='Action', default="status")
    parser.add_argument('-port', help='Container Port', default="3000", required=False)
    parser.add_argument('-image',  help='Container Image', default="ubuntu", required=False)
    parser.add_argument('-command',  help='Command to Run', default="bash", required=False)
    parser.add_argument('--verbose', '-v', action='count', default=0)
    args = parser.parse_args()

    name = commands.getoutput('basename `pwd`')
    cwd = commands.getoutput('pwd')

    # print args.action
    # sys.exit()

    if args.action == "start":
        start()
        run()
    
    elif args.action == "stop":
        stop()
    
    elif args.action == "status":
        status()
    
    elif args.action == "run":
        run()
    
    elif args.action == "clean":
        clean()
    
    else:
        print "Action not found"

except KeyboardInterrupt:
    print "You pressed Ctrl+C"
    sys.exit()
except Exception, e:
    print e
