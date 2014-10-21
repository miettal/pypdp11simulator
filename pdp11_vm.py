# -*- coding: utf-8 -*-
import sys
import os
from pprint import pprint as pp

import six

import pdp11_aout
import pdp11_decode
import pdp11_disassem
import pdp11_registers
import pdp11_memory
import pdp11_operand
import pdp11_util

class SysExit(Exception):
    def __init__(self, value=''):
        self.value = value
    def __str__(self):
        return repr(self.value)

class VM :
  def __init__(self, debug=False) :
    self.aout = ""

    self.memory = pdp11_memory.Memory()
    self.registers = pdp11_registers.Registers()
    self.condition_code = {'n':False,
                           'z':False,
                           'v':False,
                           'c':False,
    }
    self.operation_mode = None

    self.dst = pdp11_operand.Operand(self.memory, self.registers)
    self.src = pdp11_operand.Operand(self.memory, self.registers)
    self.reg = pdp11_operand.Operand(self.memory, self.registers)

    # unixv6
    self.sighandler = 0

    # debug
    self.debug = debug
    self.symbol = ""
    self.state = ""
    self.disassemble = ""
    self.dst.memory_dump = ""
    self.src.memory_dump = ""
    self.reg.memory_dump = ""
    self.syscall = ""

  def push(self, value) :
    self.registers[6] -= 2
    self.memory[self.registers[6]] = value

  def pop(self) :
    value = self.memory[self.registers[6]]
    self.registers[6] += 2
    return value

  def sys(self, num) :
    if num == 0 : #indir
      pc = self.registers[7]
      disassemble = self.disassemble
      state = self.state

      self.registers[7] = self.memory[self.registers[7]]
      self.step()

      self.registers[7] = pc
      self.registers[7] += 2
      self.disassemble = disassemble
      self.state = state

    elif num == 1 : #exit
      info = pdp11_util.uint16toint16(self.registers[0])

      self.syscall = '<exit({:d})>'.format(info)

      raise SysExit()

    elif num == 2 : #fork
      self.syscall = "not implement(syscall {:x})".format(num)

    elif num == 3 : #read
      fd = self.registers[0]
      addr = self.memory[self.registers[7]]
      size = self.memory[self.registers[7]+2]
      data = list(os.read(fd, size))
      if six.PY2 : data = map(ord, data)

      self.memory[addr:addr+len(data)] = data
      self.registers[0] = len(data)
      self.registers[7] += 4
      self.condition_code['c'] = False

      self.syscall = '<read({:d}, 0x{:04x}, {:d}) => {:d}>'.format(fd, addr, size, self.registers[0])

    elif num == 4 : #write
      fd = self.registers[0]
      addr = self.memory[self.registers[7]]
      size = self.memory[self.registers[7]+2]

      os.write(fd, ''.join(map(chr, self.memory[addr:addr+size])))
      self.registers[0] = size
      self.registers[7] += 4
      self.condition_code['c'] = False

      self.syscall = '<write({:d}, 0x{:04x}, {:d}) => {:d}>'.format(fd, addr, size, self.registers[0])

    elif num == 5 : #open
      filepath = pdp11_util.addr2str(self.memory, self.memory[self.registers[7]])
      mode = self.memory[self.registers[7]+2]

      fd = os.open(pdp11_util.chpath(filepath), mode)
      self.registers[0] = fd
      self.registers[7] += 4

      self.syscall = '<open("{}", {}) => {}>'.format(filepath, mode, self.registers[0])

    elif num == 6 : #close
      fd = self.registers[0]

      os.close(fd)
      self.registers[0] = 0

      self.syscall = '<close({}) => {}>'.format(fd, 0)

    elif num == 7 :
      self.syscall = "not implement(syscall {:x})".format(num)

    elif num == 8 : #creat
      filepath = pdp11_util.addr2str(self.memory, self.memory[self.registers[7]])
      mode = self.memory[self.registers[7]+2]

      fd = os.open(pdp11_util.chpath(filepath),
        os.O_CREAT | os.O_TRUNC | os.O_WRONLY, mode)
      self.registers[0] = fd
      self.condition_code['c'] = False
      self.registers[7] += 4

      self.syscall = '<creat("{:s}", {:04o}) => {}>'.format(filepath, mode, fd)

    elif num == 9 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 10 : #unlink
      filepath = pdp11_util.addr2str(self.memory, self.memory[self.registers[7]])

      try :
        os.unlink(pdp11_util.chpath(filepath))
        result = 0
        self.registers[0] = 0
        self.condition_code['c'] = False
      except OSError :
        result = -1
        self.registers[0] = 2
        self.condition_code['c'] = True

      self.registers[7] += 2

      self.syscall = '<unlink("{:s}") => {}>'.format(filepath, result)

    elif num == 11 : #exec
      filepath = pdp11_util.addr2str(self.memory, self.memory[self.registers[7]])
      i = 0
      argp = self.memory[self.registers[7]+2]
      args = []
      while self.memory[argp+i*2] != 0:
        p = self.memory[argp+i*2]
        args.append(pdp11_util.addr2str(self.memory, p))
        i += 1

      self.sys_exec(args)

      self.syscall = '<exec("'
      self.syscall += '", "'.join(args)
      self.syscall += '") => {}>'.format(0)

    elif num == 12 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 13 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 14 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 15 :
      filepath = pdp11_util.addr2str(self.memory, self.memory[self.registers[7]])
      mode = self.memory[self.registers[7]+2]

      os.chmod(filepath, mode)
      self.registers[0] = 0
      self.registers[7] += 4

      self.syscall = '<chmod("{:s}", 0{:03o}) => {}>'.format(filepath, mode, 0)
    elif num == 16 :
      self.syscall = "not implement(syscall {:x})".format(num)

    elif num == 17 : #brk
      addr = self.memory[self.registers[7]]

      self.registers[0] = 0

      self.syscall = '<brk(0x{:04x}) => {}>'.format(addr, 0)
    elif num == 18 : #stat
      filepath = pdp11_util.addr2str(self.memory, self.memory[self.registers[7]])
      addr = self.memory[self.registers[7]+2]

      try :
        result = 0
        stat = os.stat(pdp11_util.chpath(filepath))
        self.registers[0] = result
        self.memory[addr:"word"] = stat.st_dev
        self.memory[addr+2:"word"] = stat.st_ino
        self.memory[addr+4:"word"] = stat.st_mode
        self.memory[addr+6:"byte"] = stat.st_nlink
        self.memory[addr+7:"byte"] = stat.st_uid
        self.memory[addr+8:"byte"] = stat.st_gid
        self.memory[addr+9:"byte"] = stat.st_size >> 16
        self.memory[addr+10:"word"] = stat.st_size
        self.memory[addr+28:"word"] = int(stat.st_atime) >> 16
        self.memory[addr+30:"word"] = int(stat.st_atime)
        self.memory[addr+32:"word"] = int(stat.st_mtime) >> 16
        self.memory[addr+34:"word"] = int(stat.st_mtime)
        self.registers[0] = 0
        self.condition_code['c'] = False
      except OSError:
        result = -1
        self.registers[0] = 2
        self.condition_code['c'] = True

      self.registers[7] += 4

      self.syscall = '<stat("{:s}", 0x{:04x}) => {}>'.format(filepath, addr, result)
    elif num == 19 : #lseek
      fd = self.registers[0]
      offset = self.memory[self.registers[7]]
      whence = self.memory[self.registers[7]+2]

      self.registers[0] = os.lseek(fd, offset, whence)
      self.registers[7] += 4
      self.condition_code['c'] = False

      self.syscall = '<lseek({}, {}, {}) => {}>'.format(fd, offset, whence, self.registers[0])

    elif num == 20 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 21 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 22 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 23 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 24 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 25 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 26 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 27 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 28 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 29 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 30 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 31 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 32 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 33 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 34 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 35 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 36 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 37 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 38 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 39 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 40 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 41 :
      fd = self.registers[0]

      fd = os.dup(fd)
      self.registers[0] = fd

      self.syscall = '<dup({}) => {}>'.format(fd, i)

    elif num == 42 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 43 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 44 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 45 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 46 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 47 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 48 :
      signum = self.memory[self.registers[7]]
      sighandler = self.memory[self.registers[7]+2]
      old_sighandler = self.sighandler
      self.sighandler = sighandler

      self.registers[7] += 4
      self.registers[0] = old_sighandler

      self.syscall = '<signal({}, 0x{:04x})>'.format(signum, sighandler)

    elif num == 49 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 50 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 51 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 52 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 53 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 54 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 55 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 56 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 57 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 58 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 59 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 60 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 61 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 62 :
      self.syscall = "not implement(syscall {:x})".format(num)
    elif num == 63 :
      self.syscall = "not implement(syscall {:x})".format(num)
    else :
      pass

  def step(self) :
    instruction = pdp11_decode.searchMatchInstructionFormat(self.memory, self.registers[7])

    self.symbol = ""
    self.state = ""
    self.disassemble = ""
    self.dst.memory_dump= ""
    self.src.memory_dump= ""
    self.reg.memory_dump= ""
    self.syscall = ""

    #symbol
    for (k, v) in list(self.aout['syms']['symbol_table'].items()) :
      if v['address'] == self.registers[7] and k[0] != '~' :
        self.symbol = k

    #state
    for i in range(7) :
      self.state += "{:04x} ".format(self.registers[i])

    if self.condition_code['z'] :
      self.state += "Z"
    else :
      self.state += "-"
    if self.condition_code['n'] :
      self.state += "N"
    else :
      self.state += "-"
    if self.condition_code['c'] :
      self.state += "C"
    else :
      self.state += "-"
    if self.condition_code['v'] :
      self.state += "V"
    else :
      self.state += "-"

    self.state += " {:04x}:".format(self.registers[7])

    #disassemble
    self.memory.setMode("byte")
    (mnemonic, next_ptr) = pdp11_disassem.getMnemonic(instruction, self.memory, self.registers[7])
    ptr = self.registers[7]
    self.memory.setMode("word")
    self.disassemble = ""
    for i in range(3) :
      if ptr + i*2 < next_ptr :
        self.disassemble += "{:04x} ".format(self.memory[ptr+i*2])
      else :
        self.disassemble += "     "
    self.disassemble += mnemonic

    if instruction :
      self.registers[7] += instruction['size']

      self.operation_mode = "word"
      if '*' in instruction['operand'] :
        byte_mode = instruction['operand']['*']
        if byte_mode :
          self.operation_mode = "byte"
        else :
          self.operation_mode = "word"
      else :
        self.operation_mode = "word"

      self.dst.operation_mode = self.operation_mode
      self.src.operation_mode = self.operation_mode
      self.reg.operation_mode = self.operation_mode

      for (key, value) in list(instruction['operand'].items()) :
        if key == 'o' :
          offset = pdp11_util.uint8toint8(instruction['operand']['o'])
        if key == 's' :
          self.src.raw_value = value
          if (value&0x07) != 0x07 :
            if (value>>3) == 0 :
              self.src.addressing = "register"
              self.src.address = value&0x07
            elif (value>>3) == 1 :
              self.src.addressing = "register deferred"
              self.src.address = self.registers[value&0x07]
            elif (value>>3) == 2 :
              self.src.addressing = "autoincrement"
              self.src.address = self.registers[value&0x07]
              if self.operation_mode == "byte" :
                self.registers[value&0x07] += 1
              else :
                self.registers[value&0x07] += 2
            elif (value>>3) == 3 :
              self.src.addressing = "autoincrement deferred"
              self.src.address = self.memory[self.registers[value&0x07]]
              if self.operation_mode == "byte" :
                self.registers[value&0x07] += 1
              else :
                self.registers[value&0x07] += 2
            elif (value>>3) == 4 :
              self.src.addressing = "autodecrement"
              if self.operation_mode == "byte" :
                self.registers[value&0x07] -= 1
              else :
                self.registers[value&0x07] -= 2
              self.src.address = self.registers[value&0x07]
            elif (value>>3) == 5 :
              self.src.addressing = "autodecrement deferred"
              if self.operation_mode == "byte" :
                self.registers[value&0x07] -= 1
              else :
                self.registers[value&0x07] -= 2
              self.src.address = self.memory[self.registers[value&0x07]]
            elif (value>>3) == 6 :
              self.src.addressing = "index"
              disp = pdp11_util.uint16toint16(self.memory[self.registers[7]])
              self.src.address = (self.registers[value&0x07] + disp)&0xffff
              self.registers[7] += 2
            elif (value>>3) == 7 :
              self.src.addressing = "index deferred"
              disp = pdp11_util.uint16toint16(self.memory[self.registers[7]])
              self.src.address = self.memory[(self.registers[value&0x07] + disp)&0xffff]
              self.registers[7] += 2
            else :
              raise
          else :
            if (value>>3) == 2 or (value>>3) == 0 :
              self.src.addressing = "immidiate"
              self.src.value = self.memory[self.registers[7]]
              self.registers[7] += 2
            elif (value>>3) == 3 or (value>>3) == 1 :
              self.src.addressing = "absolute"
              self.src.address = self.memory[self.registers[7]]
              self.registers[7] += 2
            elif (value>>3) == 6 or (value>>3) == 4 :
              self.src.addressing = "relative"
              self.src.address = (self.memory[self.registers[7]] + self.registers[7] + 2)&0xffff
              self.registers[7] += 2
            elif (value>>3) == 7 or (value>>3) == 5 :
              self.src.addressing = "relative indirect"
              self.src.address = self.memory[(self.memory[self.registers[7]] + self.registers[7] + 2)&0xffff]
              self.registers[7] += 2
            else :
              raise
        if key == 'd' :
          self.dst.raw_value = value
          if (value&0x07) != 0x07 :
            if (value>>3) == 0 :
              self.dst.addressing = "register"
              self.dst.address = value&0x07
            elif (value>>3) == 1 :
              self.dst.addressing = "register deferred"
              self.dst.address = self.registers[value&0x07]
            elif (value>>3) == 2 :
              self.dst.addressing = "autoincrement"
              self.dst.address = self.registers[value&0x07]
              if self.operation_mode == "byte" :
                self.registers[value&0x07] += 1
              else :
                self.registers[value&0x07] += 2
            elif (value>>3) == 3 :
              self.dst.addressing = "autoincrement deferred"
              self.dst.address = self.memory[self.registers[value&0x07]]
              if self.operation_mode == "byte" :
                self.registers[value&0x07] += 1
              else :
                self.registers[value&0x07] += 2
            elif (value>>3) == 4 :
              self.dst.addressing = "autodecrement"
              if self.operation_mode == "byte" :
                self.registers[value&0x07] -= 1
              else :
                self.registers[value&0x07] -= 2
              self.dst.address = self.registers[value&0x07]
            elif (value>>3) == 5 :
              self.dst.addressing = "autodecrement deferred"
              if self.operation_mode == "byte" :
                self.registers[value&0x07] -= 1
              else :
                self.registers[value&0x07] -= 2
              self.dst.address = self.memory[self.registers[value&0x07]]
            elif (value>>3) == 6 :
              self.dst.addressing = "index"
              disp = pdp11_util.uint16toint16(self.memory[self.registers[7]])
              self.dst.address = (self.registers[value&0x07] + disp)&0xffff
              self.registers[7] += 2
            elif (value>>3) == 7 :
              self.dst.addressing = "index deferred"
              disp = pdp11_util.uint16toint16(self.memory[self.registers[7]])
              self.dst.address = self.memory[(self.registers[value&0x07] + disp)&0xffff]
              self.registers[7] += 2
            else :
              raise
          else :
            if (value>>3) == 2 or (value>>3) == 0  :
              self.dst.addressing = "immidiate"
              self.dst.value = self.memory[self.registers[7]]
              self.registers[7] += 2
            elif (value>>3) == 3 or (value>>3) == 1  :
              self.dst.addressing = "absolute"
              self.dst.address = self.memory[self.registers[7]]
              self.registers[7] += 2
            elif (value>>3) == 6 or (value>>3) == 4  :
              self.dst.addressing = "relative"
              self.dst.address = (self.memory[self.registers[7]] + self.registers[7] + 2)&0xffff
              self.registers[7] += 2
            elif (value>>3) == 7 or (value>>3) == 5  :
              self.dst.addressing = "relative indirect"
              self.dst.address = self.memory[(self.memory[self.registers[7]] + self.registers[7] + 2)&0xffff]
              self.registers[7] += 2
            else :
              raise
        if key == 'r' :
            self.reg.addressing = "register"
            self.reg.address = value

      if instruction['opcode'] == "halt" :
        if self.debug : self.debug.write(instruction['opcode']+" ")
        if self.debug : self.debug.write("not implement!\n")
      elif instruction['opcode'] == "wait" :
        if self.debug : self.debug.write(instruction['opcode']+" ")
        if self.debug : self.debug.write("not implement!\n")
      elif instruction['opcode'] == "reset" :
        if self.debug : self.debug.write(instruction['opcode']+" ")
        if self.debug : self.debug.write("not implement!\n")
      elif instruction['opcode'] == "nop" :
        if self.debug : self.debug.write(instruction['opcode']+" ")
        if self.debug : self.debug.write("not implement!\n")

      elif instruction['opcode'] == "scc" :
        if self.debug : self.debug.write(instruction['opcode']+" ")
        if self.debug : self.debug.write("not implement!\n")
      elif instruction['opcode'] == "sen" :
        self.condition_code['n'] = True

      elif instruction['opcode'] == "ses" :
        self.condition_code['c'] = True

      elif instruction['opcode'] == "sev" :
        self.condition_code['v'] = True

      elif instruction['opcode'] == "sez" :
        self.condition_code['z'] = True

      elif instruction['opcode'] == "clr" :
        self.condition_code['n'] = False
        self.condition_code['z'] = True
        self.condition_code['v'] = False
        self.condition_code['c'] = False

        self.dst(0)

      elif instruction['opcode'] == "inc" :
        self.dst += 1
        result = self.dst()

        self.condition_code['n'] = pdp11_util.is_negative(result, 16)
        self.condition_code['z'] = pdp11_util.is_zero(result, 16)
        self.condition_code['v'] = (0xffff & result) == 0x7fff

      elif instruction['opcode'] == "dec" :
        self.dst -= 1
        result = self.dst()

        self.condition_code['n'] = pdp11_util.is_negative(result, 16)
        self.condition_code['z'] = pdp11_util.is_zero(result, 16)

        if self.operation_mode == "byte" :
          self.condition_code['v'] = (result&0xff) == 0x80
        else :
          self.condition_code['v'] = (result&0xffff) == 0x8000

      elif instruction['opcode'] == "adc" :
        dst = self.dst()
        result = dst+self.condition_code['c']

        if self.operation_mode == "byte" :
          self.condition_code['n'] = pdp11_util.is_negative(result, 8)
          self.condition_code['z'] = pdp11_util.is_zero(result, 8)
        else :
          self.condition_code['n'] = pdp11_util.is_negative(result, 16)
          self.condition_code['z'] = pdp11_util.is_zero(result, 16)

        self.condition_code['v'] = (dst == 0x8000) and self.condition_code['c']
        self.condition_code['c'] = (dst == -1) and self.condition_code['c']

        self.dst(result)

      elif instruction['opcode'] == "sbc" :
        if self.debug : self.debug.write(instruction['opcode']+" ")
        if self.debug : self.debug.write("not implement!\n")
      elif instruction['opcode'] == "tst" :
        result = self.dst()

        if self.operation_mode == "byte" :
          self.condition_code['n'] = pdp11_util.is_negative(result, 8)
          self.condition_code['z'] = pdp11_util.is_zero(result, 8)
        else :
          self.condition_code['n'] = pdp11_util.is_negative(result, 16)
          self.condition_code['z'] = pdp11_util.is_zero(result, 16)

        self.condition_code['v'] = False
        self.condition_code['c'] = False

      elif instruction['opcode'] == "neg" :
        result = (-self.dst())&0xffff

        self.condition_code['n'] = pdp11_util.is_negative(result, 16)
        self.condition_code['z'] = pdp11_util.is_zero(result, 16)

        if self.operation_mode == "byte" :
          self.condition_code['v'] = (result&0xff) == 0x80
        else :
          self.condition_code['v'] = (result&0xffff) == 0x8000

        self.condition_code['c'] = (result&0xffff) != 0

        self.dst(result)

      elif instruction['opcode'] == "com" :
        result = ~self.dst()

        self.condition_code['n'] = pdp11_util.is_negative(result, 16)
        self.condition_code['z'] = pdp11_util.is_zero(result, 16)
        self.condition_code['v'] = False
        self.condition_code['c'] = True

        self.dst(result)

      elif instruction['opcode'] == "ror" :
        dst = self.dst()
        result = dst>>1

        if self.operation_mode == "byte" :
          self.condition_code['n'] = pdp11_util.is_negative(result, 8)
          self.condition_code['z'] = pdp11_util.is_zero(result, 8)
          self.condition_code['c'] = bool(dst&1)
          self.condition_code['v'] = self.condition_code['n'] != self.condition_code['c']
        else :
          self.condition_code['n'] = pdp11_util.is_negative(result, 16)
          self.condition_code['z'] = pdp11_util.is_zero(result, 16)
          self.condition_code['c'] = bool(dst&1)
          self.condition_code['v'] = self.condition_code['n'] != self.condition_code['c']

        self.dst(result)

      elif instruction['opcode'] == "rol" :
        dst = self.dst()
        result = dst<<1

        if self.operation_mode == "byte" :
          self.condition_code['n'] = pdp11_util.is_negative(result, 8)
          self.condition_code['z'] = pdp11_util.is_zero(result, 8)
          self.condition_code['c'] = bool(dst&(1<<8))
          self.condition_code['v'] = self.condition_code['n'] != self.condition_code['c']
        else :
          self.condition_code['n'] = pdp11_util.is_negative(result, 16)
          self.condition_code['z'] = pdp11_util.is_zero(result, 16)
          self.condition_code['c'] = bool(dst&(1<<16))
          self.condition_code['v'] = self.condition_code['n'] != self.condition_code['c']

        self.dst(result)


      elif instruction['opcode'] == "asr" :
        dst = self.dst()
        result = dst>>1

        self.condition_code['n'] = pdp11_util.is_negative(result, 16)
        self.condition_code['z'] = pdp11_util.is_zero(result, 16)
        self.condition_code['c'] = bool(dst&0x1)
        self.condition_code['v'] = self.condition_code['n'] != self.condition_code['c']

        self.dst(result)
      elif instruction['opcode'] == "asl" :
        dst = self.dst()
        result = dst<<1

        self.condition_code['n'] = pdp11_util.is_negative(result, 16)
        self.condition_code['z'] = pdp11_util.is_zero(result, 16)
        self.condition_code['c'] = (dst&0xffff) >= 0x8000
        self.condition_code['v'] = self.condition_code['n'] != self.condition_code['c']

        self.dst(result)

      elif instruction['opcode'] == "swab" :
        dst = self.dst()
        dst_h = (self.dst()>>8) & 0xff
        dst_l = self.dst()&0xff
        result = (dst_l<<8) + dst_h

        self.condition_code['n'] = pdp11_util.is_negative(result, 16)
        self.condition_code['z'] = pdp11_util.is_zero(result, 16)
        self.condition_code['v'] = False
        self.condition_code['c'] = False

        self.dst(result)
      elif instruction['opcode'] == "sxt" :
        if self.condition_code['n'] :
          result = -1
        else :
          result = 0

        self.condition_code['z'] = self.condition_code['n'] == False
        self.condition_code['v'] = False

        self.dst(result)

      elif instruction['opcode'] == "mul" :
        s =  self.src()
        if (s&0xffff) >= 0x8000 :
          s -= 0x8000
        result = self.reg()*s

        self.condition_code['n'] = (result&0xffffffff) >= 0x80000000
        self.condition_code['z'] = result == 0
        self.condition_code['v'] = False
        self.condition_code['c'] = result < -0x8000 or 0x7fff <= result

        self.reg(result, dword=True)

      elif instruction['opcode'] == "div" :
        d =  self.reg(dword=True)
        if (d&0xffffffff) >= 0x80000000 :
          d -= 0x80000000

        result = d//self.src()
        result2 = d%self.src()
        
        self.condition_code['n'] = pdp11_util.is_negative(result, 16)
        self.condition_code['z'] = pdp11_util.is_zero(result, 16)
        self.condition_code['v'] = self.src() == 0 or result >= 0x100000000
        self.condition_code['c'] = self.src() == 0

        self.reg((result<<16)+result2, dword=True)

      elif instruction['opcode'] == "ash" :
        dst = self.reg()
        nn = pdp11_util.uint6toint6((self.src()&0x3f))
        result = pdp11_util.bitshift_uint16(dst, nn)

        self.condition_code['n'] = pdp11_util.is_negative(result, 16)
        self.condition_code['z'] = pdp11_util.is_zero(result, 16)
        self.condition_code['v'] = (result&0x8000) != (dst&0x8000)

        if 0 < nn :
          self.condition_code['c'] = (dst>>(16-nn))&1
        elif nn < 0 :
          self.condition_code['c'] = (dst>>(abs(nn)-1))&1
        else :
          self.condition_code['c'] = False

        self.reg(result)

      elif instruction['opcode'] == "ashc" :
        dst = self.reg(dword=True)
        nn = pdp11_util.uint6toint6((self.src()&0x3f))
        result = pdp11_util.bitshift_uint32(dst, nn)

        self.condition_code['n'] = pdp11_util.is_negative(result, 32)
        self.condition_code['z'] = pdp11_util.is_zero(result, 32)
        self.condition_code['v'] = (result&0x80000000) != (dst&0x80000000)
        
        if 0 < nn :
          self.condition_code['c'] = (dst>>(32-nn))&1
        elif nn < 0 :
          self.condition_code['c'] = (dst>>(abs(nn)-1))&1
        else :
          self.condition_code['c'] = False

        self.reg(result, dword=True)

      elif instruction['opcode'] == "xor" :
        if self.debug : self.debug.write(instruction['opcode']+" ")
        if self.debug : self.debug.write("not implement!\n")
      elif instruction['opcode'] == "mov" :
        result = self.src()
        if self.operation_mode == "byte" :
          if result&0x80 :
            result |= 0xff00
          else :
            result &= 0x00ff

        self.condition_code['n'] = pdp11_util.is_negative(result, 16)
        self.condition_code['z'] = pdp11_util.is_zero(result, 16)
        self.condition_code['v'] = False

        self.dst(result)

      elif instruction['opcode'] == "add" :
        src = self.src()
        dst = self.dst()
        result = src+dst

        self.condition_code['n'] = pdp11_util.is_negative(result, 16)
        self.condition_code['z'] = pdp11_util.is_zero(result, 16)
        self.condition_code['v'] = ((0x8000 & src) == (0x8000 & dst) and (0x8000 & result) != (0x8000 & dst))
        self.condition_code['c'] = result & 0x10000

        self.dst(result)

      elif instruction['opcode'] == "sub" :
        src = self.src()
        dst = self.dst()
        result = dst+((~src)&0xffff)+1

        self.condition_code['n'] = pdp11_util.is_negative(result, 16)
        self.condition_code['z'] = pdp11_util.is_zero(result, 16)
        self.condition_code['v'] = ((0x8000 & src) != (0x8000 & dst) and (0x8000 & result) != (0x8000 & dst))
        self.condition_code['c'] = result < 0x10000

        self.dst(result)

      elif instruction['opcode'] == "cmp" :
        src = self.src()
        dst = self.dst()
        if self.operation_mode == "byte" :
          result = src +((~dst)&0xff)+1

          self.condition_code['n'] = pdp11_util.is_negative(result, 8)
          self.condition_code['z'] = pdp11_util.is_zero(result, 8)
          self.condition_code['v'] = ((0x80 & src) != (0x80 & dst) and (0x80 & result) == (0x80 & dst))
          self.condition_code['c'] = result < 0x100

        else :
          result = src+((~dst)&0xffff)+1

          self.condition_code['n'] = pdp11_util.is_negative(result, 16)
          self.condition_code['z'] = pdp11_util.is_zero(result, 16)
          self.condition_code['v'] = ((0x8000 & src) != (0x8000 & dst) and (0x8000 & result) == (0x8000 & dst))
          self.condition_code['c'] = result < 0x10000 

      elif instruction['opcode'] == "bis" :
        result = self.src()|self.dst()

        self.condition_code['n'] = pdp11_util.is_negative(result, 16)
        self.condition_code['z'] = pdp11_util.is_zero(result, 16)
        self.condition_code['v'] = False

        self.dst(result)

      elif instruction['opcode'] == "bic" :
        result = (~self.src())&self.dst()

        self.condition_code['n'] = pdp11_util.is_negative(result, 16)
        self.condition_code['z'] = pdp11_util.is_zero(result, 16)
        self.condition_code['v'] = False

        self.dst(result)

      elif instruction['opcode'] == "bit" :
        result = self.src()&self.dst()

        if self.operation_mode == "byte" :
          self.condition_code['n'] = pdp11_util.is_negative(result, 8)
          self.condition_code['z'] = pdp11_util.is_zero(result, 8)
        else :
          self.condition_code['n'] = pdp11_util.is_negative(result, 16)
          self.condition_code['z'] = pdp11_util.is_zero(result, 16)

        self.condition_code['v'] = False

      elif instruction['opcode'] == "br" :
        self.registers[7] += 2*offset

      elif instruction['opcode'] == "bne" :
        if self.condition_code['z'] == False :
          self.registers[7] += 2*offset

      elif instruction['opcode'] == "beq" :
        if self.condition_code['z'] == True :
          self.registers[7] += 2*offset

      elif instruction['opcode'] == "bpl" :
        if self.condition_code['n'] == False :
          self.registers[7] += 2*offset

      elif instruction['opcode'] == "bmi" :
        if self.condition_code['n'] == True :
          self.registers[7] += 2*offset

      elif instruction['opcode'] == "bvc" :
        if self.condition_code['v'] == False :
          self.registers[7] += 2*offset

      elif instruction['opcode'] == "bvs" :
        if self.condition_code['v'] == True :
          self.registers[7] += 2*offset

      elif instruction['opcode'] == "bcc" :
        if self.condition_code['c'] == False :
          self.registers[7] += 2*offset

      elif instruction['opcode'] == "bcs" :
        if self.condition_code['c'] == True :
          self.registers[7] += 2*offset

      elif instruction['opcode'] == "bge" :
        if ( (self.condition_code['n'] != self.condition_code['v']) == False) :
          self.registers[7] += 2*offset

      elif instruction['opcode'] == "blt" :
        if ( (self.condition_code['n'] != self.condition_code['v']) == True) :
          self.registers[7] += 2*offset

      elif instruction['opcode'] == "bgt" :
        if ( self.condition_code['z'] or
             (self.condition_code['n'] != self.condition_code['v'])) == False :
          self.registers[7] += 2*offset

      elif instruction['opcode'] == "ble" :
        if ( self.condition_code['z'] or
             (self.condition_code['n'] != self.condition_code['v'])) == True:
          self.registers[7] += 2*offset

      elif instruction['opcode'] == "bhi" :
        if ( self.condition_code['c'] == False and
             self.condition_code['z'] == False ) :
          self.registers[7] += 2*offset

      elif instruction['opcode'] == "blos" :
        if ( self.condition_code['c'] == True or
             self.condition_code['z'] == True ) :
          self.registers[7] += 2*offset

      elif instruction['opcode'] == "jmp" :
        addr = self.dst.addr()
        self.registers[7] = addr

      elif instruction['opcode'] == "sob" :
        result = self.reg()-1
        addr = self.dst.raw_value

        if (result&0xffff) != 0 :
          self.registers[7] -= 2*addr

        self.reg(result)

      elif instruction['opcode'] == "jsr" :
        addr = self.dst.addr()
        self.push(self.registers[instruction['operand']['r']])
        self.reg(self.registers[7])
        self.registers[7] = addr

      elif instruction['opcode'] == "rts" :
        self.registers[7] = self.registers[instruction['operand']['r']]
        self.registers[instruction['operand']['r']] = self.pop()

      elif instruction['opcode'] == "rti" :
        if self.debug : self.debug.write(instruction['opcode']+" ")
        if self.debug : self.debug.write("not implement!\n")

      elif instruction['opcode'] == "rpt" :
        if self.debug : self.debug.write(instruction['opcode']+" ")
        if self.debug : self.debug.write("not implement!\n")

      elif instruction['opcode'] == "iot" :
        if self.debug : self.debug.write(instruction['opcode']+" ")
        if self.debug : self.debug.write("not implement!\n")

      elif instruction['opcode'] == "sys" :
        x = instruction['operand']['x']
        y = instruction['operand']['y']
        z = instruction['operand']['z']
        self.sys((y<<3)+z)

      elif instruction['opcode'] == "rtt" :
        addr = self.pop()
        self.registers[7] = addr

      elif instruction['opcode'] == "cfcc" :
        pass

      elif instruction['opcode'] == "setf" :
        pass

      elif instruction['opcode'] == "seti" :
        pass

      elif instruction['opcode'] == "setd" :
        pass

      elif instruction['opcode'] == "setl" :
        pass

      else :
        if self.debug : self.debug.write(instruction['opcode']+" ")
        if self.debug : self.debug.write("not implement!\n")

    else :
      raise

  def run(self, limit=None) :
      if self.debug :
        self.debug.write(" r0   r1   r2   r3   r4   r5   sp  flags pc\n")
      i = 0
      while True :
        try :
          self.step()
        except SysExit :
          break
        finally :
          if self.debug :
            self.debug.write(self.get_state_text()+"\n")
        i += 1
        if limit is not None and i == limit : break

  def sys_exec(self, args) :
    self.memory.setMode("byte")
    # initialize
    self.memory.resetByZero()
    #   registers
    for i in range(8) :
      self.registers[i] = 0

    # load program
    f = open(pdp11_util.chpath(args[0]), 'rb')
    program = list(f.read())
    if six.PY2 :  program = map(ord, program)
    self.aout = pdp11_aout.getAout(program)
    self.memory.load(self.aout['text'] + self.aout['data'])
    self.registers[7] = self.aout['header']['a_entry']

    # set argv
    argc = [len(args)&0xff, (len(args)>>8)&0xff]
    address = 0x10000 - len(list(map(ord, '\0'.join(args)+'\0')))
    argv = []
    data = []

    align_flag = False
    if address%2 == 1 :
      address -= 1
      align_flag = True

    for arg in args :
      data += list(map(ord, arg+'\0'))
      argv += [address&0xff, (address>>8)&0xff]
      address += len(arg)+1

    if align_flag :
      data += [0]

    self.memory.load(argc+argv+data, 0x10000-len(argc+argv+data))
    self.registers[6] = 0x10000-len(argc+argv+data)

    self.sighandler = 0

  def load(self, args) :
    self.sys_exec(args)

  def get_state_text(self) :
    text = ""

    if self.symbol :
      text += self.symbol+":\n"

    text += self.state + self.disassemble

    if self.src.memory_dump : text += self.src.memory_dump
    if self.dst.memory_dump : text += self.dst.memory_dump
    if self.reg.memory_dump : text += self.reg.memory_dump

    if self.syscall:
      text += "\n"+self.syscall

    return text

if __name__ == '__main__':
  vm = VM()
  vm.debug=sys.stderr
  vm.load(['/usr/local/v6root/bin/as', 'write-1.s'])
  vm.run()

