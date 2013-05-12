# -*- coding: utf-8 -*-
import sys
import pprint

import pdp11_aout
import pdp11_decode
import pdp11_disassem
import pdp11_registers
import pdp11_memory

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
                    'addr': {
                      'value': None,
                      'addressing': None,
                      'address': None,
                    },
    }

  def loadAout(self, filename) :
    f = open('a.out', 'rb')
    program = map(ord, f.read())
    aout = pdp11_aout.getAout(program)

    self.memory.load(aout['text'] + aout['data'])
    self.registers[6] = 0xfff6
    self.registers[7] = aout['header']['a_entry']

  def getOperand(self, direction) :
    if self.operation_mode == "byte" :
      self.registers.setMode("byte")
      self.memory.setMode("byte")

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
  def getAddr(self) : return self.getOperand('addr')

  def setOperand(self, value, direction) :
    if self.operation_mode == "byte" :
      self.registers.setMode("byte")
      self.memory.setMode("byte")

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
    if num == 0 :
      pc = self.registers[7]
      self.registers[7] = self.memory[self.registers[7]]
      self.step()
      self.registers[7] = pc
      self.registers[7] += 2
    elif num == 1 :
      sys.exit()
    elif num == 2 :
      print "not implement!"
    elif num == 3 :
      print "not implement!"
    elif num == 4 :
      addr = self.memory[self.registers[7]]
      size = self.memory[self.registers[7]+2]
      print ''.join(map(chr, self.memory[addr:addr+size]))
      self.registers[7] += 4
    elif num == 5 :
      print "not implement!"
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
    elif num == 11 :
      print "not implement!"
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

    instruction = pdp11_decode.searchMatchInstructionFormat(self.memory, self.registers[7])

    if instruction :
      self.registers[7] += instruction['size']

      for (key, value) in instruction['operand'].items() :
        if '*' == key :
          if value :
            self.operation_mode = "byte"
          else :
            self.operation_mode = "word"
        else :
          self.operation_mode = "word"

        if key in ['s', 'd', 'a' ] :
          if key == 's' : direction = 'src'
          elif key == 'd' : direction = 'dst'
          else : direction = 'addr'
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
              self.operand[direction]['address'] = self.registers[value&0x07] + self.memory[self.registers[7]]
              self.registers[7] += 2
            elif (value>>3) == 7 :
              self.operand[direction]['addressing'] = "index deferred"
              self.operand[direction]['address'] = self.registers[value&0x07] + self.memory[self.registers[7]]
              self.operand[direction]['address'] = self.memory[self.registers[value&0x07] + self.memory[self.registers[7]]]
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
              self.operand[direction]['address'] = self.memory[self.registers[7]] + self.registers[7] + 2
              self.registers[7] += 2
            elif (value>>3) == 7 :
              self.operand[direction]['addressing'] = "relative indirect"
              self.operand[direction]['address'] = self.memory[self.memory[self.registers[7]] + self.registers[7] + 2]
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
        self.condition_code['n'] = False
        self.condition_code['z'] = True
        self.condition_code['v'] = False
        self.condition_code['c'] = False
      elif instruction['opcode'] == "inc" :
        v = self.getAddr()+1
        self.setAddr(v)

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
        v = self.getAddr()-1
        self.setAddr(v)

        if (0xffff & v) > 0x7fff :
          self.condition_code['n'] = True
        else :
          self.condition_code['n'] = False
        if (0xffff & v) == 0 :
          self.condition_code['z'] = True
        else :
          self.condition_code['z'] = False
        if (0xffff & v) == 0x8000 :
          self.condition_code['v'] = True
        else :
          self.condition_code['v'] = False
      elif instruction['opcode'] == "adc" :
        print "not implement!"
      elif instruction['opcode'] == "sbc" :
        print "not implement!"
      elif instruction['opcode'] == "tst" :
        addr = self.operand['addr']['address']
        self.memory[addr]
        #TODO change condition code
      elif instruction['opcode'] == "neg" :
        print "not implement!"
      elif instruction['opcode'] == "com" :
        print "not implement!"
      elif instruction['opcode'] == "ror" :
        print "not implement!"
      elif instruction['opcode'] == "rol" :
        print "not implement!"
      elif instruction['opcode'] == "asr" :
        print "not implement!"
      elif instruction['opcode'] == "asl" :
        print "not implement!"
      elif instruction['opcode'] == "swab" :
        print "not implement!"
      elif instruction['opcode'] == "sxt" :
        print "not implement!"
      elif instruction['opcode'] == "mul" :
        print "not implement!"
      elif instruction['opcode'] == "mul" :
        print "not implement!"
      elif instruction['opcode'] == "div" :
        print "not implement!"
      elif instruction['opcode'] == "ash" :
        print "not implement!"
      elif instruction['opcode'] == "ashc" :
        print "not implement!"
      elif instruction['opcode'] == "xor" :
        print "not implement!"
      elif instruction['opcode'] == "mov" :
        self.setDst(self.getSrc())

        if self.getDst() > 0x7fff :
          self.condition_code['n'] = True
        else :
          self.condition_code['n'] = False
        if self.getDst() == 0:
          self.condition_code['z'] = True
        else :
          self.condition_code['z'] = False
        self.condition_code['v'] = False
      elif instruction['opcode'] == "add" :
        print "not implement!"
      elif instruction['opcode'] == "sub" :
        self.setDst(self.getDst() - self.getSrc())
      elif instruction['opcode'] == "cmp" :
        if (0xffff & (self.getDst() + self.getSrc())) > 0x7fff :
          self.condition_code['n'] = True
        else :
          self.condition_code['n'] = False
        if (0xffff & (self.getDst() + self.getSrc())) == 0 :
          self.condition_code['z'] = True
        else :
          self.condition_code['z'] = False
        if (((0x8000 & self.getSrc()) != (0x8000 & self.getDst())) and
            ((0x8000 & (self.getDst() + self.getSrc())) == (0x8000 & self.getDst()))) :
          self.condition_code['v'] = True
        else :
          self.condition_code['v'] = False
        if (self.getDst() + self.getSrc()) < 0xffff :
          self.condition_code['c'] = True
        else :
          self.condition_code['c'] = False

      elif instruction['opcode'] == "bis" :
        print "not implement!"
      elif instruction['opcode'] == "bic" :
        print "not implement!"
      elif instruction['opcode'] == "bit" :
        print "not implement!"
      elif instruction['opcode'] == "br" :
        print "not implement!"
      elif instruction['opcode'] == "bne" :
        if self.condition_code['z'] == False :
          self.registers[7] += 2*instruction['operand']['o']
      elif instruction['opcode'] == "beq" :
        #print "%04X"%(self.memory[self.registers[7]-2])
        if self.condition_code['z'] == True :
          self.registers[7] += 2*instruction['operand']['o']
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
          self.registers[7] += 2*instruction['operand']['o']
      elif instruction['opcode'] == "bcs" :
        print "not implement!"
      elif instruction['opcode'] == "bge" :
        print "not implement!"
      elif instruction['opcode'] == "blt" :
        print "not implement!"
      elif instruction['opcode'] == "bgt" :
        if ( self.condition_code['z'] or
             (self.condition_code['n'] != self.condition_code['v'])) == False :
          self.registers[7] += 2*instruction['operand']['o']
      elif instruction['opcode'] == "ble" :
        print "not implement!"
      elif instruction['opcode'] == "bhi" :
        if ( self.condition_code['c'] == False and
             self.condition_code['z'] == False ) :
          self.registers[7] += 2*instruction['operand']['o']
      elif instruction['opcode'] == "blos" :
        print "not implement!"
      elif instruction['opcode'] == "jmp" :
        addr = self.operand['addr']['address']
        self.registers[7] = addr
      elif instruction['opcode'] == "sob" :
        print "not implement!"
      elif instruction['opcode'] == "jsr" :
        addr = self.operand['addr']['address']
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
        pass
    else :
      self.registers[7] += 2

  def run(self) :
    while True :
      self.step()

if __name__ == '__main__':
  vm = VM()
  vm.loadAout('a.out');
  vm.run()
