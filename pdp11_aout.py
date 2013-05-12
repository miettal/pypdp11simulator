# -*- coding: utf-8 -*-

def littleEndian2int(byte_list) :
  val = 0
  for x in byte_list[::-1] :
    val <<= 8
    val += x

  return val

def split_seq(seq, size):
  return [seq[i:i+size] for i in range(0, len(seq), size)]

def getAoutHeader(program) :
  header = {}
  header['a_magic'] = littleEndian2int(program[:2])
  header['a_text'] = littleEndian2int(program[2:4])
  header['a_data'] = littleEndian2int(program[4:6])
  header['a_bss'] = littleEndian2int(program[6:8])
  header['a_syms'] = littleEndian2int(program[8:10])
  header['a_entry'] = littleEndian2int(program[10:12])
  header['a_strsize'] = littleEndian2int(program[12:14])
  header['a_drsize'] = littleEndian2int(program[14:16])

  return header

def getV6AoutSyms(a_syms) :
  symbol_table = {}
  file_table = {}
  for entry in split_seq(a_syms, 12) :
    symbol = ''
    for b in entry[:8] :
      if b :
        symbol += chr(b)
    symbol_type = littleEndian2int(entry[8:10])
    address = littleEndian2int(entry[10:12])

    if symbol_type == 1 :
      symbol_table[last_symbol]['local_symbol_table'][symbol] = {'address':address, 'symbol_type':symbol_type}
    elif symbol_type == 31 :
      last_filename = symbol
      file_table[last_filename] = {'address':address, 'symbols':[]}
    else :
      last_symbol = symbol
      symbol_table[last_symbol] = {'address':address, 'symbol_type':symbol_type, 'local_symbol_table':{}}
      file_table[last_filename]['symbols'].append(symbol)

  return {'symbol_table':symbol_table, 'file_table':file_table}

def getAout(program) :
  aout = {}

  aout['header'] = getAoutHeader(program[:16])
  program = program[16:]

  aout['text'] = program[:aout['header']['a_text']]
  program = program[aout['header']['a_text']:]

  aout['data'] = program[:aout['header']['a_data']]
  program = program[aout['header']['a_data']:]

  aout['syms'] = getV6AoutSyms(program[:aout['header']['a_syms']])
  program = program[aout['header']['a_syms']:]

  return aout
