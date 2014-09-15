# -*- coding: utf-8 -*-
import sys
from pprint import pprint as pp

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


    self.filedescriptors = [None for x in range(0xffff)]

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
      #store
      pc = self.registers[7]
      disassemble = self.disassemble
      state = self.state

      #syscall
      self.registers[7] = self.memory[self.registers[7]]
      self.step()

      #load
      self.registers[7] = pc
      self.registers[7] += 2
      self.disassemble = disassemble
      self.state = state

    elif num == 1 : #exit
      info = pdp11_util.uint16toint16(self.registers[0])

      self.syscall = '<exit({:d})>'.format(info)

      raise SysExit()

    elif num == 2 : #fork
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")

    elif num == 3 : #read
      filedescriptor = self.registers[0]
      f = self.filedescriptors[filedescriptor]
      addr = self.memory[self.registers[7]]
      size = self.memory[self.registers[7]+2]

      self.memory[addr:addr+size] = map(ord, f.read(size))

      self.registers[0] = size
      self.registers[7] += 4

      self.syscall = '<read({:d}, 0x{:04x}, {:d}) => {:d}>'.format(filedescriptor, addr, size, self.registers[0])

    elif num == 4 : #write
      filedescriptor = self.registers[0]
      f = self.filedescriptors[filedescriptor]
      addr = self.memory[self.registers[7]]
      size = self.memory[self.registers[7]+2]

      f.write(''.join(map(chr, self.memory[addr:addr+size])))

      self.registers[0] = size
      self.registers[7] += 4

      self.syscall = '<write({:d}, 0x{:04x}, {:d}) => {:d}>'.format(filedescriptor, addr, size, self.registers[0])

    elif num == 5 : #open
      filepath_p = self.memory[self.registers[7]]
      mode = self.memory[self.registers[7]+2]
      self.memory.setMode("byte")
      filepath = ""
      while self.memory[filepath_p] :
        filepath += chr(self.memory[filepath_p])
        filepath_p += 1
      self.memory.setMode("byte")

      if mode == 0 :
        f = open(filepath, 'r')
      else :
        f = open(filepath, 'w')

      for (i, filedescriptor) in enumerate(self.filedescriptors) :
        if filedescriptor is None :
          self.filedescriptors[i] = f
          break

      self.registers[0] = i
      self.registers[7] += 4

      self.syscall = '<open("{}", {}) => {}>'.format(filepath, mode, self.registers[0])

    elif num == 6 : #close
      fd = self.registers[0]
      self.filedescriptors[fd] = None

      self.registers[0] = 0

      self.syscall = '<close({}) => {}>'.format(fd, 0)

    elif num == 7 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 8 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 9 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 10 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 11 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 12 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 13 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 14 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 15 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 16 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 17 : #break
      addr = self.memory[self.registers[7]]

      self.registers[0] = 0

      self.syscall = '<brk(0x{:04x}) => {}>'.format(addr, 0)
    elif num == 18 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 19 : #seek
      filedescriptor = self.registers[0]
      f = self.filedescriptors[self.registers[0]]
      offset = self.memory[self.registers[7]]
      whence = self.memory[self.registers[7]+2]

      f.seek(offset, whence)

      self.registers[0] = f.tell()
      self.registers[7] += 4

      self.syscall = '<lseek({}, {}, {}) => {}>'.format(filedescriptor, offset, whence, self.registers[0])

    elif num == 20 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 21 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 22 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 23 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 24 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 25 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 26 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 27 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 28 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 29 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 30 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 31 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 32 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 33 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 34 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 35 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 36 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 37 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 38 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 39 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 40 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 41 :
      fd = self.registers[0]
      f = self.filedescriptors[fd]
      for (i, filedescriptor) in enumerate(self.filedescriptors) :
        if filedescriptor is None :
          self.filedescriptors[i] = f
          break
      self.registers[0] = i

      self.syscall = '<dup({}) => {}>'.format(fd, i)

    elif num == 42 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 43 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 44 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 45 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 46 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 47 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 48 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 49 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 50 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 51 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 52 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 53 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 54 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 55 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 56 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 57 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 58 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 59 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 60 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 61 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 62 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    elif num == 63 :
      if self.debug : self.debug.write(str(num)+" ")
      if self.debug : self.debug.write("not implement!\n")
    else :
      pass

    self.condition_code['c'] = False

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
    for (k, v) in self.aout['syms']['symbol_table'].items() :
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

      for (key, value) in instruction['operand'].items() :
        if key == 'o' :
          offset = pdp11_util.uint8toint8(instruction['operand']['o'])
        if key == 's' :
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
        if (0xffff & result) == 0x7fff :
          self.condition_code['v'] = True
        else :
          self.condition_code['v'] = False

      elif instruction['opcode'] == "dec" :
        self.dst -= 1
        result = self.dst()

        self.condition_code['n'] = pdp11_util.is_negative(result, 16)
        self.condition_code['z'] = pdp11_util.is_zero(result, 16)

        if self.operation_mode == "byte" :
          if (result&0xff) == 0x80 :
            self.condition_code['v'] = True
          else :
            self.condition_code['v'] = False
        else :
          if (result&0xffff) == 0x8000 :
            self.condition_code['v'] = True
          else :
            self.condition_code['v'] = False

      elif instruction['opcode'] == "adc" :
        if self.debug : self.debug.write(instruction['opcode']+" ")
        if self.debug : self.debug.write("not implement!\n")
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
          if (result&0xff) == 0x80 :
            self.condition_code['v'] = True
          else :
            self.condition_code['v'] = False
        else :
          if (result&0xffff) == 0x8000 :
            self.condition_code['v'] = True
          else :
            self.condition_code['v'] = False

        if (result&0xffff) != 0 :
          self.condition_code['c'] = True
        else :
          self.condition_code['c'] = False

        self.dst(result)

      elif instruction['opcode'] == "com" :
        if self.debug : self.debug.write(instruction['opcode']+" ")
        if self.debug : self.debug.write("not implement!\n")
      elif instruction['opcode'] == "ror" :
        if self.debug : self.debug.write(instruction['opcode']+" ")
        if self.debug : self.debug.write("not implement!\n")
      elif instruction['opcode'] == "rol" :
        if self.debug : self.debug.write(instruction['opcode']+" ")
        if self.debug : self.debug.write("not implement!\n")
      elif instruction['opcode'] == "asr" :
        if self.debug : self.debug.write(instruction['opcode']+" ")
        if self.debug : self.debug.write("not implement!\n")
      elif instruction['opcode'] == "asl" :
        dst = self.dst()
        result = dst<<1

        self.condition_code['n'] = pdp11_util.is_negative(result, 16)
        self.condition_code['z'] = pdp11_util.is_zero(result, 16)

        if (dst&0xffff) >= 0x8000 :
          self.condition_code['c'] = True
        else :
          self.condition_code['c'] = False

        if  self.condition_code['n'] != self.condition_code['c'] :
          self.condition_code['v'] = True
        else :
          self.condition_code['v'] = False

        self.dst(result)
      elif instruction['opcode'] == "swab" :
        if self.debug : self.debug.write(instruction['opcode']+" ")
        if self.debug : self.debug.write("not implement!\n")
      elif instruction['opcode'] == "sxt" :
        if self.condition_code['n'] :
          result = -1
        else :
          result = 0

        if self.condition_code['n'] == False :
          self.condition_code['z'] = True
        else :
          self.condition_code['z'] = False

        self.condition_code['v'] = False

        self.dst(result)

      elif instruction['opcode'] == "mul" :
        s =  self.src()
        if (s&0xffff) >= 0x8000 :
          s -= 0x8000
        result = self.reg()*s

        if (result&0xffffffff) >= 0x80000000 :
          self.condition_code['n'] = True
        else :
          self.condition_code['n'] = False

        if result == 0 :
          self.condition_code['z'] = True
        else :
          self.condition_code['z'] = False

        self.condition_code['v'] = False

        if result < -0x10000 or 0xffff <= result :
          self.condition_code['c'] = True
        else :
          self.condition_code['c'] = False

        self.reg(result, dword=True)
      elif instruction['opcode'] == "div" :
        d =  self.reg(dword=True)
        if (d&0xffffffff) >= 0x80000000 :
          d -= 0x80000000

        result = d/self.src()
        result2 = d%self.src()
        
        self.condition_code['n'] = pdp11_util.is_negative(result, 16)
        self.condition_code['z'] = pdp11_util.is_zero(result, 16)

        if self.src() == 0 or result >= 0x100000000 :
          self.condition_code['v'] = True
        else :
          self.condition_code['v'] = False

        if self.src() == 0 :
          self.condition_code['c'] = True
        else :
          self.condition_code['c'] = False

        self.reg((result<<16)+result2, dword=True)

      elif instruction['opcode'] == "ash" :
        dst = self.dst()
        nn = pdp11_util.uint6toint6((self.src()&0x3f))
        result = pdp11_util.bitshift_uint16(dst, nn)

        self.condition_code['n'] = pdp11_util.is_negative(result, 16)
        self.condition_code['z'] = pdp11_util.is_zero(result, 16)

        if (result&0x8000) != (dst&0x8000) :
          self.condition_code['v'] = True
        else :
          self.condition_code['v'] = False

        if 0 < nn :
          if (dst>>(16-nn))&1:
            self.condition_code['c'] = True
          else :
            self.condition_code['c'] = False
        elif nn < 0 :
          if (dst>>(abs(nn)-1))&1:
            self.condition_code['c'] = True
          else :
            self.condition_code['c'] = False
        else :
          self.condition_code['c'] = False

        self.dst(result)

      elif instruction['opcode'] == "ashc" :
        if self.debug : self.debug.write(instruction['opcode']+" ")
        if self.debug : self.debug.write("not implement!\n")
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
        result = self.src()+self.dst()

        self.condition_code['n'] = pdp11_util.is_negative(result, 16)
        self.condition_code['z'] = pdp11_util.is_zero(result, 16)

        if (((0x8000 & self.src()) == (0x8000 & self.dst())) and
            ((0x8000 & result) != (0x8000 & self.dst()))) :
          self.condition_code['v'] = True
        else :
          self.condition_code['v'] = False

        if result & 0x10000 :
          self.condition_code['c'] = True
        else :
          self.condition_code['c'] = False

        self.dst(result)

      elif instruction['opcode'] == "sub" :
        result = self.dst()+((~self.src())&0xffff)+1

        if (result&0xffff) >= 0x8000 :
          self.condition_code['n'] = True
        else :
          self.condition_code['n'] = False
        if (result&0xffff) == 0 :
          self.condition_code['z'] = True
        else :
          self.condition_code['z'] = False
        if (((0x8000 & self.src()) != (0x8000 & self.dst())) and
            ((0x8000 & result) != (0x8000 & self.dst()))) :
          self.condition_code['v'] = True
        else :
          self.condition_code['v'] = False

        if result < 0x10000 :
          self.condition_code['c'] = True
        else :
          self.condition_code['c'] = False

        self.dst(result)

      elif instruction['opcode'] == "cmp" :
        src = self.src()
        dst = self.dst()
        if self.operation_mode == "byte" :
          result = src +((~dst)&0xff)+1

          self.condition_code['n'] = pdp11_util.is_negative(result, 8)
          self.condition_code['z'] = pdp11_util.is_zero(result, 8)

          if ((0x80 & src) != (0x80 & dst) and
              (0x80 & result) == (0x80 & self.dst())) :
            self.condition_code['v'] = True
          else :
            self.condition_code['v'] = False

          if result < 0x100:
            self.condition_code['c'] = True
          else :
            self.condition_code['c'] = False
        else :
          result = src+((~dst)&0xffff)+1

          self.condition_code['n'] = pdp11_util.is_negative(result, 16)
          self.condition_code['z'] = pdp11_util.is_zero(result, 16)

          if ((0x8000 & src) != (0x8000 & dst) and
              ((0x8000 & result) == (0x8000 & dst))) :
            self.condition_code['v'] = True
          else :
            self.condition_code['v'] = False

          if result < 0x10000 :
            self.condition_code['c'] = True
          else :
            self.condition_code['c'] = False

      elif instruction['opcode'] == "bis" :
        if self.debug : self.debug.write(instruction['opcode']+" ")
        if self.debug : self.debug.write("not implement!\n")
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
        if self.debug : self.debug.write(instruction['opcode']+" ")
        if self.debug : self.debug.write("not implement!\n")

      elif instruction['opcode'] == "jmp" :
        addr = self.dst.addr()
        self.registers[7] = addr

      elif instruction['opcode'] == "sob" :
        result = self.reg()-1
        addr = self.dst.address

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

  def run(self) :
      if self.debug :
        self.debug.write(" r0   r1   r2   r3   r4   r5   sp  flags pc\n")
      while True :
        try :
          self.step()
        except SysExit :
          break
        finally :
          if self.debug :
            self.debug.write(self.get_state_text()+"\n")

  def load(self, args, stdin=None, stdout=None, stderr=None) :
    self.memory.setMode("byte")
    # initialize
    #   registers
    for i in range(8) :
      self.registers[i] = 0
    #   filedescriptors
    if stdin is None : stdin = sys.stdin
    if stdout is None : stdout = sys.stdout
    if stderr is None : stderr = sys.stderr
    self.filedescriptors = [None for x in range(0xffff)]
    self.filedescriptors[0] = stdin
    self.filedescriptors[1] = stdout
    self.filedescriptors[2] = stderr

    # load program
    f = open(args[0], 'rb')
    program = map(ord, f.read())
    self.aout = pdp11_aout.getAout(program)
    self.memory.load(self.aout['text'] + self.aout['data'])
    self.registers[7] = self.aout['header']['a_entry']

    # set argv
    argc = [len(args)&0xff, (len(args)>>8)&0xff]
    address = 0x10000 - len(map(ord, '\0'.join(args)+'\0'))
    argv = []
    data = []

    align_flag = False
    if address%2 == 1 :
      address -= 1
      align_flag = True

    for arg in args :
      data += map(ord, arg+'\0')
      argv += [address&0xff, (address>>8)&0xff]
      address += len(arg)+1

    if align_flag :
      data += [0]

    self.memory.load(argc+argv+data, 0x10000-len(argc+argv+data))
    self.registers[6] = 0x10000-len(argc+argv+data)

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
  vm.load(['/usr/local/v6root/bin/nm', 'test1'],
    sys.stdin,
    sys.stdout,
    sys.stderr
  )
  vm.run()

