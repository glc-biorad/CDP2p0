POLYNOMIAL = 0x11021 #0x1021
PRESET = 0

def _initial(c):
    crc = 0
    c = c << 8
    for j in range(8):
        if (crc ^ c) & 0x8000:
            crc = (crc << 1) ^ POLYNOMIAL
        else:
            crc = crc << 1
        c = c << 1
    return crc

_tab = [ _initial(i) for i in range(256) ]

def _update_crc(crc, c):
    cc = 0xff & c

    tmp = (crc >> 8) ^ cc
    crc = (crc << 8) ^ _tab[tmp & 0xff]
    crc = crc & 0xffff
    #print (crc)

    return crc

def crc(str):
    crc = PRESET
    for c in str:
        crc = _update_crc(crc, ord(c))
    return crc

def crcb(*i):
    crc = PRESET
    for c in i:
        crc = _update_crc(crc, c)
    return crc

def crc16_ccitt(crc, data):
    msb = crc >> 8
    lsb = crc & 255
    for c in data:
        x = ord(c) ^ msb
        x ^= (x >> 4)
        msb = (lsb ^ (x >> 3) ^ (x << 4)) & 255
        lsb = (x ^ (x << 5)) & 255
    return (msb << 8) + lsb

def compute_crc16_xmodem(input_data):
    checksum_int = crc(input_data)
    checksum_hex_str = hex(checksum_int)
    checksum_str = checksum_hex_str[2:]
    if len(checksum_str) == 3:
        checksum_str = '0' + checksum_str
    elif len(checksum_str) == 2:
        checksum_str = '00' + checksum_str
    elif len(checksum_str) == 1:
        checksum_str = '000' + checksum_str
    return checksum_str.upper()

if __name__ == '__main__':
    #print(crc('123456789'))
    cs = crc('#060006?VR03F201')
    print(cs)
    print(type(hex(cs)))
    print(hex(cs))
    print(hex(cs)[2:])
