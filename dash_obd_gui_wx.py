import wx
import time
import random

import wx
import pdb
import obd_io  # OBD2 funcs
import os  # os.environ

from os.path import exists

import decimal
import glob

import threading
import sys
import serial
import platform
import time
import configparser  # safe application configuration
import webbrowser  # open browser from python
#from multiprocessing import Process
#from multiprocessing import Queue

from obd2_codes import pcodes
from obd2_codes import ptest

from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
import obd
from obd import OBDStatus

# index for sensor data stored

INDEX_RPM = 4
INDEX_SPEED = 1 
INDEX_COOLANT = 3
INDEX_FUEL = 2
INDEX_AIRTEMP = 8
INDEX_DISTANCE = 5
INDEX_FUEL_RATE = 6 

INDEX_STATUS = 7 


class GUI(wx.Frame):
   sensors = []
   portName = "AUTO"
   RECONNATTEMPTS = 5
   SERTIMEOUT = 5
   baudrate = "AUTO"
   fast = 'FAST'

   speedVal = 0;
   fuelVal = 0;
   rpmVal = 0;
   airTempVal = 0;
   distVal = 0;
   coolantVal = 0;
   
      
   LOG_FILENAME = "log.csv" 

   def __init__(self, parent, title):
      super(GUI, self).__init__(parent, title = title,size = (720, 680))

      self.InitUI()
      self.Centre()
      self.Show()

      
      if(self.connectToOBD() != 1):
         print("Couldnt connect");
         exit()

      self.update()
      
      self.setLogFileName();
      print(self.LOG_FILENAME)
      
   def setLogFileName(self):
      baseName = "log/OBD_LOG"      
      fileCnt = 0;
      while(fileCnt < 100):
         file_exists = exists(baseName + str(fileCnt) + ".csv")
         if(file_exists):
            fileCnt = fileCnt + 1;
         else:
            self.LOG_FILENAME = baseName + str(fileCnt) + ".csv"
            with open(self.LOG_FILENAME, "a") as log:
               log.write("{},{},{}\n".format("SPEED","RPM","FUEL","DIST","AIRTEMP","COOLANT"))
            break

   def writeToLogFile(self):
      with open(self.LOG_FILENAME, "a") as log:
         log.write("{},{},{}\n".format(self.speedVal, self.rpmVal, self.fuelVal,self.distVal,self.airTempVal,self.coolantVal))
      
   def initCommunication(self):
      self.connection = obd_io.OBDConnection(self.portName, self.baudrate, self.SERTIMEOUT, self.RECONNATTEMPTS, self.fast)
      if self.connection.connection.status() != 'Car Connected':  # Cant open serial port
         self.sensors[7].SetLabel("Cant Connect!")
         #wx.PostEvent(self._notify_window, StatusEvent([666]))  # signal apl, that communication was disconnected
         #wx.PostEvent(self._notify_window, StatusEvent([0, 1, "Error cant connect..."]))
         self.stop()
         return None
      else:
         self.sensors[7].SetLabel("Connected!")
         #wx.PostEvent(self._notify_window, DebugEvent([1, "Communication initialized..."]))
         #wx.PostEvent(self._notify_window, StatusEvent([0, 1, "Car connected!"]))

         r = self.connection.connection.query(obd.commands.ELM_VERSION)
         self.ELMver = str(r.value)
         self.protocol = self.connection.connection.protocol_name()

         #wx.PostEvent(self._notify_window, StatusEvent([2, 1, str(self.ELMver)]))
         #wx.PostEvent(self._notify_window, StatusEvent([1, 1, str(self.protocol)]))
         #wx.PostEvent(self._notify_window, StatusEvent([3, 1, str(self.connection.connection.port_name())]))
         try:
            r = self.connection.connection.query(obd.commands.VIN)
            if r.vale != None:
               self.VIN = str(r.value)
               wx.PostEvent(self._notify_window, StatusEvent([4, 1, str(self.VIN)]))
         except:
            pass
         return 1

   def stop(self):
      try:  # if stop is called before any connection port is not defined (and not connected )
         self.connection.connection.close()
      except:
         pass
      # lock.release()
      self.process_active = False

   def connectToOBD(self):
      print("Connect to OBD")
      if(self.initCommunication() == 1):
         self.sensors[7].SetLabel("Connected")
         return 1
      else:
         self.sensors[7].SetLabel("Not connected")
         return 0

   def InitUI(self): 
	
      p = wx.Panel(self) 

      p.SetBackgroundColour("black");
      gs = wx.GridSizer(3, 3, 5, 5)

      font = wx.Font(18, wx.ROMAN, wx.ITALIC, wx.NORMAL)

      txt = "--\n"+str(0)
      st = wx.StaticText(p, label=txt, style=wx.ALIGN_CENTER)
      st.SetForegroundColour("white")
      st.SetFont(font)
      self.sensors.append(st)

      txt = "SPEED(mph)\n"+str(INDEX_SPEED)
      st = wx.StaticText(p, label=txt, style=wx.ALIGN_CENTER)
      st.SetForegroundColour("white")
      st.SetFont(font)
      self.sensors.append(st)

      txt = "FUEL %\n"+str(INDEX_FUEL)
      st = wx.StaticText(p, label=txt, style=wx.ALIGN_CENTER)
      st.SetForegroundColour("white")
      st.SetFont(font)
      self.sensors.append(st)

      
      txt = "COOLANT (C)\n"+str(INDEX_COOLANT)
      st = wx.StaticText(p, label=txt, style=wx.ALIGN_CENTER)
      st.SetForegroundColour("white")
      st.SetFont(font)
      self.sensors.append(st)

      txt = "RPM\n"+str(INDEX_RPM)
      st = wx.StaticText(p, label=txt, style=wx.ALIGN_CENTER)
      st.SetForegroundColour("white")
      st.SetFont(font)
      self.sensors.append(st)

      txt = "DIST(miles)\n"+str(INDEX_DISTANCE)
      st = wx.StaticText(p, label=txt, style=wx.ALIGN_CENTER)
      st.SetForegroundColour("white")
      st.SetFont(font)
      self.sensors.append(st)

      txt = "MPG\n"+str(INDEX_FUEL_RATE)
      st = wx.StaticText(p, label=txt, style=wx.ALIGN_CENTER)
      st.SetForegroundColour("white")
      st.SetFont(font)
      self.sensors.append(st)

      txt = "Status\n"+str(7)
      st = wx.StaticText(p, label=txt, style=wx.ALIGN_CENTER)
      st.SetForegroundColour("white")
      st.SetFont(font)
      self.sensors.append(st)

      txt = "AIR TEMP (C)\n"+str(INDEX_AIRTEMP)
      st = wx.StaticText(p, label=txt, style=wx.ALIGN_CENTER)
      st.SetForegroundColour("white")
      st.SetFont(font)
      self.sensors.append(st)

      # txt = "--\n"+str(9)
      # st = wx.StaticText(p, label=txt, style=wx.ALIGN_CENTER)
      # st.SetForegroundColour("white")
      # sensors.append(st)

      for i in range(1,10):
         gs.Add(self.sensors[i-1],0,wx.EXPAND)
         p.SetSizer(gs)

   def update(self):
    #  r = str(random.randint(0, 100))
      r = self.connection.connection.query(obd.commands.RPM)
      print(r.value.magnitude)
      self.sensors[INDEX_RPM].SetLabel("RPM\n" + str(r.value.magnitude))
      self.rpmVal = r.value.magnitude
      
      r= self.connection.connection.query(obd.commands.SPEED)
      print(r.value.magnitude)
      self.sensors[INDEX_SPEED].SetLabel("SPEED(mph)\n" + str(r.value.magnitude))
      self.speedVal = r.value.magnitude
      
      r = self.connection.connection.query(obd.commands.COOLANT_TEMP)
      print(r.value.magnitude)
      self.sensors[INDEX_COOLANT].SetLabel("COOLANT (C)\n" + str(r.value.magnitude))   
      self.coolantVal = r.value.magnitude
            
      r = self.connection.connection.query(obd.commands.DISTANCE_SINCE_DTC_CLEAR)
      print(r.value.magnitude)
      self.sensors[INDEX_DISTANCE].SetLabel("DIST(miles)\n" + str("{:.2f}".format(r.value.magnitude/1.6)))
      self.distVal = r.value.magnitude
      
      r = self.connection.connection.query(obd.commands.FUEL_LEVEL)
      print(r.value.magnitude)
      self.sensors[INDEX_FUEL_RATE].SetLabel("Gal/Hr\n" + "{:.2f}".format(r.value.magnitude))

      r = self.connection.connection.query(obd.commands.FUEL_LEVEL)
      print(r.value.magnitude)
      self.sensors[INDEX_FUEL].SetLabel("FUEL %\n" + "{:.2f}".format(r.value.magnitude))
      self.fuelVal = r.value.magnitude

      r = self.connection.connection.query(obd.commands.AMBIANT_AIR_TEMP)
      print(r.value.magnitude)
      self.sensors[INDEX_AIRTEMP].SetLabel("AIR TEMP(C)\n" + str((r.value.magnitude)))
      self.airTempVal = r.value.magnitude
      
      self.writeToLogFile()
      
      wx.CallLater(1000, self.update)

   
app = wx.App() 
GUI(None, title = 'OBD Sensor Dash') 
app.MainLoop()
