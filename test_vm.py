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
import glob
import traceback
import re

import six
if six.PY3 :
  from io import StringIO
else :
  from StringIO import StringIO

import pdp11_vm
from subprocess import *

def itersplit(s, sep=None):
  exp = re.compile(r'\s+' if sep is None else re.escape(sep))
  pos = 0
  while True:
    m = exp.search(s, pos)
    if not m:
      if pos < len(s) or sep is not None:
        yield s[pos:]
      break
    if pos < m.start() or sep is not None:
      yield s[pos:m.start()]
    pos = m.end()

def test(args) :
  vm = pdp11_vm.VM()
  vm.debug = StringIO()
  vm.load(args)

  flag = False
  try :
    #Popen(["rm", "-f", "a.out"]).wait()
    #Popen(["rm", "-f"] + glob.glob("/tmp/atm*")).wait()
    vm.run()
  except :
    pass
  finally:
    myvm_output = vm.debug.getvalue()

  myvm_output = vm.debug.getvalue()

  #Popen(["rm", "-f", "a.out"]).wait()
  #Popen(["rm", "-f"] + glob.glob("/tmp/atm*")).wait()
  p = Popen(["7run", "-m", "-r", "/usr/local/v6root"] + args, stdout=PIPE, stderr=PIPE)
  nanarun_output = p.communicate()[1].decode('ascii')

  if myvm_output != nanarun_output :
    output = ""
    for (myvm_line, nanarun_line) in zip(itersplit(myvm_output, '\n'), itersplit(nanarun_output, '\n')) :

      output += " "+nanarun_line+"\n"
      if myvm_line != nanarun_line:
        output += "-"+myvm_line+"\n"
        flag = True

  print((' '.join(args)+"...")+' ')
  if flag :
    print("failed")
    print(output)
  else :
    print("success")

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

  test(['/usr/local/v6root/bin/as', 'write-1.s'])
  #test(['/usr/local/v6root/bin/nm', 'a.out'])

  sys.exit(0)

