# -*- coding: utf-8 -*-

import pdp11_decode
import pdp11_aout

def getMnemonic(code, ptr) :
  instruction = pdp11_decode.searchMatchInstructionFormat(code, ptr)

  if not instruction :
    mnemonic = "unknown"
    ptr += 2
  else :
    mnemonic = "%s\t"%instruction['opcode']
    ptr += instruction['size']

    if 's' in instruction['operand'] :
      s = instruction['operand']['s']
      if (s&0x07) == 0x07 :
        if (s>>3) == 2 :
          mnemonic += "$%o"%((code[ptr+1]<<8)+code[ptr])
          ptr += 2
        elif (s>>3) == 3 :
          mnemonic += "*$%o"%((code[ptr+1]<<8)+code[ptr])
          ptr += 2
        elif (s>>3) == 6 :
          mnemonic += "%o"%((code[ptr+1]<<8)+code[ptr]+ptr+2)
          ptr += 2
        elif (s>>3) == 7 :
          mnemonic += "*$0x%x"%((code[ptr+1]<<8)+code[ptr]+ptr+2)
          ptr += 2
        else :
          pass
      else :
        if (s>>3) == 0 :
          mnemonic += "r%d"%(s&0x07)
        elif (s>>3) == 1 :
          mnemonic += "(r%d)"%(s&0x07)
        elif (s>>3) == 2 :
          mnemonic += "(r%d)+"%(s&0x07)
        elif (s>>3) == 3 :
          mnemonic += "*(r%d)+"%(s&0x07)
        elif (s>>3) == 4 :
          mnemonic += "-(r%d)"%(s&0x07)
        elif (s>>3) == 5 :
          mnemonic += "*-(r%d)"%(s&0x07)
        elif (s>>3) == 6 :
          mnemonic += "%o(r%d)"%((code[ptr+1]<<8)+code[ptr], s&0x07)
          ptr += 2
        elif (s>>3) == 7 :
          mnemonic += "*%o(r%d)"%((code[ptr+1]<<8)+code[ptr], s&0x07)
          ptr += 2
        else :
          pass
      mnemonic += ', '
    if 'd' in instruction['operand'] :
      d = instruction['operand']['d']
      if (d&0x07) == 0x07 :
        if (d>>3) == 2 :
          mnemonic += "$%o"%((code[ptr+1]<<8)+code[ptr])
          ptr += 2
        elif (d>>3) == 3 :
          mnemonic += "*$%o"%((code[ptr+1]<<8)+code[ptr])
          ptr += 2
        elif (d>>3) == 6 :
          mnemonic += "%o"%((code[ptr+1]<<8)+code[ptr]+ptr+2)
          ptr += 2
        elif (d>>3) == 7 :
          mnemonic += "@%o"%((code[ptr+1]<<8)+code[ptr])
          ptr += 2
        else :
          pass
      else :
        if (d>>3) == 0 :
          mnemonic += "r%d"%(d&0x07)
        elif (d>>3) == 1 :
          mnemonic += "(r%d)"%(d&0x07)
        elif (d>>3) == 2 :
          mnemonic += "(r%d)+"%(d&0x07)
        elif (d>>3) == 3 :
          mnemonic += "*(r%d)+"%(d&0x07)
        elif (d>>3) == 4 :
          mnemonic += "-(r%d)"%(d&0x07)
        elif (d>>3) == 5 :
          mnemonic += "*-(r%d)"%(d&0x07)
        elif (d>>3) == 6 :
          mnemonic += "%o(r%d)"%((code[ptr+1]<<8)+code[ptr], d&0x07)
          ptr += 2
        elif (d>>3) == 7 :
          mnemonic += "*%o(r%d)"%((code[ptr+1]<<8)+code[ptr], d&0x07)
          ptr += 2
        else :
          pass
    if 'r' in instruction['operand'] :
      r = instruction['operand']['r']
      mnemonic += "r%d"%(r)
      mnemonic += ", "
    if 'a' in instruction['operand'] :
      a = instruction['operand']['a']
      if (a&0x07) == 0x07 :
        if (a>>3) == 2 :
          mnemonic += "$%o"%((code[ptr+1]<<8)+code[ptr])
          ptr += 2
        elif (a>>3) == 3 :
          mnemonic += "*$%o"%((code[ptr+1]<<8)+code[ptr])
          ptr += 2
        elif (a>>3) == 6 :
          mnemonic += "0x%x"%((code[ptr+1]<<8)+code[ptr]+ptr+2)
          ptr += 2
        elif (a>>3) == 7 :
          mnemonic += "*$0x%x"%((code[ptr+1]<<8)+code[ptr]+ptr+2)
          ptr += 2
        else :
          pass
      else :
        if (a>>3) == 0 or (a>>3) == 1 :
          mnemonic += "r%d"%(a&0x07)
        elif (a>>3) == 2 or (a>>3) == 3 :
          mnemonic += "(r%d)+"%(a&0x07)
        elif (a>>3) == 4 or (a>>3) == 5 :
          mnemonic += "-(r%d)"%(a&0x07)
        elif (a>>3) == 6 or (a>>3) == 7 :
          mnemonic += "%o(r%d)"%((code[ptr+1]<<8)+code[ptr], a&0x07)
          ptr += 2
        else :
          pass
    if 'o' in instruction['operand'] :
      o = instruction['operand']['o']
      mnemonic += "0x%x"%(ptr + o*2)
  
    if 'x' in instruction['operand'] :
      x = instruction['operand']['x']
      y = instruction['operand']['y']
      z = instruction['operand']['z']
      mnemonic += "%o"%((y<<2)+z)

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
      print "%s:"%([k for (k, v) in aout['syms']['file_table'].items() if v['address'] == ptr][0])
    except IndexError:
      pass

    try :
      symbols = [k for (k, v) in aout['syms']['symbol_table'].items() if v['address'] == ptr]
      for symbol in symbols :
        print "%s:"%(symbol)
        for (k, v) in aout['syms']['symbol_table'][symbol]['local_symbol_table'].items() :
          print("\t\t%s(r5):%s"%(oct(v['address'])[1:], k))
    except IndexError:
      pass

    d = getDisassem(code, ptr)
    disassem = d[0]
    next_ptr = d[1]
    
    print disassem

    ptr = next_ptr

if __name__ == '__main__':
  f = open('a.out', 'rb')
  program = map(ord, f.read())
  printDisassembler(program)
