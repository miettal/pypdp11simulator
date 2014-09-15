#!/usr/bin/env python
# coding:utf-8
#
# test_vm.py
#
# Author:   Hiromasa Ihara (miettal)
# URL:      http://miettal.com
# License:  MIT License
# Created:  2014-09-13
#

import sys
import os
import StringIO
import traceback

import pdp11_vm
from subprocess import *

def test(args) :
  vm = pdp11_vm.VM()
  vm.debug = StringIO.StringIO()
  vm.load(args, open(os.devnull), open(os.devnull, 'w'), open(os.devnull, 'w'))

  flag = False
  try :
    vm.run()
  except :
    pass

  myvm_output = vm.debug.getvalue()

  p = Popen(["7run", "-m"] + args, stdout=PIPE, stderr=PIPE)
  nanarun_output = p.communicate()[1]

  output = ""
  for (myvm_line, nanaran_line) in zip(myvm_output.split('\n'), nanarun_output.split('\n')) :
    myvm_line= myvm_line.strip()
    nanaran_line  = nanaran_line.strip()

    output += " "+nanaran_line+"\n"
    if myvm_line != nanaran_line:
      output += "-"+myvm_line+"\n"
      flag = True

  print ' '.join(args)+"...",
  if flag :
    print "failed"
    print output
  else :
    print "success"

if __name__ == '__main__':
  test_cfiles = [
    {'src':'test1.c', 'args':[],},
    {'src':'test2.c', 'args':[],},
    {'src':'test3.c', 'args':[],},
    {'src':'test4.c', 'args':[],},
    {'src':'test4.c', 'args':['arg1', ],},
    {'src':'test4.c', 'args':['arg1', 'arg2', ],},
    {'src':'test4.c', 'args':['arg1', 'arg2', 'arg3'],},
    {'src':'test6.c', 'args':[],},
  ]

  for x in test_cfiles :
    bin_filename = x['src'].split('.')[0]
    Popen(['v6cc', x['src']]).wait()
    Popen(['mv', 'a.out', bin_filename]).wait()
    test([bin_filename]+x['args'])

  #test(['/usr/local/v6root/bin/nm', 'test1'])
  test(['/usr/local/v6root/bin/as', 'write.s'])

  sys.exit(0)

