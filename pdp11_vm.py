# -*- coding: utf-8 -*-
import pprint
import sys

import pdp11_aout
import pdp11_decode
import pdp11_disassem
import pdp11_registers
import pdp11_memory
import pdp11_util

class VM :
  def __init__(self) :
    self.memory = pdp11_memory.Memory()
    self.registers = pdp11_registers.Registers()
    self.condition_code = {'n':False,
                           'z':False,
                           'v':False,
                           'c':False,
    }
    self.operation_mode = None
    self.operand = {'dst': {
                      'value': None,
                      'addressing': None,
                      'address': None,
                    },
                    'src': {
                      'value': None,
                      'addressing': None,
                      'address': None,
                    },
    }

    self.filedescriptors_ = [sys.stdin, sys.stdout, sys.stderr]

  def loadAout(self, filename) :
    f = open(filename, 'rb')
    program = map(ord, f.read())
    aout = pdp11_aout.getAout(program)
    self.memory.load(aout['text'] + aout['data'])
    self.registers[7] = aout['header']['a_entry']

  def getOperand(self, direction) :
    self.registers.setMode(self.operation_mode)
    self.memory.setMode(self.operation_mode)

    if self.operand[direction]['addressing'] == 'immidiate' :
      value = self.operand[direction]['value']
    elif self.operand[direction]['addressing'] == 'register' :
      value = self.registers[self.operand[direction]['address']]
    elif ( self.operand[direction]['addressing'] == 'register deferred' or
           self.operand[direction]['addressing'] == 'autoincrement' or
           self.operand[direction]['addressing'] == 'autoincrement deferred' or
           self.operand[direction]['addressing'] == 'autodecrement' or
           self.operand[direction]['addressing'] == 'autodecrement deferred' or
           self.operand[direction]['addressing'] == 'index' or
           self.operand[direction]['addressing'] == 'index deferred' or
           self.operand[direction]['addressing'] == 'absolute' or
           self.operand[direction]['addressing'] == 'relative' or
           self.operand[direction]['addressing'] == 'relative indirect' ) :
      value = self.memory[self.operand[direction]['address']]
    else :
      pass

    self.registers.setMode("word")
    self.memory.setMode("word")

    return value

  def getSrc(self) : return self.getOperand('src')
  def getDst(self) : return self.getOperand('dst')

  def setOperand(self, value, direction) :
    self.registers.setMode(self.operation_mode)
    self.memory.setMode(self.operation_mode)

    if self.operand[direction]['addressing'] == 'immidiate' :
      pass
    elif self.operand[direction]['addressing'] == 'register' :
      self.registers[self.operand[direction]['address']] = value
    elif ( self.operand[direction]['addressing'] == 'register deferred' or
           self.operand[direction]['addressing'] == 'autoincrement' or
           self.operand[direction]['addressing'] == 'autoincrement deferred' or
           self.operand[direction]['addressing'] == 'autodecrement' or
           self.operand[direction]['addressing'] == 'autodecrement deferred' or
           self.operand[direction]['addressing'] == 'index' or
           self.operand[direction]['addressing'] == 'index deferred' or
           self.operand[direction]['addressing'] == 'absolute' or
           self.operand[direction]['addressing'] == 'relative' or
           self.operand[direction]['addressing'] == 'relative indirect' ) :
      self.memory[self.operand[direction]['address']] = value
    else :
      pass

    self.registers.setMode("word")
    self.memory.setMode("word")

  def setDst(self, value) : self.setOperand(value, 'dst')
  def setAddr(self, value) : self.setOperand(value, 'addr')

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
      self.registers[7] = self.memory[self.registers[7]]
      self.step()
      self.registers[7] = pc
      self.registers[7] += 2

    elif num == 1 : #exit
      sys.exit()

    elif num == 2 : #fork
      print "not implement!"
    elif num == 3 : #read
      f = self.filedescriptors_[self.registers[0]]
      addr = self.memory[self.registers[7]]
      size = self.memory[self.registers[7]+2]

      self.memory[addr:addr+size] = map(ord, f.read(size))

      self.registers[0] = size
      self.registers[7] += 4

    elif num == 4 : #write
      f = self.filedescriptors_[self.registers[0]]
      addr = self.memory[self.registers[7]]
      size = self.memory[self.registers[7]+2]

      f.write(''.join(map(chr, self.memory[addr:addr+size])))

      self.registers[0] = size
      self.registers[7] += 4

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

      self.registers[0] = len(self.filedescriptors_)
      self.filedescriptors_.append(f)
      self.registers[7] += 4

    elif num == 6 :
      print "not implement!"
    elif num == 7 :
      print "not implement!"
    elif num == 8 :
      print "not implement!"
    elif num == 9 :
      print "not implement!"
    elif num == 10 :
      print "not implement!"
    elif num == 11 : #lseek
      f = self.filedescriptors_[self.registers[0]]
      offset = self.memory[self.registers[7]]
      whence = self.memory[self.registers[7]+2]

      f.seek(offset, whence)

      self.registers[0] = f.tell()
      self.registers[7] += 4

    elif num == 12 :
      print "not implement!"
    elif num == 13 :
      print "not implement!"
    elif num == 14 :
      print "not implement!"
    elif num == 15 :
      print "not implement!"
    elif num == 16 :
      print "not implement!"
    elif num == 17 :
      print "not implement!"
    elif num == 18 :
      print "not implement!"
    elif num == 19 :
      print "not implement!"
    elif num == 20 :
      print "not implement!"
    elif num == 21 :
      print "not implement!"
    elif num == 22 :
      print "not implement!"
    elif num == 23 :
      print "not implement!"
    elif num == 24 :
      print "not implement!"
    elif num == 25 :
      print "not implement!"
    elif num == 26 :
      print "not implement!"
    elif num == 27 :
      print "not implement!"
    elif num == 28 :
      print "not implement!"
    elif num == 29 :
      print "not implement!"
    elif num == 30 :
      print "not implement!"
    elif num == 31 :
      print "not implement!"
    elif num == 32 :
      print "not implement!"
    elif num == 33 :
      print "not implement!"
    elif num == 34 :
      print "not implement!"
    elif num == 35 :
      print "not implement!"
    elif num == 36 :
      print "not implement!"
    elif num == 37 :
      print "not implement!"
    elif num == 38 :
      print "not implement!"
    elif num == 39 :
      print "not implement!"
    elif num == 40 :
      print "not implement!"
    elif num == 41 :
      print "not implement!"
    elif num == 42 :
      print "not implement!"
    elif num == 43 :
      print "not implement!"
    elif num == 44 :
      print "not implement!"
    elif num == 45 :
      print "not implement!"
    elif num == 46 :
      print "not implement!"
    elif num == 47 :
      print "not implement!"
    elif num == 48 :
      print "not implement!"
    elif num == 49 :
      print "not implement!"
    elif num == 50 :
      print "not implement!"
    elif num == 51 :
      print "not implement!"
    elif num == 52 :
      print "not implement!"
    elif num == 53 :
      print "not implement!"
    elif num == 54 :
      print "not implement!"
    elif num == 55 :
      print "not implement!"
    elif num == 56 :
      print "not implement!"
    elif num == 57 :
      print "not implement!"
    elif num == 58 :
      print "not implement!"
    elif num == 59 :
      print "not implement!"
    elif num == 60 :
      print "not implement!"
    elif num == 61 :
      print "not implement!"
    elif num == 62 :
      print "not implement!"
    elif num == 63 :
      print "not implement!"
    else :
      pass

  def step(self) :
    self.printState()
    instruction = pdp11_decode.searchMatchInstructionFormat(self.memory, self.registers[7])

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

      for (key, value) in instruction['operand'].items() :

        if key == 'o' :
          offset = pdp11_util.uint8toint8(instruction['operand']['o'])
        if key in ['s', 'd'] :
          if key == 's' : direction = 'src'
          else : direction = 'dst'
          if (value&0x07) != 0x07 :
            if (value>>3) == 0 :
              self.operand[direction]['addressing'] = "register"
              self.operand[direction]['address'] = value&0x07
            elif (value>>3) == 1 :
              self.operand[direction]['addressing'] = "register deferred"
              self.operand[direction]['address'] = self.registers[value&0x07]
            elif (value>>3) == 2 :
              self.operand[direction]['addressing'] = "autoincrement"
              self.operand[direction]['address'] = self.registers[value&0x07]
              if self.operation_mode == "byte" :
                self.registers[value&0x07] += 1
              else :
                self.registers[value&0x07] += 2
            elif (value>>3) == 3 :
              self.operand[direction]['addressing'] = "autoincrement deferred"
              self.operand[direction]['address'] = self.memory[self.registers[value&0x07]]
              if self.operation_mode == "byte" :
                self.registers[value&0x07] += 1
              else :
                self.registers[value&0x07] += 2
            elif (value>>3) == 4 :
              self.operand[direction]['addressing'] = "autodecrement"
              if self.operation_mode == "byte" :
                self.registers[value&0x07] -= 1
              else :
                self.registers[value&0x07] -= 2
              self.operand[direction]['address'] = self.registers[value&0x07]
            elif (value>>3) == 5 :
              self.operand[direction]['addressing'] = "autodecrement deferred"
              if self.operation_mode == "byte" :
                self.registers[value&0x07] -= 1
              else :
                self.registers[value&0x07] -= 2
              self.operand[direction]['address'] = self.memory[self.registers[value&0x07]]
            elif (value>>3) == 6 :
              self.operand[direction]['addressing'] = "index"
              disp = pdp11_util.uint16toint16(self.memory[self.registers[7]])
              self.operand[direction]['address'] = self.registers[value&0x07] + disp
              self.registers[7] += 2
            elif (value>>3) == 7 :
              self.operand[direction]['addressing'] = "index deferred"
              disp = pdp11_util.uint16toint16(self.memory[self.registers[7]])
              self.operand[direction]['address'] = self.memory[self.registers[value&0x07] + disp]
              self.registers[7] += 2
            else :
              pass
          else :
            if (value>>3) == 2 :
              self.operand[direction]['addressing'] = "immidiate"
              self.operand[direction]['value'] = self.memory[self.registers[7]]
              self.registers[7] += 2
            elif (value>>3) == 3 :
              self.operand[direction]['addressing'] = "absolute"
              self.operand[direction]['address'] = self.memory[self.registers[7]]
              self.registers[7] += 2
            elif (value>>3) == 6 :
              self.operand[direction]['addressing'] = "relative"
              self.operand[direction]['address'] = (
                self.memory[self.registers[7]]
                + self.registers[7] + 2)
              self.registers[7] += 2
            elif (value>>3) == 7 :
              self.operand[direction]['addressing'] = "relative indirect"
              self.operand[direction]['address'] = (self.memory[
                self.memory[self.registers[7]]
                + self.registers[7] + 2])
              self.registers[7] += 2
            else :
              pass

      if instruction['opcode'] == "halt" :
        print "not implement!"
      elif instruction['opcode'] == "wait" :
        print "not implement!"
      elif instruction['opcode'] == "reset" :
        print "not implement!"
      elif instruction['opcode'] == "nop" :
        print "not implement!"
      elif instruction['opcode'] == "clr" :
        self.setDst(0)

        self.condition_code['n'] = False
        self.condition_code['z'] = True
        self.condition_code['v'] = False
        self.condition_code['c'] = False

      elif instruction['opcode'] == "inc" :
        v = self.getDst()+1
        self.setDst(v)

        if (0xffff & v) > 0x7fff :
          self.condition_code['n'] = True
        else :
          self.condition_code['n'] = False
        if (0xffff & v) == 0 :
          self.condition_code['z'] = True
        else :
          self.condition_code['z'] = False
        if (0xffff & v) == 0x7fff :
          self.condition_code['v'] = True
        else :
          self.condition_code['v'] = False

      elif instruction['opcode'] == "dec" :
        dst = self.getDst()
        result = self.getDst()-1
        self.setDst(result)

        if (result&0xffff) >= 0x8000 :
          self.condition_code['n'] = True
        else :
          self.condition_code['n'] = False

        if (result&0xffff) == 0 :
          self.condition_code['z'] = True
        else :
          self.condition_code['z'] = False

        if self.operation_mode == "byte" :
          if (dst&0xff) == 0x80 :
            self.condition_code['v'] = True
          else :
            self.condition_code['v'] = False
        else :
          if (dst&0xffff) == 0x8000 :
            self.condition_code['v'] = True
          else :
            self.condition_code['v'] = False

      elif instruction['opcode'] == "adc" :
        print "not implement!"
      elif instruction['opcode'] == "sbc" :
        print "not implement!"
      elif instruction['opcode'] == "tst" :
        result = self.getDst()
        self.setDst(result)

        if self.operation_mode == "byte" :
          if (result&0xff) >= 0x80 :
            self.condition_code['n'] = True
          else :
            self.condition_code['n'] = False

          if (result&0xff) == 0 :
            self.condition_code['z'] = True
          else :
            self.condition_code['z'] = False
        else :
          if (result&0xffff) > 0x8000 :
            self.condition_code['n'] = True
          else :
            self.condition_code['n'] = False

          if (result&0xffff) == 0 :
            self.condition_code['z'] = True
          else :
            self.condition_code['z'] = False

        self.condition_code['v'] = False

        self.condition_code['c'] = False

      elif instruction['opcode'] == "neg" :
        result = (-self.getDst())&0xffff
        self.setDst(result)

        if (result&0xffff) >= 0x8000 :
          self.condition_code['n'] = True
        else :
          self.condition_code['n'] = False

        if (result&0xffff) == 0 :
          self.condition_code['z'] = True
        else :
          self.condition_code['z'] = False

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

        if (result&0xffff) == 0 :
          self.condition_code['c'] = True
        else :
          self.condition_code['c'] = False

      elif instruction['opcode'] == "com" :
        print "not implement!"
      elif instruction['opcode'] == "ror" :
        print "not implement!"
      elif instruction['opcode'] == "rol" :
        print "not implement!"
      elif instruction['opcode'] == "asr" :
        print "not implement!"
      elif instruction['opcode'] == "asl" :
        result = (self.getDst()<<1)
        self.setDst(result)
      elif instruction['opcode'] == "swab" :
        print "not implement!"
      elif instruction['opcode'] == "sxt" :
        print "not implement!"
      elif instruction['opcode'] == "mul" :
        print "not implement!"
      elif instruction['opcode'] == "mul" :
        print "not implement!"
      elif instruction['opcode'] == "div" :
        result = self.getDst()/self.getSrc()
        
        if (result&0xffff) >= 0x8000 :
          self.condition_code['n'] = True
        else :
          self.condition_code['n'] = False

        if (result&0xffff) == 0 :
          self.condition_code['z'] = True
        else :
          self.condition_code['z'] = False

        if self.getSrc() == 0 :
          self.condition_code['v'] = True
        else :
          self.condition_code['v'] = False

        if self.getSrc() == 0 :
          self.condition_code['c'] = True
        else :
          self.condition_code['c'] = False

      elif instruction['opcode'] == "ash" :
        dst = self.getDst()
        nn = pdp11_util.uint6toint6((self.getSrc()&0x3f))
        result = pdp11_util.bitshift_uint16(dst, nn)
        self.setDst(result)

        if (result&0xffff) >= 0x8000 :
          self.condition_code['n'] = True
        else :
          self.condition_code['n'] = False

        if (result&0xffff) == 0 :
          self.condition_code['z'] = True
        else :
          self.condition_code['z'] = False

        if (result&0x8000) != (dst&0x8000) :
          self.condition_code['v'] = True
        else :
          self.condition_code['v'] = False

        if nn :
          if result&0x10000 :
            self.condition_code['c'] = True
          else :
            self.condition_code['c'] = False
        else :
          self.condition_code['c'] = False

      elif instruction['opcode'] == "ashc" :
        print "not implement!"
      elif instruction['opcode'] == "xor" :
        print "not implement!"
      elif instruction['opcode'] == "mov" :
        result = self.getSrc()
        if self.operation_mode == "byte" :
          if result&0x80 :
            result |= 0xff00
          else :
            result &= 0x00ff
        self.setDst(result)

        if (result&0xffff) >= 0x8000 :
          self.condition_code['n'] = True
        else :
          self.condition_code['n'] = False

        if (result&0xffff) == 0 :
          self.condition_code['z'] = True
        else :
          self.condition_code['z'] = False

        self.condition_code['v'] = False

      elif instruction['opcode'] == "add" :
        result = self.getSrc()+self.getDst()
        self.setDst(result)

        if result < 0 :
          self.condition_code['n'] = True
        else :
          self.condition_code['n'] = False
        if result == 0 :
          self.condition_code['z'] = True
        else :
          self.condition_code['z'] = False
        if (((0x8000 & self.getSrc()) != (0x8000 & self.getDst())) and
            ((0x8000 & result) == (0x8000 & self.getDst()))) :
          self.condition_code['v'] = True
        else :
          self.condition_code['v'] = False
        if result < 0x10000:
          self.condition_code['c'] = True
        else :
          self.condition_code['c'] = False

      elif instruction['opcode'] == "sub" :
        result = self.getDst()-self.getSrc()
        self.setDst(result)

        if result < 0 :
          self.condition_code['n'] = True
        else :
          self.condition_code['n'] = False
        if result == 0 :
          self.condition_code['z'] = True
        else :
          self.condition_code['z'] = False
        if (((0x8000 & self.getSrc()) != (0x8000 & self.getDst())) and
            ((0x8000 & result) == (0x8000 & self.getDst()))) :
          self.condition_code['v'] = True
        else :
          self.condition_code['v'] = False
        if result > 0xffff:
          self.condition_code['c'] = True
        else :
          self.condition_code['c'] = False

      elif instruction['opcode'] == "cmp" :
        if self.operation_mode == "byte" :
          result = self.getSrc()+((-self.getDst())&0xff)
          if (result&0xff) > 0x80 :
            self.condition_code['n'] = True
          else :
            self.condition_code['n'] = False

          if (result&0xff) == 0 :
            self.condition_code['z'] = True
          else :
            self.condition_code['z'] = False

          if (((0x80 & self.getSrc()) != (0x80 & self.getDst())) and
              ((0x80 & result) == (0x80 & self.getDst()))) :
            self.condition_code['v'] = True
          else :
            self.condition_code['v'] = False

          if result < 0x100:
            self.condition_code['c'] = True
          else :
            self.condition_code['c'] = False
        else :
          result = self.getSrc()+((-self.getDst())&0xffff)

          if (result&0xffff) >= 0x8000 :
            self.condition_code['n'] = True
          else :
            self.condition_code['n'] = False

          if (result&0xffff) == 0 :
            self.condition_code['z'] = True
          else :
            self.condition_code['z'] = False

          if (((0x8000 & self.getSrc()) != (0x8000 & self.getDst())) and
              ((0x8000 & result) == (0x8000 & self.getDst()))) :
            self.condition_code['v'] = True
          else :
            self.condition_code['v'] = False

          if result < 0x10000:
            self.condition_code['c'] = True
          else :
            self.condition_code['c'] = False

      elif instruction['opcode'] == "bis" :
        print "not implement!"
      elif instruction['opcode'] == "bic" :
        result = (~self.getSrc())&self.getDst()
        self.setDst(result)

        if (result&0x8000) >= 0x8000 :
          self.condition_code['n'] = True
        else :
          self.condition_code['n'] = False

        if (result&0xffff) == 0 :
          self.condition_code['z'] = True
        else :
          self.condition_code['z'] = False

        self.condition_code['v'] = False

        self.condition_code['c'] = True

      elif instruction['opcode'] == "bit" :
        print "not implement!"
      elif instruction['opcode'] == "br" :
        self.registers[7] += 2*offset

      elif instruction['opcode'] == "bne" :
        if self.condition_code['z'] == False :
          self.registers[7] += 2*offset

      elif instruction['opcode'] == "beq" :
        if self.condition_code['z'] == True :
          self.registers[7] += 2*offset

      elif instruction['opcode'] == "bpl" :
        print "not implement!"
      elif instruction['opcode'] == "bmi" :
        print "not implement!"
      elif instruction['opcode'] == "bmi" :
        print "not implement!"
      elif instruction['opcode'] == "bvc" :
        print "not implement!"
      elif instruction['opcode'] == "bvs" :
        print "not implement!"
      elif instruction['opcode'] == "bcc" :
        if self.condition_code['c'] == False :
          self.registers[7] += 2*offset

      elif instruction['opcode'] == "bcs" :
        print "not implement!"
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
        print "not implement!"
      elif instruction['opcode'] == "jmp" :
        addr = self.operand['dst']['address']
        self.registers[7] = addr

      elif instruction['opcode'] == "sob" :
        result = self.registers[instruction['operand']['r']]-1
        self.registers[instruction['operand']['r']] = result
        addr = self.operand['dst']['address']

        if (result&0xffff) != 0 :
          self.registers[7] -= 2*addr

      elif instruction['opcode'] == "jsr" :
        addr = self.operand['dst']['address']
        self.push(self.registers[instruction['operand']['r']])
        self.registers[instruction['operand']['r']] = self.registers[7] 
        self.registers[7] = addr

      elif instruction['opcode'] == "rts" :
        self.registers[7] = self.registers[instruction['operand']['r']]
        self.registers[instruction['operand']['r']] = self.pop()

      elif instruction['opcode'] == "rti" :
        print "not implement!"
      elif instruction['opcode'] == "rpt" :
        print "not implement!"
      elif instruction['opcode'] == "iot" :
        print "not implement!"
      elif instruction['opcode'] == "sys" :
        x = instruction['operand']['x']
        y = instruction['operand']['y']
        z = instruction['operand']['z']
        self.sys((y<<2)+z)

      elif instruction['opcode'] == "rtt" :
        addr = self.pop()
        self.registers[7] = addr

      else :
        print "not implement!"
    else :
      self.registers[7] += 2

  def run(self, argv) :
    argv_ = []
    argv_ += [len(argv)&0xff, (len(argv)>>8)&0xff]
    address = 0x10000
    for arg in argv :
      address -= len(arg)+1
      argv_ += [address&0xff, (address>>8)&0xff]
    argv_ += map(ord, '\0'.join(reversed(argv))+'\0')

    self.memory.load(argv_, 0x10000-len(argv_))
    self.registers[6] = 0x10000-len(argv_)
    
    while True :
      self.step()

  def printState(self) :
    print("%04x,%04x,%04x,%04x,%04x,%04x,sp=%04x,pc=%04x: %s"%
      (self.registers[0],
       self.registers[1],
       self.registers[2],
       self.registers[3],
       self.registers[4],
       self.registers[5],
       self.registers[6],
       self.registers[7],
       pdp11_disassem.getMnemonic(self.memory[:], self.registers[7])[0]))

if __name__ == '__main__':
  vm = VM()
  vm.loadAout('/usr/local/v6root/bin/nm');
  vm.run(['a.out'])
  #vm.run(['arg1', 'arg2', 'arg3', 'arg4'])
  #vm.run([])
