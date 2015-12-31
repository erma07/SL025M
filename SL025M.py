#!/usr/bin/python

#http://www.stronglink-rfid.com/download/SL025M-User-Manual.pdf

import serial

def SELECT_RFID_CARD_SL025M (port,baudrate,timeout):

	ser = serial.Serial(
    		port=port,
   	 	baudrate=baudrate,
    		parity=serial.PARITY_NONE,
    		stopbits=serial.STOPBITS_ONE,
    		bytesize=serial.EIGHTBITS,
		timeout=timeout
	)

	TYPES= {b'\x01' : 'Mifare 1k, 4 byte UID',
		b'\x02' : 'Mifare 1k, 7 byte UID',
		b'\x03' : 'Mifare UltraLight or NATG203, 7 byte UID',
                b'\x04' : 'Mifare 4k, 4 byte UID',
                b'\x05' : 'Mifare 4k, 7 byte UID',
                b'\x06' : 'Mifare DesFire, 7 byte UID',
                b'\x0A' : 'Other'}

	lrc = 0

	SELECTCMD=bytearray(b'\xBA\x02\x01')

	for v in SELECTCMD:
		lrc ^= v
		ser.write(chr(v))
	
	ser.write(chr(lrc))
		
	values = bytearray()

	values.append(ser.read())

	if chr(values[len(values)-1]) == b'\xBD':

		values.append(ser.read())

		length = values[len(values)-1]

		RFID = ""

		for num in range(0,length):

			values.append(ser.read())

			string = values[len(values)-1]

			if num == 0:
				continue
			elif num == 1:
				if chr(string) == b'\x00':
					continue
				else:
					if chr(string) == b'\x01':
						return "ERR","no card present", chr(string).encode("hex")
					elif chr(string) == b'\xF0':
						return "ERR","checksum", chr(string).encode("hex")
					else:
						return "ERR","unknown", chr(string).encode("hex")
					break

			elif num + 2 > length:
				lrc = 0

				for n in range(0,length+1):
					lrc ^= values[n]

				if string != lrc:
					return "ERR","recv_checksum", chr(string).encode("hex"), chr(lrc).encode("hex")
					break

			elif num + 3 > length:
				type = string
			else:
				RFID += chr(string).encode("hex")

		return "RFID",RFID.upper(),"TYPE",type,TYPES[chr(type)] 
	else:
		return "ERR","port_conn","connecting port", port


print SELECT_RFID_CARD_SL025M ("/dev/ttyUSB0",115200,3)
