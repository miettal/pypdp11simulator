# -*- coding: utf-8 -*-

class Register() :
  def __init__(self) :
    self.register = [ 0 for x in range(8) ]
    self.n = False
    self.z = False
    self.v = False
    self.c = False
    self.mode = "word"

  def setMode(self, mode) :
    assert mode == 'byte' or mode == 'word' or mode == 'dword', 'mode must be "byte" or "word", "dword"'
    self.mode = mode

  def __setitem__(self, index, value) :
    if self.mode == 'byte' :
      if value > 0x7f :
        self.register[index] = 0xff00 | (value & 0xff)
      else :
        self.register[index] = value & 0xff
    elif self.mode == 'word' :
      self.register[index] = value & 0xffff
    elif self.mode == 'dword' :
      self.register[index] = (value >> 16) & 0xffff
      self.register[index+1] = value & 0xffff
    else :
      raise AssertionError('mode must be "byte" or "word", "dword"')

  def __getitem__(self, index) :
    if self.mode == 'byte' :
      return self.register[index]
    elif self.mode == 'word' :
      return self.register[index]
    if self.mode == 'dword' :
      return self.register[index]<<16+self.register[index+1]
    else  :
      raise AssertionError('mode must be "byte" or "word", "dword"')

  def __repr__(self) :
    s = ""
    for x in range(8) :
      s += "R%1d:%04x,"%(x, self.register[x])
    s = s[:-1]

    return s

  def __str__(self) :
    return self.__repr__()
