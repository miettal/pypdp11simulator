# -*- coding: utf-8 -*-

import random

class Registers() :
  def __init__(self) :
    self.registers = [ random.randint(0, 65535) for x in range(8) ]
    self.registers = [ 0 for x in range(8) ]
    self.mode = "word"

  def setMode(self, mode) :
    assert mode == 'byte' or mode == 'word', 'mode must be "byte" or "word"'
    self.mode = mode

  def __setitem__(self, index, value) :
    if self.mode == 'byte' :
      if value > 0x7f :
        self.registers[index] = 0xff00 | (value & 0xff)
      else :
        self.registers[index] = value & 0xff
    elif self.mode == 'word' :
      self.registers[index] = value & 0xffff
    else :
      raise AssertionError('mode must be "byte" or "word"')

  def __getitem__(self, index) :
    if self.mode == 'byte' :
      return self.registers[index] & 0xff
    elif self.mode == 'word' :
      return self.registers[index]
    else  :
      raise AssertionError('mode must be "byte" or "word"')

  def __repr__(self) :
    s = ""
    for x in range(8) :
      s += "R%1d:%04x,"%(x, self.registers[x])
    s = s[:-1]

    return s

  def __str__(self) :
    return self.__repr__()
