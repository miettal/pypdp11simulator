# -*- coding: utf-8 -*-

def uint6toint6(n) :
  if n > 0x20: n -= 0x40
  return n

def uint8toint8(n) :
  if n > 0x80: n -= 0x100
  return n

def uint16toint16(n) :
  if n > 0x8000 : n -= 0x10000
  return n

def bitshift_uint16(n, b) :
  n = uint16toint16(n)
  if b >= 0 :
    return (n<<b)&0xffff
  else :
    return (n>>abs(b))&0xffff
