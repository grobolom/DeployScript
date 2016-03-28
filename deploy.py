#!/usr/bin/env python

import os
import re
import logging
import optparse
import subprocess

class Deployer:
    def main(self):
        CheckUncommitted().run()
        PullUpstream().run()
        PushToUpstream().run()
        print 'done.'

# abstract class
class Command:
    def call_command(self, command):
        # need shell=True for multiple commands (like running phpunit tests)
        process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                cwd='/home/vasja/web')
        output,_ = process.communicate()
        return output;

    def run(self):
        output = self.call_command(self.command)
        valid = self.expectedOutput(output)
        if not valid:
            print output
            raise Exception(self.name + ' failed!')

class PushToUpstream(Command):
    name = 'Push Changes To Production'
    command = 'hg push -r main'
    def expectedOutput(self, output):
        push_result = output.split('\n')[-2]
        no_changes = 'no changes found' in push_result
        pushed_some_changes = 'remote: added ' in push_result
        return (no_changes or pushed_some_changes)

class CheckUncommitted(Command):
    name = 'Check For Uncommitted Files'
    command = 'hg status -mard'
    def expectedOutput(self, output):
        return len(output) <= 0

class PullUpstream(Command):
    name = 'Pull Files From Upstream'
    command = 'hg pull --rebase; echo $?'
    def expectedOutput(self, output):
        return output.split('\n')[-2] != 0


####################
####### RUN ########
####################

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s')

if __name__ == "__main__":
    deployer = Deployer()
    deployer.main()