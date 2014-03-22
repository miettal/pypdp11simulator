# -*- coding: utf-8 -*-

instruction_table = {
  "[0]00000": "halt",
  "[0]00001": "wait",
  "[0]00005": "reset",
  "[0]00240": "nop",
  "[*]050dd": "clr",
  "[*]052dd": "inc",
  "[*]053dd": "dec",
  "[*]055dd": "adc",
  "[*]056dd": "sbc",
  "[*]057dd": "tst",
  "[*]054dd": "neg",
  "[*]051dd": "com",
  "[*]060dd": "ror",
  "[*]061dd": "rol",
  "[*]062dd": "asr",
  "[*]063dd": "asl",
  "[0]003dd": "swab",
  "[0]067dd": "sxt",
  "[0]70rss": "mul",
  "[0]71rss": "div",
  "[0]72rss": "ash",
  "[0]73rss": "ashc",
  "[0]74rdd": "xor",
  "[*]1ssdd": "mov",
  "[0]6ssdd": "add",
  "[1]6ssdd": "sub",
  "[*]2ssdd": "cmp",
  "[*]5ssdd": "bis",
  "[*]4ssdd": "bic",
  "[*]3ssdd": "bit",
  "[00000001][oooooooo]": "br",
  "[00000010][oooooooo]": "bne",
  "[00000011][oooooooo]": "beq",
  "[10000000][oooooooo]": "bpl",
  "[10000001][oooooooo]": "bmi",
  "[10000001][oooooooo]": "bmi",
  "[10000100][oooooooo]": "bvc",
  "[10000101][oooooooo]": "bvs",
  "[10000110][oooooooo]": "bcc",
  "[10000111][oooooooo]": "bcs",
  "[00000100][oooooooo]": "bge",
  "[00000101][oooooooo]": "blt",
  "[00000110][oooooooo]": "bgt",
  "[00000111][oooooooo]": "ble",
  "[10000010][oooooooo]": "bhi",
  "[10000011][oooooooo]": "blos",
  "[0]001dd": "jmp",
  "[0]77rdd": "sob",
  "[0]04rdd": "jsr",
  "[0]0020r": "rts",
  "[0]00002": "rti",
  "[0]00003": "rpt",
  "[0]00004": "iot",
  "[1]04xyz": "sys",
  "[0]00004": "rtt",
}

def searchMatchInstructionFormat(code, ptr) :
  for (fmt, opcode) in instruction_table.items() :
    m = matchInstructionFormat(code, ptr, fmt)
    if m:
      return {'opcode':opcode, 'operand':m['operand'], 'size':m['size']}
  else :
    return None

def matchInstructionFormat(code, ptr, fmt) :
  bit_index = 0
  bit_mode = False
  operand = {}

  for ch in fmt :
    if ch == '[' :
      bit_mode = True
    elif ch == ']' :
      bit_mode = False
    elif bit_mode :
      value = (code[ptr+bit_index/8+(-1 if (bit_index/8)%2 else 1)]>>(7-bit_index%8) & 0x01)
      bit_index += 1
      try :
        if int(ch) != value :
          return False
      except ValueError:
        try :
          operand[ch] <<= 1
          operand[ch] += value
        except KeyError :
          operand[ch] = value
    else :
      value = (code[ptr+bit_index/8+(-1 if (bit_index/8)%2 else 1)]>>(7-bit_index%8) & 0x01)
      bit_index += 1
      value <<= 1
      value += (code[ptr+bit_index/8+(-1 if (bit_index/8)%2 else 1)]>>(7-bit_index%8) & 0x01)
      bit_index += 1
      value <<= 1
      value += (code[ptr+bit_index/8+(-1 if (bit_index/8)%2 else 1)]>>(7-bit_index%8) & 0x01)
      bit_index += 1

      try :
        if int(ch, 8) != value :
          return False
      except ValueError :
        try :
          operand[ch] <<= 3
          operand[ch] += value
        except KeyError :
          operand[ch] = value
            
  return {'operand':operand, 'size':bit_index/8}

