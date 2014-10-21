# -*- coding: utf-8 -*-

import random

class Memory() :
  def __init__(self) :
    self.memory = None
    self.mode = "word"

    self.resetByZero()

  def setMode(self, mode) :
    assert mode == 'byte' or mode == 'word', 'mode must be "byte" or "word"'
    self.mode = mode

  def __setitem__(self, index, value) :
    if isinstance(index, slice) :
      if isinstance(index.stop, str) :
        mode = self.mode
        self.setMode(index.stop)
        self[index.start] = value
        self.setMode(mode)
      else :
        self.memory.__setitem__(index, value)
    else :
      if self.mode == 'byte' :
        self.memory[index&0xffff] = value&0xff
      elif self.mode == 'word' :
        self.memory[index&0xffff] = value&0xff
        self.memory[(index+1)&0xffff] = (value>>8)&0xff
      else :
        raise AssertionError('mode must be "byte" or "word"')

  def __getitem__(self, index) :
    if isinstance(index, slice) :
      if isinstance(index.stop, str) :
        mode = self.mode
        self.setMode(index.stop)
        value = self[index.start]
        self.setMode(mode)
        return value
      else :
        return self.memory.__getitem__(index)
    else :
      if self.mode == 'byte' :
        return self.memory[index&0xffff]
      elif self.mode == 'word' :
        return (self.memory[(index+1)&0xffff]<<8)+self.memory[index&0xffff]
      else :
        raise AssertionError('mode must be "byte" or "word"')

  def load(self, data, point=0) :
    self.memory[point:point+len(data)] = data

  def resetByRandom(self) :
    self.memory = [ random.randint(0, 255) for x in range(65536) ]

  def resetByZero(self) :
    self.memory = [ 0 for x in range(65536) ]

