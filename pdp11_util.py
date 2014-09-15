# -*- coding: utf-8 -*-

def uint6toint6(n) :
  if n >= 0x20: n -= 0x40
  return n

def uint8toint8(n) :
  if n >= 0x80: n -= 0x100
  return n

def uint16toint16(n) :
  if n >= 0x8000 : n -= 0x10000
  return n

def bitshift_uint16(n, b) :
  if 0 <= b :
    return (n<<b)&0xffff
  else :
    if is_negative(n, 16) :
      return (n>>abs(b))&0xffff|(((1<<abs(b))-1)<<(16-abs(b)))
    else :
      return (n>>abs(b))&0xffff

def is_negative(n, b) :
  return bool(n&(1<<(b-1)))

def is_zero(n, b) :
  return (n&((1<<b)-1)) == 0

