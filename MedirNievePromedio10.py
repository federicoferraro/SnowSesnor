#EJECUTAR CON PYTHON3
#Pegar una muestra en el servidor de new.omixom.com

#!/usr/bin/python

import requests	#Importo requests para realizar la petición get
import json	
import smbus
import time
import datetime
from time import time
from serial import Serial
from gpiozero import OutputDevice
from time import sleep

SensorOnOff = OutputDevice(10)

fondo = 1943#324
maxAlt = 45#294

address = 0x48
A1 = 0x01       # A0=0x00(IN adc),A1=0x01(pote),A2=0x02(LDR) y A3=0x03
#bus = smbus.SMBus(0)
cont=0;prom=0;title=1;lecture=0

numero_serie = 25996

serialDevice = "/dev/ttyAMA0" # default for RaspberryPi ZERO W hay que sacarla del BT y aputarla al serial 0
maxwait = 1 # seconds to try for a good reading before quitting

SensorOnOff.on()
sleep(1)

def measure(portName):
    ser = Serial(portName, 9600, 8, 'N', 1, timeout=1)
    timeStart = time()
    valueCount = 0


    while time() < timeStart + maxwait:
        if ser.inWaiting():
            bytesToRead = ser.inWaiting()
            valueCount += 1
            if valueCount < 2: # 1st reading may be partial number; throw it out
                continue
            testData = ser.read(bytesToRead)
            if not testData.startswith(b'R'):
                # data received did not start with R
                continue
            try:
                sensorData = testData.decode('utf-8').lstrip('R')
            except UnicodeDecodeError:
                # data received could not be decoded properly
                continue
            try:
                mm = int(sensorData)
            except ValueError:
                # value is not a number
                continue
            ser.close()
            return(mm)

    ser.close()
    raise RuntimeError("Expected serial data not received")

if __name__ == '__main__':
#    measurement = measure(serialDevice)
#    print("distance =",measurement)
	
	
	measurementAc = 0
	
	for i in [1,2,3,4,5]:
		measurement = measure(serialDevice)
		measurementAc = measurementAc + measurement
#		print("ciclo =",i)
#		print("distance =",measurement)
		print('ciclo: {0}, distance: {1}'.format(i, measurement))
		
	print("distancia acumulada =",measurementAc)
	measurement = measurementAc/5
	print("distancia promedio =",measurement)
	
	lecture = int(measurement)

sleep(1)
SensorOnOff.off()
	
#valor = round((((lecture-150)/(48-150))*14),2)
#valor = round(((fondo - int(measurement))/maxAlt)*100,1)
valor = round((fondo - int(measurement)),1)
archive = open("datos_sensor.txt","a") #El flag "a" es para reescribir el txt sin borrar lo demas
if title == 1:
	archive.write("---------- Datos sensor ----------\n")
	title = 0
archive.write("{} - Valor: {}\n".format(datetime.datetime.now(),valor))	#a este datetime lo dejo asi porque es el real, el otro es para que quede bien en new ya que esta adelantado utc+3
print("Nivel de Nieve: {} mm".format(valor))
print("Valor del Sensor: {}".format(lecture))
hora_local = datetime.timezone(datetime.timedelta(hours=0))	#Me va a mostrar 3 horas adelantadas pero asi queda en hora en new.
dateutc = datetime.datetime.now(hora_local).strftime('%Y-%m-%d %H:%M:%S')
print(dateutc)
parametros = {'nivel_nieve':[lecture],'dateutc':[dateutc]}	#OK - envio el adc a new. Alla aplico la FT para el calculo.
url = 'https://new.omixom.com/weatherstation/updateweatherstation.jsp?ID='+str(numero_serie)+'&PASSWORD=vwrnlDhZtz'
r = requests.get(url,params=parametros)
print(r)
if r.status_code == 201:
	print("TRAMA RECIBIDA OK")
else:
	print("ERROR")

