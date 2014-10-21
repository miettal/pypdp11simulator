# -*- coding: utf-8 -*-

import pdp11_decode
import pdp11_aout
import pdp11_util

def getMnemonic(instruction, code, ptr) :

  if not instruction :
    mnemonic = "unknown"
    ptr += 2
  else :
    mnemonic = ""
    mnemonic += "%s"%instruction['opcode']
    ptr += instruction['size']

    op_num = 0

    if '*' in instruction['operand'] :
      byte_mode = instruction['operand']['*']
      if byte_mode :
        mnemonic += "b"

    if 's' in instruction['operand'] :
      if op_num == 0 : mnemonic += " "
      if 1 <= op_num : mnemonic += ", "
      op_num += 1
      s = instruction['operand']['s']
      if (s&0x07) == 0x07 :
        if (s>>3) == 2 :
          mnemonic += "$%x"%(((code[ptr+1]<<8)+code[ptr])&0xffff)
          ptr += 2
        elif (s>>3) == 3 :
          mnemonic += "*$%04x"%(((code[ptr+1]<<8)+code[ptr])&0xffff)
          ptr += 2
        elif (s>>3) == 6 :
          mnemonic += "%04x"%(((code[ptr+1]<<8)+code[ptr]+ptr+2)&0xffff)
          ptr += 2
        elif (s>>3) == 7 :
          mnemonic += "*%04x"%(((code[ptr+1]<<8)+code[ptr]+ptr+2)&0xffff)
          ptr += 2
        else :
          pass
      else :
        if (s>>3) == 0 :
          mnemonic += "%s"%(register_name(s&(0x07)))
        elif (s>>3) == 1 :
          mnemonic += "(%s)"%(register_name(s&(0x07)))
        elif (s>>3) == 2 :
          mnemonic += "(%s)+"%(register_name(s&(0x07)))
        elif (s>>3) == 3 :
          mnemonic += "*(%s)+"%(register_name(s&(0x07)))
        elif (s>>3) == 4 :
          mnemonic += "-(%s)"%(register_name(s&(0x07)))
        elif (s>>3) == 5 :
          mnemonic += "*-(%s)"%(register_name(s&(0x07)))
        elif (s>>3) == 6 :
          disp = pdp11_util.uint16toint16((code[ptr+1]<<8)+code[ptr])
          mnemonic += "%x(%s)"%(disp, register_name(s&(0x07)))
          ptr += 2
        elif (s>>3) == 7 :
          disp = pdp11_util.uint16toint16((code[ptr+1]<<8)+code[ptr])
          mnemonic += "*%x(%s)"%(disp, register_name(s&(0x07)))
          ptr += 2
        else :
          pass

    if 'r' in instruction['operand'] :
      if op_num == 0 : mnemonic += " "
      if 1 <= op_num : mnemonic += ", "
      op_num += 1
      r = instruction['operand']['r']
      mnemonic += "%s"%(register_name(r))

    if 'd' in instruction['operand'] :
      if op_num == 0 : mnemonic += " "
      if 1 <= op_num : mnemonic += ", "
      op_num += 1
      d = instruction['operand']['d']
      if instruction['opcode'] == "sob" :
        mnemonic += "%d"%d
      elif (d&0x07) == 0x07 :
        if (d>>3) == 2 :
          mnemonic += "$%x"%(((code[ptr+1]<<8)+code[ptr])&0xffff)
          ptr += 2
        elif (d>>3) == 3 :
          mnemonic += "*$%04x"%(((code[ptr+1]<<8)+code[ptr])&0xffff)
          ptr += 2
        elif (d>>3) == 6 :
          mnemonic += "%04x"%(((code[ptr+1]<<8)+code[ptr]+ptr+2)&0xffff)
          ptr += 2
        elif (d>>3) == 7 :
          mnemonic += "*%04x"%((ptr+(code[ptr+1]<<8)+code[ptr]+2)&0xffff)
          ptr += 2
        else :
          pass
      else :
        if (d>>3) == 0 :
          mnemonic += "%s"%(register_name(d&(0x07)))
        elif (d>>3) == 1 :
          mnemonic += "(%s)"%(register_name(d&(0x07)))
        elif (d>>3) == 2 :
          mnemonic += "(%s)+"%(register_name(d&(0x07)))
        elif (d>>3) == 3 :
          mnemonic += "*(%s)+"%(register_name(d&(0x07)))
        elif (d>>3) == 4 :
          mnemonic += "-(%s)"%(register_name(d&(0x07)))
        elif (d>>3) == 5 :
          mnemonic += "*-(%s)"%(register_name(d&(0x07)))
        elif (d>>3) == 6 :
          disp = pdp11_util.uint16toint16((code[ptr+1]<<8)+code[ptr])
          mnemonic += "%x(%s)"%(disp, register_name(d&(0x07)))
          ptr += 2
        elif (d>>3) == 7 :
          disp = pdp11_util.uint16toint16((code[ptr+1]<<8)+code[ptr])
          mnemonic += "*%x(%s)"%(disp, register_name(d&(0x07)))
          ptr += 2
        else :
          pass

    if 'o' in instruction['operand'] :
      if op_num == 0 : mnemonic += " "
      if 1 <= op_num : mnemonic += ", "
      op_num += 1
      offset = pdp11_util.uint8toint8(instruction['operand']['o'])
      mnemonic += "%04x"%(ptr + offset*2)
  
    if 'x' in instruction['operand'] :
      if op_num == 0 : mnemonic += " "
      if 1 <= op_num : mnemonic += ", "
      op_num += 1
      x = instruction['operand']['x']
      y = instruction['operand']['y']
      z = instruction['operand']['z']
      mnemonic += "%x"%((y<<3)+z)

  return (mnemonic, ptr)

def getDisassem(code, ptr) :
  m = getMnemonic(code, ptr)
  mnemonic = m[0]
  next_ptr = m[1]
  dump = ("%4x: ")%ptr
  for x in range(3) :
    if ptr < next_ptr :
      dump += "%02x%02x "%(code[ptr+1], code[ptr])
      ptr += 2
    else :
      dump += "     "
  disassem = "%s %s"%(dump, mnemonic)

  return (disassem, next_ptr)

def printDisassembler(program) :
  aout = pdp11_aout.getAout(program)

  code = aout['text']
  ptr = 0
  while ptr < len(code) :
    next_ptr = ptr
    try :
      print("%s:"%([k for (k, v) in list(aout['syms']['file_table'].items()) if v['address'] == ptr][0]))
    except IndexError:
      pass

    try :
      symbols = [k for (k, v) in list(aout['syms']['symbol_table'].items()) if v['address'] == ptr]
      for symbol in symbols :
        print("%s:"%(symbol))
        for (k, v) in list(aout['syms']['symbol_table'][symbol]['local_symbol_table'].items()) :
          print(("  %s(r5):%s"%(oct(v['address'])[1:], k)))
    except IndexError:
      pass

    d = getDisassem(code, ptr)
    disassem = d[0]
    next_ptr = d[1]
    
    print(disassem)

    ptr = next_ptr

def register_name(n) :
  if 0 <= n <= 5 :
    return "r%d"%n
  elif n == 6 :
    return "sp"
  else :
    return "pc"

if __name__ == '__main__':
  f = open('a.out', 'rb')
  program = list(map(ord, f.read()))
  printDisassembler(program)

