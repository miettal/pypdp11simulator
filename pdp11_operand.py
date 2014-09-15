#!/usr/bin/env python
# coding:utf-8
#
# pdp11_operand.py
#
# Author:   Hiromasa Ihara (miettal)
# URL:      http://miettal.com
# License:  MIT License
# Created:  2014-09-15
#

class Operand() :
  def __init__(self, memory, registers) :
    self.memory = memory
    self.registers = registers
    self.addressing = ""
    self.address = 0
    self.operation_mode = ""
    self.value = 0
    self.memory_dump = ""

  def __call__(self, value=None, dword=False) :
    if value is None :
      self.registers.setMode(self.operation_mode)
      self.memory.setMode(self.operation_mode)
      if self.addressing == 'immidiate' :
        value = self.value
      elif self.addressing == 'register' :
        if dword and self.address%2 == 0:
          value = (self.registers[self.address]<<16)+self.registers[self.address+1]
        else :
          value = self.registers[self.address]
      elif ( self.addressing == 'register deferred' or
             self.addressing == 'autoincrement' or
             self.addressing == 'autoincrement deferred' or
             self.addressing == 'autodecrement' or
             self.addressing == 'autodecrement deferred' or
             self.addressing == 'index' or
             self.addressing == 'index deferred' or
             self.addressing == 'absolute' or
             self.addressing == 'relative' or
             self.addressing == 'relative indirect' ) :
        value = self.memory[self.address]
        if not self.memory_dump :
          if self.operation_mode == "byte" :
            self.memory_dump += " ;[{:04x}]{:02x}".format(self.address, self.memory[self.address])
          else :
            self.memory_dump += " ;[{:04x}]{:04x}".format(self.address, self.memory[self.address])
      else :
        raise

      self.registers.setMode("word")
      self.memory.setMode("word")

      return value
    else :
      self.registers.setMode(self.operation_mode)
      self.memory.setMode(self.operation_mode)
 
      if self.addressing == 'immidiate' :
        pass
      elif self.addressing == 'register' :
        self.registers[self.address] = value
        if dword and self.address%2 == 0:
          self.registers[self.address] = value>>16
          self.registers[self.address+1] = value
        else :
          self.registers[self.address] = value
      elif ( self.addressing == 'register deferred' or
             self.addressing == 'autoincrement' or
             self.addressing == 'autoincrement deferred' or
             self.addressing == 'autodecrement' or
             self.addressing == 'autodecrement deferred' or
             self.addressing == 'index' or
             self.addressing == 'index deferred' or
             self.addressing == 'absolute' or
             self.addressing == 'relative' or
             self.addressing == 'relative indirect' ) :
        if not self.memory_dump :
          if self.operation_mode == "byte" :
            self.memory_dump += " ;[{:04x}]{:02x}".format(self.address, self.memory[self.address])
          else :
            self.memory_dump += " ;[{:04x}]{:04x}".format(self.address, self.memory[self.address])
        self.memory[self.address] = value
      else :
        pass

      self.registers.setMode("word")
      self.memory.setMode("word")

  def addr(self) :
    addr = self.address
    if not self.memory_dump :
      self.memory_dump += " ;[{:04x}]{:04x}".format(self.address, self.memory[self.address])
    return addr

  def __iadd__(self, other) :
    self(self()+other)
    return self

  def __isub__(self, other) :
    self(self()-other)
    return self

