import wx
import os
import sys
import webbrowser
import serial
import httplib2
import time
import serial
import thread

from httplib2 import Http
from urllib import urlencode
import json


try:
    from agw import buttonpanel as bp
except ImportError: # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.buttonpanel as bp

import images
import random


#----------------------------------------------------------------------

ID_BackgroundColour = wx.NewId()
ID_GradientFrom = wx.NewId()
ID_GradientTo = wx.NewId()
ID_BorderColour = wx.NewId()
ID_CaptionColour = wx.NewId()
ID_ButtonTextColour = wx.NewId()
ID_SelectionBrush = wx.NewId()
ID_SelectionPen = wx.NewId()
ID_SeparatorColour = wx.NewId()

global exitflag
global device1,arduino1,theuser
exitflag = 0
global consolequeue
consolequeue = []

def createjson(arduino1):
    try:
        dict = {'A0': '0','A1': '0','A2': '0','A3': '0','A4': '0','A5': '0','D2': '0','D3': '0','D4': '0','D5': '0','D6': '0','D7': '0','D8': '0','D9': '0','D10': '0','D11': '0','D12': '0','D13': '0'}
        dict['A0']=arduino1.A0
        dict['A1']=arduino1.A1
        dict['A2']=arduino1.A2
        dict['A3']=arduino1.A3
        dict['A4']=arduino1.A4
        dict['A5']=arduino1.A5
        dict['D2']=arduino1.D2
        dict['D3']=arduino1.D3
        dict['D4']=arduino1.D4
        dict['D5']=arduino1.D5
        dict['D6']=arduino1.D6
        dict['D7']=arduino1.D7
        dict['D8']=arduino1.D8
        dict['D9']=arduino1.D9
        dict['D10']=arduino1.D10
        dict['D11']=arduino1.D11
        dict['D12']=arduino1.D12
        dict['D13']=arduino1.D13
            
        val=json.dumps(dict)
        return val
    except:
        return 'Fail'

    

def writeconsole(console,data):
    global consolequeue
    consolequeue.append(data)
    while len(consolequeue) > 0:        
        com = consolequeue.pop(0)
        console.logtext.AppendText(com)
        
def CloseSerial(ser,monitor):
    global exitflag
    writeconsole(monitor,"CloseSerial(): Closed serial Connection! \n")
    conn = "Serial: Closed!\t\tPort:N/A"
    monitor.statusbar.SetStatusText(conn, 1)
    ser.close()
    exitflag = 1

class userClass:  
    def __init__(self, name, passw):
        self.name = name
        self.passw = passw
        
class Device:  
    def __init__(self, name, port,ser):
        self.name = name
        self.port = port
        self.ser  = ser
    def show(self):
        print 'the port is:',self.port
        print 'the port is:',self.name
        
class Arduino:  
    def __init__(self, A0, A1,A2,A3,A4,A5,D2,D3,D4,D5,D6,D7,D8,D9,D10,D11,D12,D13):
        self.A0  = A0
        self.A1  = A1
        self.A2  = A2
        self.A3  = A3
        self.A4  = A4
        self.A5  = A5
        self.D2=D2
        self.D3=D3
        self.D4=D4
        self.D5=D5        
        self.D6=D6
        self.D7=D7
        self.D8=D8
        self.D9=D9
        self.D10=D10
        self.D11=D11        
        self.D12=D12
        self.D13=D13        

# =====================================================
# ==                SERIAL RX THREAD                 ==
# =====================================================
def SerialRx(threadName, ser,url,monitor):
   global exitflag
   monitor.logtext.AppendText("SerialRx Started ....\n")
   start = 0
   pulse = '0xe0'
   tbuffer = 0
   #                 0   1   2   3   4   5   2   3   4   5   6   7   8   9  10  11  12  13
   arduino1=Arduino('N','N','N','N','N','N','N','N','N','N','N','N','N','N','N','N','N','N')
   while 1:
        if exitflag == 1:
           writeconsole(monitor,"exitflag = 1: SerialRx is closing ......\n")
           break
        else:
           try:
               if (ser.isOpen()):
                   try:
                       datain=ser.read(1)
                       if len(datain)>0:         # if there is data read from serial port then send it to Browser
                          r = str(hex(ord(datain)))
                          #writeconsole(monitor,"---- Rx Data : ----  "+r+" \n")
                          #writeconsole(monitor,"Arduino:"+resp+" Buffer = "+str(tbuffer)+"\n")
                          casa = (r=='0xe0' or r=='0xe1' or r=='0xe2' or r=='0xe3' or r=='0xe4' or r=='0xe5')
                          casd1 = (r=='0x92' or r=='0x93' or r=='0x94' or r=='0x95')
                          casd2 = (r=='0x96' or r=='0x97' or r=='0x98' or r=='0x99')
                          casd3 = (r=='0x9A' or r=='0x9B' or r=='0x9C' or r=='0x9D')
                          cas = casd1 or casd2 or casd3 or casa
                          
                          if casa:
                              start = 1
                              pulse = r
                              tbuffer=0
                              #writeconsole(monitor,"---- Header ----  "+r+" \n")
                          elif start == 1:
                              tbuffer+=int(str(ord(datain)))
                              start = 2
                              #writeconsole(monitor,"---- LSB "+r+" \n")
                          elif start == 2:
                              tbuffer+=int(str(ord(datain)))*256
                              #writeconsole(monitor,"---- MSB "+r+" \n")
                              if pulse == '0xe0':
                                  arduino1.A0 = tbuffer
                              elif pulse == '0xe1':
                                  arduino1.A1 = tbuffer
                              elif pulse == '0xe2':
                                  arduino1.A2 = tbuffer
                              elif pulse == '0xe3':
                                  arduino1.A3 = tbuffer
                              elif pulse == '0xe4':
                                  arduino1.A4 = tbuffer
                              elif pulse == '0xe5':
                                  arduino1.A5 = tbuffer
                                  # Send data when analog reporting is done
                                  try:
                                      da=createjson(arduino1)
                                      #writeconsole(monitor,"JSON sent:"+da+"\n")
                                      #devicedata=dict(Name="Arduino",Data=da)
                                      h = Http()
                                      user=theuser.name
                                      passw=theuser.passw
                                      headers={'user':user,'passw':passw}
                                      response, content = h.request(url, "POST", da, headers=headers)
                                      #writeconsole(monitor,"Cloud server data:"+str(content)+"\n")
                                      #writeconsole(monitor,"Cloud server response:"+str(response)+"\n")
                                      conn = "Cloud Status: "+str(response['status']+"\tUpdated: "+str(response['date']))
                                      monitor.statusbar.SetStatusText(conn, 2)
                                      start=0
                                      tbuffer=0
                                      pulse=''                                      
                                  except:
                                      writeconsole(monitor,"Cannot establish Connection to Cloud server ......\n")
                                      writeconsole(monitor,"SerialRx is Aborting ......\n")
                                      exitflag=1
                                      CloseSerial(ser,monitor)
                                      break
                             
                              elif pulse == '0x90':
                                  arduino1.D2 = tbuffer
                              elif pulse == '0x91':
                                  arduino1.D3 = tbuffer


                   except:
                       pass
               else:
                   conn = "Serial: Unknown!\t\tPort:Unknown"
                   monitor.statusbar.SetStatusText(conn, 1)
           except:
                monitor.logtext.AppendText("SerialRx Cannot read from serial ......\n")
# =====================================================
# ==                SERIAL TX THREAD                 ==
# =====================================================
            
def SerialTx(threadName,ser,url,monitor):
   global exitflag
   time.sleep(2)   #both tx and Rx threads are writing to the main console so adding a delay to avoid overwriting
   monitor.logtext.AppendText("SerialTx Started ....\n")
   
   while 1:
        if exitflag == 1:
           writeconsole(monitor,"exitflag = 1: SerialTx is closing ......\n")
           break
        else:
            try:
                h = Http()
                user=theuser.name
                passw=theuser.passw
                #headers={'user':user,'passw':passw}
                da='user='+user+'&passw='+passw
                #urlget=url+'?user='+user+'&passw='+passw
                #resp, content = h.request(urlget, "GET")                                                     
                resp, content = h.request(url, "POST", da)
                #writeconsole(monitor,"user: "+user+" passw: "+passw+"\n")
            except:
                writeconsole(monitor,"SerialTx: Cannot establish Connection to Cloud server ......\n")
                writeconsole(monitor,"SerialTx is Aborting ......\n")
                writeconsole(monitor,"Closing Serial Connection ......\n")
                exitflag=1
                CloseSerial(ser,monitor)
                break;
            time.sleep(1)
            command=str(content)
            if command.find('quit') !=-1:
                #print 'SerialTx is closing ...... '
                writeconsole(monitor,'Server: '+command+'\n')
                writeconsole(monitor,"Cloud Server Close connection Request: SerialTx is closing ......\n")
                exitflag=1
                CloseSerial(ser,monitor)
                break;

                
            elif len(command)>0:
                if command.find('Error') !=-1:  # server error
                    writeconsole(monitor,'Server Error Occured: '+command+"\n")
                elif command.find('undefined') !=-1:  # the command = undefined
                    #print command
                    #monitor.logtext.AppendText(command+"\n")
                    writeconsole(monitor,command+"\n")
                    #am = 1

                elif command.find('NOC')==-1:       # the command is not NOC        
                    #val = chr(0x91)+chr(0x1F)+chr(0x0)
                    a = command.split(',')    #websocket sends data as a string in the format START, COMMAND, END
                    #print a
                    writeconsole(monitor,"Command to be Sent:"+command+"\n")
                    for i in range(len(a)):
                        if a[i] == '0':                            
                            ser.write(chr(0))
                            writeconsole(monitor,"Writing:"+a[i]+"\n")
                        elif a[i] == '1':
                            ser.write(chr(1))
                            writeconsole(monitor,"Writing:"+a[i]+"\n")
                        else:
                            writeconsole(monitor,"Writing:"+hex(eval(a[i]))+"\n")
                            val = chr(eval(a[i]))
                            ser.write(val)
##                    if command.find('0xF4,0x0D,1') !=-1:
##                        writeconsole(monitor,"Set Digital Port to Input ......\n")
##                        ser.write(chr(eval('0xD0')))
##                        ser.write(chr(eval('0x01')))
##                        ser.write(chr(eval('0xD1')))
##                        ser.write(chr(eval('0x01')))
##                        ser.write(chr(eval('0xF0')))        #query pin state
##                        ser.write(chr(eval('0x6D')))
##                        ser.write(chr(eval('0x0D')))
##                        ser.write(chr(eval('0xF7')))                         
##                        ser.write(chr(eval('0xF0')))        #query pin state
##                        ser.write(chr(eval('0x6D')))
##                        ser.write(chr(eval('0x02')))
##                        ser.write(chr(eval('0xF7')))                        
##                        writeconsole(monitor,"====> DONE: Set Digital Port to Input ......\n")



#----------------------------------------------------------------------
class MySplashScreen(wx.SplashScreen):
    def __init__(self,flag):
        bmp = wx.Image("startupIcon.png").ConvertToBitmap()
        wx.SplashScreen.__init__(self, bmp,
                                 wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT,5000, None, -1)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.fc = wx.FutureCall(10000, self.ShowMain)
        self.flag = flag

    def OnClose(self, evt):
        # Make sure the default handler runs too so this window gets
        # destroyed
        evt.Skip()
        self.Hide()
        
        # if the timer is still running then go ahead and show the
        # main frame now
        if self.fc.IsRunning():
            self.fc.Stop()
            self.ShowMain()


    def ShowMain(self):
        if self.flag:
            Example(None, title="Cloudduino")
        #frame = wxPythonDemo(None, "wxPython: (A Demonstration)")
        #frame.Show()
        #if self.fc.IsRunning():
        #    self.Raise()
        #wx.CallAfter(frame.ShowTip)

# ----------------------
# --- Login    ---------
# ----------------------

class Example(wx.Frame):

    def __init__(self, parent, title):    
        super(Example, self).__init__(parent, title=title, size=(550, 420))

        self.InitUI()
        self.Centre()
        self.Show()     

    def InitUI(self):
      
        panel = wx.Panel(self)
        
        sizer = wx.GridBagSizer(5, 5)

        self.text1 = wx.StaticText(panel, label="Cloudduino: Login")
        sizer.Add(self.text1, pos=(0, 0), flag=wx.TOP|wx.LEFT|wx.BOTTOM, border=15)

        icon = wx.StaticBitmap(panel, bitmap=wx.Bitmap('clouduinosmall.png'))
        sizer.Add(icon, pos=(0, 4), flag=wx.TOP|wx.RIGHT|wx.ALIGN_RIGHT,border=5)

        line = wx.StaticLine(panel)
        sizer.Add(line, pos=(1, 0), span=(1, 5),flag=wx.EXPAND|wx.BOTTOM, border=10)

        text2 = wx.StaticText(panel, label="Username")
        sizer.Add(text2, pos=(2, 0), flag=wx.LEFT, border=10)

        self.tc1 = wx.TextCtrl(panel)
        sizer.Add(self.tc1, pos=(2, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND)

        text3 = wx.StaticText(panel, label="Password")
        sizer.Add(text3, pos=(3, 0), flag=wx.LEFT|wx.TOP, border=10)

        self.tc2 = wx.TextCtrl(panel)
        sizer.Add(self.tc2, pos=(3, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND,border=5)

        sb = wx.StaticBox(panel, label="Options")

        boxsizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
        boxsizer.Add(wx.CheckBox(panel, label="Remember me"), flag=wx.LEFT|wx.TOP, border=5)
        boxsizer.Add(wx.CheckBox(panel, label="Remember Settings"),flag=wx.LEFT, border=5)
        boxsizer.Add(wx.CheckBox(panel, label="Generate Back-up file"), flag=wx.LEFT|wx.BOTTOM, border=5)
        sizer.Add(boxsizer, pos=(5, 0), span=(1, 5), flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)

        button3 = wx.Button(panel, label='Help')
        sizer.Add(button3, pos=(7, 0), flag=wx.LEFT, border=10)

        login = wx.Button(panel, label="Login!")
        sizer.Add(login, pos=(7, 3))
        self.Bind(wx.EVT_BUTTON, self.OnButton, login)

        button5 = wx.Button(panel, label="Sign Up!")
        sizer.Add(button5, pos=(7, 4), span=(1, 1),flag=wx.BOTTOM|wx.RIGHT, border=5)
        self.Bind(wx.EVT_BUTTON, self.SignUp, button5)
        
        sizer.AddGrowableCol(2)
        
        panel.SetSizer(sizer)
        
    def OnButton(self, evt):
        global theuser
        #self.Close()
        #self.Destroy()
        #self.Hide()
        user=self.tc1.GetValue()
        passw=self.tc2.GetValue()
        #data = dict(username=user, password=passw)
        data="username="+user+"&password="+passw
        try:
            h=Http()
            #resp, content = h.request("https://cloudduino.appspot.com/init/desktop", "POST", urlencode(data))
            resp, content = h.request("https://cloudduino.appspot.com/init/desktop", "POST", data)
            #resp, content = h.request("http://localhost:8081/init/desktop", "POST", data)
            if content.find('Fail')!=-1:
                self.text1.SetLabel(label='')
                self.text1.SetLabel(label='Failed Login, please try again or press Sign Up! for an account')
            elif content.find('Success')!=-1:
                self.text1.SetLabel(label='')
                self.text1.SetLabel(label='Success!')
                theuser=userClass(user,passw)
                self.win = ButtonPanelDemo(self)
                self.win.Show(True)
                self.Hide()
                
            else:
                 self.text1.SetLabel(label='')
                 self.text1.SetLabel(label='No Response, please try again')
        except:
            self.text1.SetLabel(label='')
            self.text1.SetLabel(label='Error: No Response, please try again')

        
    def SignUp(self, evt):
        url = 'https://cloudduino.appspot.com'
        webbrowser.open_new(url)
        self.Hide()
        MySplashScreen(False).Show()




class SettingsPanel(wx.MiniFrame):

    def __init__(self, parent, id=wx.ID_ANY, title="Settings Panel", pos=wx.DefaultPosition,size=wx.DefaultSize,
                 style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.FRAME_NO_TASKBAR | wx.FRAME_FLOAT_ON_PARENT | wx.CLIP_CHILDREN):

        wx.MiniFrame.__init__(self, parent, id, title, pos, size, style)

        self.targetTitleBar = parent.titleBar
        self.parent = parent
        self.panel = wx.Panel(self, -1)
        
        self.coloursizer_staticbox = wx.StaticBox(self.panel, -1, "Colour Options")
        self.bottomsizer_staticbox = wx.StaticBox(self.panel, -1, "Size Options")
        self.stylesizer_staticbox = wx.StaticBox(self.panel, -1, "ButtonPanel Styles")
        self.defaultstyle = wx.RadioButton(self.panel, -1, "Default Style", style=wx.RB_GROUP)
        self.gradientstyle = wx.RadioButton(self.panel, -1, "Gradient Style")
        self.verticalgradient = wx.RadioButton(self.panel, -1, "Vertical Gradient", style=wx.RB_GROUP)
        self.horizontalgradient = wx.RadioButton(self.panel, -1, "Horizontal Gradient")

        b = self.CreateColourBitmap(wx.BLACK)
        
        self.bakbrush = wx.BitmapButton(self.panel, ID_BackgroundColour, b, size=wx.Size(50,25))
        self.gradientfrom = wx.BitmapButton(self.panel, ID_GradientFrom, b, size=wx.Size(50,25))
        self.gradientto = wx.BitmapButton(self.panel, ID_GradientTo, b, size=wx.Size(50,25))
        self.bordercolour = wx.BitmapButton(self.panel, ID_BorderColour, b, size=wx.Size(50,25))
        self.captioncolour = wx.BitmapButton(self.panel, ID_CaptionColour, b, size=wx.Size(50,25))
        self.textbuttoncolour = wx.BitmapButton(self.panel, ID_ButtonTextColour, b, size=wx.Size(50,25))
        self.selectionbrush = wx.BitmapButton(self.panel, ID_SelectionBrush, b, size=wx.Size(50,25))
        self.selectionpen = wx.BitmapButton(self.panel, ID_SelectionPen, b, size=wx.Size(50,25))
        self.separatorcolour = wx.BitmapButton(self.panel, ID_SeparatorColour, b, size=wx.Size(50,25))

        self.separatorspin = wx.SpinCtrl(self.panel, -1, "7", min=3, max=20, style=wx.SP_ARROW_KEYS)
        self.marginspin = wx.SpinCtrl(self.panel, -1, "6", min=3, max=20, style=wx.SP_ARROW_KEYS)
        self.paddingspin = wx.SpinCtrl(self.panel, -1, "6", min=3, max=20,style=wx.SP_ARROW_KEYS)
        self.borderspin = wx.SpinCtrl(self.panel, -1, "3", min=3, max=7,style=wx.SP_ARROW_KEYS)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnDefaultStyle, self.defaultstyle)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnGradientStyle, self.gradientstyle)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnVerticalGradient, self.verticalgradient)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnHorizontalGradient, self.horizontalgradient)
        self.Bind(wx.EVT_BUTTON, self.OnSetColour, id=ID_BackgroundColour)
        self.Bind(wx.EVT_BUTTON, self.OnSetColour, id=ID_GradientFrom)
        self.Bind(wx.EVT_BUTTON, self.OnSetColour, id=ID_GradientTo)
        self.Bind(wx.EVT_BUTTON, self.OnSetColour, id=ID_BorderColour)
        self.Bind(wx.EVT_BUTTON, self.OnSetColour, id=ID_CaptionColour)
        self.Bind(wx.EVT_BUTTON, self.OnSetColour, id=ID_ButtonTextColour)
        self.Bind(wx.EVT_BUTTON, self.OnSetColour, id=ID_SelectionBrush)
        self.Bind(wx.EVT_BUTTON, self.OnSetColour, id=ID_SelectionPen)
        self.Bind(wx.EVT_BUTTON, self.OnSetColour, id=ID_SeparatorColour)
        
        self.Bind(wx.EVT_SPINCTRL, self.OnSeparator, self.separatorspin)
        self.Bind(wx.EVT_SPINCTRL, self.OnMargins, self.marginspin)
        self.Bind(wx.EVT_SPINCTRL, self.OnPadding, self.paddingspin)
        self.Bind(wx.EVT_SPINCTRL, self.OnBorder, self.borderspin)

        self.Bind(wx.EVT_CLOSE, self.OnClose)        


    def __set_properties(self):

        self.defaultstyle.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.defaultstyle.SetValue(1)
        self.gradientstyle.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.verticalgradient.SetValue(1)

        if self.targetTitleBar.GetStyle() & bp.BP_DEFAULT_STYLE:
            self.verticalgradient.Enable(False)
            self.horizontalgradient.Enable(False)
            self.defaultstyle.SetValue(1)
        else:
            self.gradientstyle.SetValue(1)

        self.borderspin.SetValue(self.targetTitleBar.GetBPArt().GetMetric(bp.BP_BORDER_SIZE))
        self.separatorspin.SetValue(self.targetTitleBar.GetBPArt().GetMetric(bp.BP_SEPARATOR_SIZE))
        self.marginspin.SetValue(self.targetTitleBar.GetBPArt().GetMetric(bp.BP_MARGINS_SIZE).x)
        self.paddingspin.SetValue(self.targetTitleBar.GetBPArt().GetMetric(bp.BP_PADDING_SIZE).x)

        self.UpdateColours()        
        

    def __do_layout(self):

        mainsizer = wx.BoxSizer(wx.VERTICAL)
        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        bottomsizer = wx.StaticBoxSizer(self.bottomsizer_staticbox, wx.VERTICAL)
        sizer_13 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_12 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
        coloursizer = wx.StaticBoxSizer(self.coloursizer_staticbox, wx.HORIZONTAL)
        rightsizer = wx.BoxSizer(wx.VERTICAL)
        sizer_9 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        leftsizer = wx.BoxSizer(wx.VERTICAL)
        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        stylesizer = wx.StaticBoxSizer(self.stylesizer_staticbox, wx.VERTICAL)
        tophsizer = wx.BoxSizer(wx.HORIZONTAL)
        tophsizer2 = wx.BoxSizer(wx.VERTICAL)
        
        stylesizer.Add(self.defaultstyle, 0, wx.ALL|wx.EXPAND|wx.ADJUST_MINSIZE, 5)

        tophsizer.Add(self.gradientstyle, 0, wx.LEFT|wx.RIGHT|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)

        tophsizer2.Add(self.verticalgradient, 0, wx.BOTTOM|wx.ADJUST_MINSIZE, 3)
        tophsizer2.Add(self.horizontalgradient, 0, wx.ADJUST_MINSIZE, 0)
        
        tophsizer.Add(tophsizer2, 1, wx.LEFT|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 10)

        stylesizer.Add(tophsizer, 1, wx.EXPAND, 0)

        mainsizer.Add(stylesizer, 0, wx.ALL|wx.EXPAND, 5)

        label_1 = wx.StaticText(self.panel, -1, "Background Brush Colour:")
        sizer_1.Add(label_1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_1.Add((0, 0), 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_1.Add(self.bakbrush, 0, wx.ADJUST_MINSIZE, 0)

        leftsizer.Add(sizer_1, 1, wx.EXPAND, 0)

        label_2 = wx.StaticText(self.panel, -1, "Gradient Colour From:")
        sizer_2.Add(label_2, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_2.Add((0, 0), 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_2.Add(self.gradientfrom, 0, wx.ADJUST_MINSIZE, 0)

        leftsizer.Add(sizer_2, 1, wx.EXPAND, 0)

        label_3 = wx.StaticText(self.panel, -1, "Gradient Colour To:")
        sizer_3.Add(label_3, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_3.Add((0, 0), 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_3.Add(self.gradientto, 0, wx.ADJUST_MINSIZE, 0)

        leftsizer.Add(sizer_3, 1, wx.EXPAND, 0)

        label_4 = wx.StaticText(self.panel, -1, "Border Colour:")
        sizer_4.Add(label_4, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_4.Add((0, 0), 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_4.Add(self.bordercolour, 0, wx.ADJUST_MINSIZE, 0)

        leftsizer.Add(sizer_4, 1, wx.EXPAND, 0)

        label_5 = wx.StaticText(self.panel, -1, "Main Caption Colour:")
        sizer_5.Add(label_5, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_5.Add((0, 0), 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_5.Add(self.captioncolour, 0, wx.ADJUST_MINSIZE, 0)

        leftsizer.Add(sizer_5, 1, wx.EXPAND, 0)

        coloursizer.Add(leftsizer, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        coloursizer.Add((20, 20), 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        
        label_6 = wx.StaticText(self.panel, -1, "Text Button Colour:")
        sizer_6.Add(label_6, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_6.Add((0, 0), 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_6.Add(self.textbuttoncolour, 0, wx.ADJUST_MINSIZE, 0)

        rightsizer.Add(sizer_6, 1, wx.EXPAND, 0)

        label_7 = wx.StaticText(self.panel, -1, "Selection Brush Colour:")
        sizer_7.Add(label_7, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_7.Add((0, 0), 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_7.Add(self.selectionbrush, 0, wx.ADJUST_MINSIZE, 0)

        rightsizer.Add(sizer_7, 1, wx.EXPAND, 0)

        label_8 = wx.StaticText(self.panel, -1, "Selection Pen Colour:")
        sizer_8.Add(label_8, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_8.Add((0, 0), 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_8.Add(self.selectionpen, 0, wx.ADJUST_MINSIZE, 0)

        rightsizer.Add(sizer_8, 1, wx.EXPAND, 0)

        label_9 = wx.StaticText(self.panel, -1, "Separator Colour:")
        sizer_9.Add(label_9, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_9.Add((0, 0), 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_9.Add(self.separatorcolour, 0, wx.ADJUST_MINSIZE, 0)

        rightsizer.Add(sizer_9, 1, wx.EXPAND, 0)

        coloursizer.Add(rightsizer, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)

        mainsizer.Add(coloursizer, 0, wx.ALL|wx.EXPAND, 5)

        label_10 = wx.StaticText(self.panel, -1, "Separator Size:")
        sizer_10.Add(label_10, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_10.Add((0, 0), 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_10.Add(self.separatorspin, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)

        bottomsizer.Add(sizer_10, 1, wx.EXPAND, 0)

        label_11 = wx.StaticText(self.panel, -1, "Margins Size:")
        sizer_11.Add(label_11, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_11.Add((0, 0), 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_11.Add(self.marginspin, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ADJUST_MINSIZE, 5)

        bottomsizer.Add(sizer_11, 1, wx.EXPAND, 0)

        label_12 = wx.StaticText(self.panel, -1, "Padding Size:")
        sizer_12.Add(label_12, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_12.Add((0, 0), 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_12.Add(self.paddingspin, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ADJUST_MINSIZE, 5)

        bottomsizer.Add(sizer_12, 1, wx.EXPAND, 0)

        label_13 = wx.StaticText(self.panel, -1, "Border Size:")
        sizer_13.Add(label_13, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        sizer_13.Add((0, 0), 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_13.Add(self.borderspin, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ADJUST_MINSIZE, 5)

        bottomsizer.Add(sizer_13, 1, wx.EXPAND, 0)

        mainsizer.Add(bottomsizer, 0, wx.ALL|wx.EXPAND, 5)

        self.panel.SetSizer(mainsizer)
        sizer = wx.BoxSizer()
        sizer.Add(self.panel, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.Fit()


    def CreateColourBitmap(self, c):
    
        image = wx.EmptyImage(25, 14)
        
        for x in xrange(25):
            for y in xrange(14):
                pixcol = c
                if x == 0 or x == 24 or y == 0 or y == 13:
                    pixcol = wx.BLACK
                    
                image.SetRGB(x, y, pixcol.Red(), pixcol.Green(), pixcol.Blue())
            
        return image.ConvertToBitmap()


    def UpdateColours(self):
    
        bk = self.targetTitleBar.GetBPArt().GetColour(bp.BP_BACKGROUND_COLOUR)
        self.bakbrush.SetBitmapLabel(self.CreateColourBitmap(bk))
        
        capfrom = self.targetTitleBar.GetBPArt().GetColour(bp.BP_GRADIENT_COLOUR_FROM)
        self.gradientfrom.SetBitmapLabel(self.CreateColourBitmap(capfrom))

        capto = self.targetTitleBar.GetBPArt().GetColour(bp.BP_GRADIENT_COLOUR_TO)
        self.gradientto.SetBitmapLabel(self.CreateColourBitmap(capto))

        captxt = self.targetTitleBar.GetBPArt().GetColour(bp.BP_TEXT_COLOUR)
        self.captioncolour.SetBitmapLabel(self.CreateColourBitmap(captxt))

        bor = self.targetTitleBar.GetBPArt().GetColour(bp.BP_BORDER_COLOUR)
        self.bordercolour.SetBitmapLabel(self.CreateColourBitmap(bor))
        
        btntext = self.targetTitleBar.GetBPArt().GetColour(bp.BP_BUTTONTEXT_COLOUR)
        self.textbuttoncolour.SetBitmapLabel(self.CreateColourBitmap(btntext))

        selb = self.targetTitleBar.GetBPArt().GetColour(bp.BP_SELECTION_BRUSH_COLOUR)
        self.selectionbrush.SetBitmapLabel(self.CreateColourBitmap(selb))

        selp = self.targetTitleBar.GetBPArt().GetColour(bp.BP_SELECTION_PEN_COLOUR)
        self.selectionpen.SetBitmapLabel(self.CreateColourBitmap(selp))
        
        sepc = self.targetTitleBar.GetBPArt().GetColour(bp.BP_SEPARATOR_COLOUR)
        self.separatorcolour.SetBitmapLabel(self.CreateColourBitmap(sepc))


    def OnDefaultStyle(self, event):

        self.verticalgradient.Enable(False)
        self.horizontalgradient.Enable(False)
        self.targetTitleBar.SetStyle(bp.BP_DEFAULT_STYLE)

        self.targetTitleBar.Refresh()

        event.Skip()
        

    def OnGradientStyle(self, event): 

        self.verticalgradient.Enable(True)
        self.horizontalgradient.Enable(True)
        self.targetTitleBar.SetStyle(bp.BP_USE_GRADIENT)
        self.targetTitleBar.Refresh()
        
        event.Skip()


    def OnVerticalGradient(self, event):

        self.targetTitleBar.GetBPArt().SetGradientType(bp.BP_GRADIENT_VERTICAL)
        self.targetTitleBar.SetStyle(bp.BP_USE_GRADIENT)
        self.targetTitleBar.Refresh()
        
        event.Skip()
        

    def OnHorizontalGradient(self, event):

        self.targetTitleBar.GetBPArt().SetGradientType(bp.BP_GRADIENT_HORIZONTAL)
        self.targetTitleBar.SetStyle(bp.BP_USE_GRADIENT)
        self.targetTitleBar.Refresh()
        
        event.Skip()
        

    def OnSetColour(self, event):

        dlg = wx.ColourDialog(self.parent)
        
        dlg.SetTitle("Colour Picker")
        
        if dlg.ShowModal() != wx.ID_OK:
            return
        
        var = 0
        if event.GetId() == ID_BackgroundColour:
            var = bp.BP_BACKGROUND_COLOUR
        elif event.GetId() == ID_GradientFrom:
            var = bp.BP_GRADIENT_COLOUR_FROM
        elif event.GetId() == ID_GradientTo:
            var = bp.BP_GRADIENT_COLOUR_TO
        elif event.GetId() == ID_BorderColour:
            var = bp.BP_BORDER_COLOUR
        elif event.GetId() == ID_CaptionColour:
            var = bp.BP_TEXT_COLOUR
        elif event.GetId() == ID_ButtonTextColour:
            var = bp.BP_BUTTONTEXT_COLOUR
        elif event.GetId() == ID_SelectionBrush:
            var = bp.BP_SELECTION_BRUSH_COLOUR
        elif event.GetId() == ID_SelectionPen:
            var = bp.BP_SELECTION_PEN_COLOUR
        elif event.GetId() == ID_SeparatorColour:
            var = bp.BP_SEPARATOR_COLOUR
        else:
            return        
        
        self.targetTitleBar.GetBPArt().SetColour(var, dlg.GetColourData().GetColour())
        self.targetTitleBar.Refresh()
        self.UpdateColours()
        self.parent.useredited = True


    def OnSeparator(self, event):

        self.targetTitleBar.GetBPArt().SetMetric(bp.BP_SEPARATOR_SIZE, event.GetInt())
        self.targetTitleBar.DoLayout()
        self.parent.mainPanel.Layout()
        self.parent.useredited = True
        event.Skip()


    def OnMargins(self, event):

        self.targetTitleBar.GetBPArt().SetMetric(bp.BP_MARGINS_SIZE,wx.Size(event.GetInt(), event.GetInt()))
        self.targetTitleBar.DoLayout()
        self.parent.mainPanel.Layout()
        self.parent.useredited = True        
        event.Skip()


    def OnPadding(self, event):

        self.targetTitleBar.GetBPArt().SetMetric(bp.BP_PADDING_SIZE, wx.Size(event.GetInt(), event.GetInt()))
        self.targetTitleBar.DoLayout()
        self.parent.mainPanel.Layout()
        self.parent.useredited = True
        
        event.Skip()


    def OnBorder(self, event):

        self.targetTitleBar.GetBPArt().SetMetric(bp.BP_BORDER_SIZE, event.GetInt())
        self.targetTitleBar.DoLayout()
        self.parent.mainPanel.Layout()
        self.parent.useredited = True        
        event.Skip()


    def OnClose(self, event):

        self.parent.hassettingpanel = False
        self.Destroy()


#----------------------------------------------------------------------
#-- Main Program Starts here                                        ---
#----------------------------------------------------------------------

class ButtonPanelDemo(wx.Frame):

    def __init__(self, parent, id=wx.ID_ANY, title="Cloudduino Internet Gateway",
                 pos=wx.DefaultPosition, size=(880, 400), style=wx.DEFAULT_FRAME_STYLE):
        
        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self.useredited = False
        self.hassettingpanel = False

        self.SetIcon(images.Mondrian.GetIcon())
        self.CreateMenuBar()

        self.statusbar = self.CreateStatusBar(3, wx.ST_SIZEGRIP)
        self.statusbar.SetStatusWidths([-1, -1, -2])
        # statusbar fields
        statusbar_fields = [("Help!"),("Serial: None\tPort:Not defined"),("Cloud Status: None")]

        for i in range(len(statusbar_fields)):
            self.statusbar.SetStatusText(statusbar_fields[i], i)
        
        self.mainPanel = wx.Panel(self, -1)
        self.logtext = wx.TextCtrl(self.mainPanel, -1, "", style=wx.TE_MULTILINE|wx.TE_READONLY)
        
        vSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainPanel.SetSizer(vSizer) 

        self.alignments = [bp.BP_ALIGN_LEFT, bp.BP_ALIGN_RIGHT, bp.BP_ALIGN_TOP, bp.BP_ALIGN_BOTTOM]
        
        self.alignment = bp.BP_ALIGN_LEFT
        self.agwStyle = bp.BP_USE_GRADIENT
        
        self.titleBar = bp.ButtonPanel(self.mainPanel, -1, "Cloudduino Internet Gateway ver. 0.9.9.1",
                                       agwStyle=self.agwStyle, alignment=self.alignment)

        self.created = False
        self.pngs = [ (images._bp_btn1.GetBitmap(), 'Network'),
                      (images._bp_btn2.GetBitmap(), 'Disconnect'),
                      (images._bp_btn3.GetBitmap(), 'Connect'),
                      (images._bp_btn4.GetBitmap(), 'List Ports'),
                      ]
        self.CreateButtons()
        self.SetProperties()
        
    def CreateMenuBar(self):

        mb = wx.MenuBar()
        
        file_menu = wx.Menu()
        
        item = wx.MenuItem(file_menu, wx.ID_ANY, "&Quit")
        file_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnClose, item)

        edit_menu = wx.Menu()

        #item = wx.MenuItem(edit_menu, wx.ID_ANY, "Set Bar Text")
        #edit_menu.AppendItem(item)
        #self.Bind(wx.EVT_MENU, self.OnSetBarText, item)

        #edit_menu.AppendSeparator()        

##        submenu = wx.Menu()
##        
##        item = wx.MenuItem(submenu, wx.ID_ANY, "BP_ALIGN_LEFT", kind=wx.ITEM_RADIO)
##        submenu.AppendItem(item)
##        item.Check(True)
##        self.Bind(wx.EVT_MENU, self.OnAlignment, item)
##        
##        item = wx.MenuItem(submenu, wx.ID_ANY, "BP_ALIGN_RIGHT", kind=wx.ITEM_RADIO)
##        submenu.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.OnAlignment, item)
##        
##        item = wx.MenuItem(submenu, wx.ID_ANY, "BP_ALIGN_TOP", kind=wx.ITEM_RADIO)
##        submenu.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.OnAlignment, item)
##        
##        item = wx.MenuItem(submenu, wx.ID_ANY, "BP_ALIGN_BOTTOM", kind=wx.ITEM_RADIO)
##        submenu.AppendItem(item)
##        self.Bind(wx.EVT_MENU, self.OnAlignment, item)
##
##        edit_menu.AppendMenu(wx.ID_ANY, "&Alignment", submenu)
                
        submenu = wx.Menu()

        item = wx.MenuItem(submenu, wx.ID_ANY, "Default Style", kind=wx.ITEM_RADIO)
        submenu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnDefaultStyle, item)
        
        item = wx.MenuItem(submenu, wx.ID_ANY, "Gradient Style", kind=wx.ITEM_RADIO)
        submenu.AppendItem(item)
        item.Check(True)
        self.Bind(wx.EVT_MENU, self.OnGradientStyle, item)
        
        edit_menu.AppendMenu(wx.ID_ANY, "&Styles", submenu)

        edit_menu.AppendSeparator()
        
        item = wx.MenuItem(submenu, wx.ID_ANY, "Settings Panel")
        edit_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnSettingsPanel, item)

        demo_menu = wx.Menu()
        
        item = wx.MenuItem(demo_menu, wx.ID_ANY, "Launch Web Interface")
        demo_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnDefaultDemo, item)

        
        help_menu = wx.Menu()

        item = wx.MenuItem(help_menu, wx.ID_ANY, "&About...")
        help_menu.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnAbout, item)
      
        mb.Append(file_menu, "&File")
        mb.Append(edit_menu, "&GUI View")
        mb.Append(demo_menu, "&Web Interface")
        mb.Append(help_menu, "&Help")
        
        self.SetMenuBar(mb)


    def CreateButtons(self):
        global device1
        # Here we (re)create the buttons for the default startup demo
        self.Freeze()
        ser=serial.Serial()
        device1=Device('None','None',ser)
        if self.created:
            sizer = self.mainPanel.GetSizer()
            sizer.Detach(0)
            self.titleBar.Hide()
            wx.CallAfter(self.titleBar.Destroy)
            self.titleBar = bp.ButtonPanel(self.mainPanel, -1, "Cloudduino", agwStyle=self.agwStyle, alignment=self.alignment)
            self.SetProperties()
                    
        self.indices = []
        
        for count, png in enumerate(self.pngs):

            shortHelp = "Cloudduino %d"%(count+1)
            kind = wx.ITEM_CHECK
            longHelp = "Button Description No"
            if count < 1:
                # First 2 buttons are togglebuttons
                kind = wx.ITEM_CHECK                
                longHelp = "Click Network to set Serial Port. e.g. COM4"            
            elif count < 2:
                # First 2 buttons are togglebuttons
                kind = wx.ITEM_CHECK                
                longHelp = "Click to Disconnect"
            elif count < 3:
                # First 2 buttons are togglebuttons
                kind = wx.ITEM_CHECK                
                longHelp = "Click Connect to establish a serial connection with Arduino"
            elif count < 4:
                # First 2 buttons are togglebuttons
                kind = wx.ITEM_CHECK                
                longHelp = "Click to List all serial Ports"

            else:
                kind = wx.ITEM_NORMAL
                longHelp = "Simple Button without label No %d"%(count+1)                

            btn = bp.ButtonInfo(self.titleBar, wx.NewId(),
                                png[0], kind=kind,
                                shortHelp=shortHelp, longHelp=longHelp)
            
            self.titleBar.AddButton(btn)
            self.Bind(wx.EVT_BUTTON, self.OnButton, id=btn.GetId())
            
            self.indices.append(btn.GetId())
            
            if count < 4:
                # First 2 buttons have also a text
                btn.SetText(png[1])

            if count == 2:
                # Append a separator after the second button
                self.titleBar.AddSeparator()
            

        # Add a wx.Choice to ButtonPanel
        self.choices = wx.Choice(self.titleBar, -1, choices=[])
        self.titleBar.AddControl(self.choices)        
        
        self.strings = ["First", "Second", "Third", "Fourth"]

        self.ChangeLayout()              
        self.Thaw()
        self.titleBar.DoLayout()

        self.created = True
   

    def ChangeLayout(self):
        
        # Change the layout after a switch in ButtonPanel alignment
        self.Freeze()
        
        if self.alignment in [bp.BP_ALIGN_LEFT, bp.BP_ALIGN_RIGHT]:
            vSizer = wx.BoxSizer(wx.VERTICAL)
        else:
            vSizer = wx.BoxSizer(wx.HORIZONTAL)
            
        self.mainPanel.SetSizer(vSizer) 

        vSizer.Add(self.titleBar, 0, wx.EXPAND)
        vSizer.Add((20, 20))
        vSizer.Add(self.logtext, 1, wx.EXPAND|wx.ALL, 5)

        vSizer.Layout()
        self.mainPanel.Layout()
        self.Thaw()
                

    def SetProperties(self):

        # No resetting if the user is using the Settings Panel
        if self.useredited:
            return
        
        # Sets the colours for the two demos: called only if the user didn't
        # modify the colours and sizes using the Settings Panel
        bpArt = self.titleBar.GetBPArt()
        

        # set the colour the text is drawn with
        bpArt.SetColour(bp.BP_TEXT_COLOUR, wx.WHITE)

        # These default to white and whatever is set in the system
        # settings for the wx.SYS_COLOUR_ACTIVECAPTION.  We'll use
        # some specific settings to ensure a consistent look for the
        # demo.

        bpArt.SetColour(bp.BP_BORDER_COLOUR, wx.Colour(120,23,224))
        bpArt.SetColour(bp.BP_GRADIENT_COLOUR_FROM, wx.Colour(60,11,112))
        bpArt.SetColour(bp.BP_GRADIENT_COLOUR_TO, wx.Colour(120,23,224))
        bpArt.SetColour(bp.BP_BUTTONTEXT_COLOUR, wx.Colour(70,143,255))
        bpArt.SetColour(bp.BP_SEPARATOR_COLOUR, bp.BrightenColour(wx.Colour(60, 11, 112), 0.85))
        bpArt.SetColour(bp.BP_SELECTION_BRUSH_COLOUR, wx.Colour(225, 225, 255))
        bpArt.SetColour(bp.BP_SELECTION_PEN_COLOUR, wx.SystemSettings_GetColour(wx.SYS_COLOUR_ACTIVECAPTION))

        self.titleBar.SetStyle(self.agwStyle)
        
        
    def OnAlignment(self, event):
        
        # Here we change the alignment property of ButtonPanel
        current = event.GetId()
        item = self.GetMenuBar().FindItemById(current)
        alignment = getattr(bp, item.GetLabel())
        self.alignment = alignment

        self.ChangeLayout()    
        self.titleBar.SetAlignment(alignment)
        self.mainPanel.Layout()
        
        event.Skip()


    def OnDefaultStyle(self, event):
        
        # Restore the ButtonPanel default style (no gradient)
        self.agwStyle = bp.BP_DEFAULT_STYLE
        self.SetProperties()

        event.Skip()        


    def OnGradientStyle(self, event):

        # Use gradients to paint ButtonPanel background
        self.agwStyle = bp.BP_USE_GRADIENT
        self.SetProperties()

        event.Skip()        


    def OnDefaultDemo(self, event):
        url = 'http://cloudduino.appspot.com'
        webbrowser.open_new(url)
        self.logtext.AppendText("Web Interface is Launched !!!!\n")
        #event.Skip()
       
        
    def OnButton(self, event):
        global device1,exitflag
        btn = event.GetId()
        indx = self.indices.index(btn)
        if indx == 0:
            dlg = wx.TextEntryDialog( self, 'Network', 'Serial Port', 'Cloudduino')
            dlg.SetValue(" ")

            if dlg.ShowModal() == wx.ID_OK:
                self.logtext.AppendText('Serial Port Entered: %s\n' % dlg.GetValue())
                ser=serial.Serial()
                device1=Device('Arduino',dlg.GetValue(),ser)
                #device1.show()
            dlg.Destroy()

        
        elif indx == 1:
            #url = 'http://cloudduinodemo.appspot.com'
            #webbrowser.open_new(url)
            #self.logtext.AppendText("Demo is Launched !!!!\n")
            #device1.show()
            ser=device1.ser
            self.logtext.AppendText("Force Close Serial Connection\n")
            CloseSerial(ser,self)
            
        elif indx == 2:
            # launch serial connection
            if device1.port == 'None':
                self.logtext.AppendText("No Port defined ....Please Click Network then select Port\n")
            else:
                self.logtext.AppendText("Connecting to Arduino ....\n")
                try:
                    ser=serial.Serial()
                    ser.baudrate=57600        
                    ser.port=device1.port
                    ser.open()
                    if(ser.isOpen()):
                       self.logtext.AppendText("Connection Open !!!!\n")
                       conn = "Serial: OK!\tPort:"+device1.port
                       self.statusbar.SetStatusText(conn, 1)
                    else:
                       self.logtext.AppendText("Connection Failed !!!!\n") 

##                    #for i in range(60):
                    while True:
                        response=ser.read(1)
                        if len(response)>0:
                            resp = str(hex(ord(response)))
                            #print resp
                            self.logtext.AppendText("Arduino:"+resp+"\n")
                            if resp == '0xF7' or resp == '0xf7':
                                self.logtext.AppendText("Arduino Connection: OK!\n")
                                self.logtext.AppendText("Firmata Detected:\n")
                                break
                    QUERY_VERSION='0xF9'
                    SET_SAMPLING_TIME_2s=['0xF0','0x7A','80','15','0xF7']
                    val = chr(eval(QUERY_VERSION))
                    ser.write(val)
                    self.logtext.AppendText("Query Firmata Version:\n")
                    cnt=0
                    firmata=[]
                    while cnt < 3:
                        response=ser.read(1)
                        if len(response)>0:
                            resp = str(hex(ord(response)))
                            firmata.append(resp)
                            #print resp
                            self.logtext.AppendText("Arduino:"+resp+"\n")
                            if cnt==2:
                                self.logtext.AppendText("Firmata version: "+firmata[1]+" rel:  "+firmata[2]+":\n")
                                # Set the sampling frequency to 2s, this is enough speed for remote monitoring
                                self.logtext.AppendText("Set Sampling time to 2s\n")
                                for byte in SET_SAMPLING_TIME_2s:
                                    val = chr(eval(byte))
                                    ser.write(val)
                                self.logtext.AppendText("====> DONE: Set Sampling time to 2s\n")    
                                h = Http()
                                #urlpost="http://localhost:8080/app/LabScriptPost"
                                urlpost="https://cloudduino.appspot.com/app/LabScriptPost"
                                #urlget="http://localhost:8080/app/LabScriptGet"
                                urlget="https://cloudduino.appspot.com/app/LabScriptGet"
                                exitflag = 0
                                try:
                                  self.logtext.AppendText(" Start SerialTx Thread \n")
                                  thread.start_new_thread( SerialTx, ("Tx-Thread", ser,urlget,self))
                                except Exception,e:
                                  self.logtext.AppendText("Exception:"+ e.message+"\n")

                                try:
                                  self.logtext.AppendText(" Start SerialRx Thread \n")
                                  thread.start_new_thread( SerialRx, ("Rx-Thread", ser,urlpost,self))
                                except Exception,e:
                                  self.logtext.AppendText("Exception:"+ e.message+"\n")
                                # configure firmata to report all analog and digital pins
                                ANALOG_REPORTING=['0xC0','1','0XC1','1','0xC2','1','0xC3','1','0xC4','1','0xC5','1']
                                #ANALOG_REPORTING=['0xD0','0x1','0xD1','0x1']
                                self.logtext.AppendText("Set ANALOG & DIGITAL REPORTING\n")
                                for byte in ANALOG_REPORTING:
                                    val = chr(eval(byte))
                                    ser.write(val)
                                self.logtext.AppendText("====> DONE: Set ANALOG & DIGITAL REPORTING\n") 

                        cnt+=1               

                except Exception,e:
                    if e.message == 'SerialException':
                        #print 'SerialException'
                        self.logtext.AppendText("'SerialException'\n")
                        pass
                    else:
                        #print e.message
                        self.logtext.AppendText(e.message+"\n")
                        pass
        elif indx == 3:
            self.choices.Clear()
            self.logtext.AppendText("'Start Scanning....Please wait '\n")
            ser = serial.Serial()
            for i in range(10):
                try:
                    ser.port = i
                    ser.open() # open serial connection
                    if(ser.isOpen()):
                        self.choices.Append(ser.name)
                    ser.close()
                except Exception,e:
                    if e.message == 'SerialException':
                        self.logtext.AppendText("'SerialException'\n")
                        pass
                    else:
                        pass
            self.logtext.AppendText("'Scanning Done! '\n")

             
        else:            
            self.logtext.AppendText("Event Fired From " + str(indx) + " Button\n")
        
        #self.logtext.AppendText("Event Fired From " + self.strings[indx] + " Button\n")
        event.Skip()


    def OnSetBarText(self, event):

        dlg = wx.TextEntryDialog(self, "Enter The Text You Wish To Display On The Bar (Clear If No Text):",
                                 "Set Text", self.titleBar.GetBarText())
        
        if dlg.ShowModal() == wx.ID_OK:
        
            val = dlg.GetValue()
            self.titleBar.SetBarText(val)
            self.titleBar.DoLayout()
            self.mainPanel.Layout()


    def OnSettingsPanel(self, event):

        if self.hassettingpanel:
            self.settingspanel.Raise()
            return

        self.settingspanel = SettingsPanel(self, -1)
        self.settingspanel.Show()
        self.hassettingpanel = True


    def OnClose(self, event):
        
        self.Destroy()
        event.Skip()


    def OnAbout(self, event):

        msg = "Arduino Cloud Internet Gateway.\n\n" + \
              "Author: Slim Ben Ghalba @ 30 Dec 2012\n\n" + \
              "Please Report Any Bug/Requests Of Improvements\n" + \
              "To Me At The Following Adresses:\n\n" + \
              "3pppinc@gmail.com\n" + "\n\n" + \
              "Cloudduino(c) ver. 0.9.9.1\n\n" + \
              "30 Dec 2012 "
              
        dlg = wx.MessageDialog(self, msg, "Cloudduino Internet Gateway",wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()        

overview = bp.__doc__



if __name__ == '__main__':
    #app = wx.App()
    #ButtonPanelDemo(None).Show(True)
    #app.MainLoop()
    app = wx.App()
    #Example(None, title="Cloudduino")
    MySplashScreen(True)
    app.MainLoop()    


