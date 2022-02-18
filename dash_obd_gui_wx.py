import wx
import time
import random

import obd_io  # OBD2 funcs
import os  # os.environ

class GUI(wx.Frame):
   sensors = []
   portName = "AUTO"
   RECONNATTEMPTS = 5
   SERTIMEOUT = 5
   baudrate = "AUTO"
   fast = 'FAST'

   def __init__(self, parent, title):
      super(GUI, self).__init__(parent, title = title,size = (500, 500))

      self.InitUI()
      self.Centre()
      self.Show()
      if(self.connectToOBD() != 1):
         exit()

      self.on_timer()

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
      else:
         self.sensors[7].SetLabel("Not connected")

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

      txt = "SPEED(mph)\n"+str(1)
      st = wx.StaticText(p, label=txt, style=wx.ALIGN_CENTER)
      st.SetForegroundColour("white")
      st.SetFont(font)
      self.sensors.append(st)

      txt = "Fuel(Gal)\n"+str(2)
      st = wx.StaticText(p, label=txt, style=wx.ALIGN_CENTER)
      st.SetForegroundColour("white")
      st.SetFont(font)
      self.sensors.append(st)

      txt = "--\n"+str(3)
      st = wx.StaticText(p, label=txt, style=wx.ALIGN_CENTER)
      st.SetForegroundColour("white")
      st.SetFont(font)
      self.sensors.append(st)

      txt = "RPM:\n"+str(4)
      st = wx.StaticText(p, label=txt, style=wx.ALIGN_CENTER)
      st.SetForegroundColour("white")
      st.SetFont(font)
      self.sensors.append(st)

      txt = "Distance(miles)\n"+str(5)
      st = wx.StaticText(p, label=txt, style=wx.ALIGN_CENTER)
      st.SetForegroundColour("white")
      st.SetFont(font)
      self.sensors.append(st)

      txt = "--\n"+str(6)
      st = wx.StaticText(p, label=txt, style=wx.ALIGN_CENTER)
      st.SetForegroundColour("white")
      st.SetFont(font)
      self.sensors.append(st)

      txt = "--\n"+str(7)
      st = wx.StaticText(p, label=txt, style=wx.ALIGN_CENTER)
      st.SetForegroundColour("white")
      st.SetFont(font)
      self.sensors.append(st)

      txt = "--\n"+str(8)
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

   def on_timer(self):
      r = str(random.randint(0, 100))
      self.sensors[1].SetLabel("SPEED(mph)\n" + r)
      wx.CallLater(1000, self.on_timer)
   
app = wx.App() 
GUI(None, title = 'Grid demo') 
app.MainLoop()
