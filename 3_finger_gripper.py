import serial
import array
import binascii

CRC_HI_TBL = [
0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01,
0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81,
0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01,
0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01,
0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01,
0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
0x40]

CRC_LOW_TBL = [
0x00, 0xC0, 0xC1, 0x01, 0xC3, 0x03, 0x02, 0xC2, 0xC6, 0x06, 0x07, 0xC7, 0x05, 0xC5, 0xC4,
0x04, 0xCC, 0x0C, 0x0D, 0xCD, 0x0F, 0xCF, 0xCE, 0x0E, 0x0A, 0xCA, 0xCB, 0x0B, 0xC9, 0x09,
0x08, 0xC8, 0xD8, 0x18, 0x19, 0xD9, 0x1B, 0xDB, 0xDA, 0x1A, 0x1E, 0xDE, 0xDF, 0x1F, 0xDD,
0x1D, 0x1C, 0xDC, 0x14, 0xD4, 0xD5, 0x15, 0xD7, 0x17, 0x16, 0xD6, 0xD2, 0x12, 0x13, 0xD3,
0x11, 0xD1, 0xD0, 0x10, 0xF0, 0x30, 0x31, 0xF1, 0x33, 0xF3, 0xF2, 0x32, 0x36, 0xF6, 0xF7,
0x37, 0xF5, 0x35, 0x34, 0xF4, 0x3C, 0xFC, 0xFD, 0x3D, 0xFF, 0x3F, 0x3E, 0xFE, 0xFA, 0x3A,
0x3B, 0xFB, 0x39, 0xF9, 0xF8, 0x38, 0x28, 0xE8, 0xE9, 0x29, 0xEB, 0x2B, 0x2A, 0xEA, 0xEE,
0x2E, 0x2F, 0xEF, 0x2D, 0xED, 0xEC, 0x2C, 0xE4, 0x24, 0x25, 0xE5, 0x27, 0xE7, 0xE6, 0x26,
0x22, 0xE2, 0xE3, 0x23, 0xE1, 0x21, 0x20, 0xE0, 0xA0, 0x60, 0x61, 0xA1, 0x63, 0xA3, 0xA2,
0x62, 0x66, 0xA6, 0xA7, 0x67, 0xA5, 0x65, 0x64, 0xA4, 0x6C, 0xAC, 0xAD, 0x6D, 0xAF, 0x6F,
0x6E, 0xAE, 0xAA, 0x6A, 0x6B, 0xAB, 0x69, 0xA9, 0xA8, 0x68, 0x78, 0xB8, 0xB9, 0x79, 0xBB,
0x7B, 0x7A, 0xBA, 0xBE, 0x7E, 0x7F, 0xBF, 0x7D, 0xBD, 0xBC, 0x7C, 0xB4, 0x74, 0x75, 0xB5,
0x77, 0xB7, 0xB6, 0x76, 0x72, 0xB2, 0xB3, 0x73, 0xB1, 0x71, 0x70, 0xB0, 0x50, 0x90, 0x91,
0x51, 0x93, 0x53, 0x52, 0x92, 0x96, 0x56, 0x57, 0x97, 0x55, 0x95, 0x94, 0x54, 0x9C, 0x5C,
0x5D, 0x9D, 0x5F, 0x9F, 0x9E, 0x5E, 0x5A, 0x9A, 0x9B, 0x5B, 0x99, 0x59, 0x58, 0x98, 0x88,
0x48, 0x49, 0x89, 0x4B, 0x8B, 0x8A, 0x4A, 0x4E, 0x8E, 0x8F, 0x4F, 0x8D, 0x4D, 0x4C, 0x8C,
0x44, 0x84, 0x85, 0x45, 0x87, 0x47, 0x46, 0x86, 0x82, 0x42, 0x43, 0x83, 0x41, 0x81, 0x80,
0x40]


class three_finger_gripper():
    def __init__(self,comport='/dev/ttyUSB0'):
        '''
        comport='/dev/ttyUSB0'
        '''
        self._comport=comport
        self.ser = serial.Serial(comport,115200,timeout = 0.2)
        self.active()

    def active(self):
        '''
        just for start 
        '''
        print("initing...")
        self.ser = serial.Serial(self._comport,115200,timeout = 0.2)
        rGTO=1
        rACT=1
        rmode=0
        Action_request_byte0= (rGTO << 3) + (rmode << 1) + rACT
        act_cmd = [0x09, 0x10, 0x03, 0xE8, 0x00, 0x03, 0x06, Action_request_byte0, 0x00, 0x00, 0x00, 0x00, 0x00]
        
        self._compute_modbus_rtu_crc(act_cmd)

        act_cmd_bytes=array.array('B',act_cmd).tostring()
        self.ser.write(act_cmd_bytes)

        data_raw = self.ser.readline()
        data = binascii.hexlify(data_raw)
        while(not self._check_active()):
            pass
        print("initing OK")

    def deactive(self):
        '''
        turn off gripper
        '''
        stat_cmd = [0x09, 0x10, 0x03, 0xE8, 0x00, 0x03, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

        act_cmd=stat_cmd

        self._compute_modbus_rtu_crc(act_cmd)

        act_cmd_bytes=array.array('B',act_cmd).tostring()
        self.ser.write(act_cmd_bytes)

        data_raw = self.ser.readline()
        data = binascii.hexlify(data_raw)
        print("shutdown")
        self.ser.close()

    def move_gripper(self,mode,pos,Force,Speed):
        '''
        mode="Basic" | "Pinch" | "Wide" | "Scissor" \n
        pos=0 to 255 (define by mode)               \n
        Force=0 to 255                              \n
        Speed=0 to 255                              \n
        '''
        pos,Force,Speed=self._check_pos_force_speed(mode,pos,Force,Speed)
        mode_num=0
        if mode == "Basic":
            mode_num=0
        elif mode == "Pinch":
            mode_num=1
        elif mode == "Wide":
            mode_num=2
        elif mode == "Scissor":
            mode_num=3

        rGTO=1
        rACT=1
        rmode=mode_num
        Action_request_byte0= (rGTO << 3) + (rmode << 1) + rACT
        stat_cmd = [0x09, 0x10, 0x03, 0xE8, 0x00, 0x03, 0x06, Action_request_byte0, 0x00, 0x00, pos,Force,Speed]

        act_cmd=stat_cmd
        self._compute_modbus_rtu_crc(act_cmd)

        act_cmd_bytes=array.array('B',act_cmd).tostring()
        self.ser.write(act_cmd_bytes)

        data_raw = self.ser.readline()
        data = binascii.hexlify(data_raw)
        while(not self._whether_gripper_stop()):
            pass

    def individual_move_gripper(self,pos,Speed,Force):
        '''
        pos   = [A_pos,B_pos,C_pos]         \n
        Speed = [A_speed,B_speed,C_speed]   \n
        Force = [A_force,B_force,C_force]   \n
        '''
        A_info=[]
        B_info=[]
        C_info=[]

        A_info,B_info,C_info=self._individual_check_pos_force_speed(["A","B","C"],pos,Speed,Force)

        act_cmd = [0x09, 0x10, 0x03, 0xE8, 0x00, 0x06, 0x0C, 0x09, 0x04, 0x00,A_info[0],A_info[1],A_info[2], B_info[0],B_info[1],B_info[2], C_info[0],C_info[1],C_info[2]]
        #act_cmd = [0x09, 0x10, 0x03, 0xE8, 0x00, 0x06, 0x0C, 0x09, 0x04, 0x00,200 ,100,100 ,0,0,0 ,0,0,0]
        self._compute_modbus_rtu_crc(act_cmd)
        act_cmd_bytes=array.array('B',act_cmd).tostring()
        self.ser.write(act_cmd_bytes)
        data_raw = self.ser.readline()
        data = binascii.hexlify(data_raw)
        
        while(not self._whether_gripper_stop()):
            pass

    def _check_active(self):
        '''
        check active
        '''
        act_cmd = [0x09, 0x03, 0x07, 0xD0, 0x00, 0x01]
        
        self._compute_modbus_rtu_crc(act_cmd)

        act_cmd_bytes=array.array('B',act_cmd).tostring()
        self.ser.write(act_cmd_bytes)

        data_raw = self.ser.readline()
        data = binascii.hexlify(data_raw)
        #data_bindary=int.from_bytes(data,'big')
        hex_str = data.decode()
        hex_int = int(hex_str, 16)
        data_bindary = hex_int + 0x200

        data_bindary=(data_bindary & 0xFFFF0000) >> 16  #gripper status | object status
        data_bindary=data_bindary>>8                    #gripper status f9ff
        gMIC=(data_bindary & 0b00110000) >> 4           #gMIC
        if gMIC ==3:
            return True
        return False

    def _whether_gripper_stop(self):
        '''
        check whether gripper stop
        '''
        act_cmd = [0x09, 0x03, 0x07, 0xD0, 0x00, 0x01]
    
        self._compute_modbus_rtu_crc(act_cmd)

        act_cmd_bytes=array.array('B',act_cmd).tostring()
        self.ser.write(act_cmd_bytes)

        data_raw = self.ser.readline()
        data = binascii.hexlify(data_raw)
        
        hex_str = data.decode()
        hex_int = int(hex_str, 16)
        data_bindary = hex_int + 0x200

        data_bindary=(data_bindary & 0xFFFF0000) >> 16  #gripper status | object status
        data_bindary=data_bindary>>8                    #gripper status f9ff
        gSTA=(data_bindary & 0b11000000) >> 6           #gSTA 
        
        if gSTA > 0 :
            if gSTA == 1 :
                print("Gripper is stopped. One or two fingers stopped before requested position")
            elif gSTA == 2 :
                print("Gripper is stopped. All fingers stopped before requested position")
            else :
                print("Gripper is stopped. All fingers reached requested position")

            #_fingers_status()
            return True
        return False

    def _check_pos_force_speed(self,mode,pos,Force,Speed):
        '''
        change pos,Force,Speed for safe
        '''
        if mode == "Pinch":
            if pos>120:
                print("pos too big, change pos to 120")
                pos=120

        if pos>255:
                print("pos too big, change pos to 255")
                pos=255
        elif pos<0:
                print("pos too small, change pos to 0")
                pos=0

        if Force>255:
            print("Force too big, change Force to 255")
            Force=255
        elif Force<0:
            print("Force too small, change pos to 0")
            Force=0

        if Speed>255:
            print("Speed too big, change Speed to 255")
            Speed=255
        elif Speed<0:
            print("Speed too small, change pos to 0")
            Speed=0
        return pos,Force,Speed

    def _individual_check_pos_force_speed(self,finger_id,pos,Speed,Force):
        '''
        finger_id = ['A', 'B', 'C']         \n
        pos   = [A_pos,B_pos,C_pos]         \n
        Speed = [A_speed,B_speed,C_speed]   \n
        Force = [A_force,B_force,C_force]   \n
        '''
        all_info=[]
        index=0
        for finger in finger_id:
            if finger=="Scissor" and pos[index]>100:
                print("pos too big, change pos to 100")
                pos[index]=100
            elif pos[index]>255:
                print("pos too big, change pos to 255")
                pos[index]=255
            elif pos[index]<0:
                print("pos too small, change pos to 0")
                pos[index]=0
            
            if Force[index]>255:
                print("Force too big, change Force to 255")
                Force[index]=255
            elif Force[index]<0:
                print("Force too small, change pos to 0")
                Force[index]=0

            if Speed[index]>255:
                print("Speed too big, change Speed to 255")
                Speed[index]=255
            elif Speed[index]<0:
                print("Speed too small, change pos to 0")
                Speed[index]=0
            all_info.append([pos[index],Speed[index],Force[index]])
            index+=1
        
        #return A_info,    B_info,     C_info,     SS_info
        return all_info[0],all_info[1],all_info[2]

    def _compute_modbus_rtu_crc(self,buff):
        '''
        compute CRC
        '''
        crc_hi = 0xFF
        crc_low = 0xFF
        i = 0
        data_len = len(buff)
        while(data_len):
            idx = (crc_low ^ buff[i]) & 0xFF
            crc_low = (crc_hi ^ CRC_HI_TBL[idx]) & 0xFF
            crc_hi = CRC_LOW_TBL[idx] & 0xFF
            data_len-=1
            i+=1    
        buff.append(crc_low)
        buff.append(crc_hi)

    def _fingers_status(self):
        '''
        output all fingers status
        '''
        act_cmd = [0x09, 0x03, 0x07, 0xD0, 0x00, 0x01]
        self._compute_modbus_rtu_crc(act_cmd)

        act_cmd_bytes=array.array('B',act_cmd).tostring()
        self.ser.write(act_cmd_bytes)

        data_raw = self.ser.readline()
        data = binascii.hexlify(data_raw)
        data_bindary=int.from_bytes(data,'big')
        data_bindary=(data_bindary & 0xFFFF0000) >> 16  #gripper status | object status
        data_bindary=data_bindary & 0xFF                #object status
        data_bindary=data_bindary & 0b00111111          #gDTC | gDTB | gDTA
        if data_bindary>0:
            gDTA = data_bindary & 0b11
            gDTB = (data_bindary >> 2) & 0b11
            gDTC = (data_bindary >> 4) & 0b11
            if gDTA == 3:
                print("A finger is at request position")
            else : print("A finger touched something")

            if gDTB == 3:
                print("B finger is at request position")
            else : print("B finger touched something")

            if gDTC == 3:
                print("C finger is at request position")
            else : print("C finger touched something")

##########################################################
#control

gripper=three_finger_gripper()

print("Basic mode")
print("close_gripper")
gripper.move_gripper("Basic",255,100,100)
print("open_gripper")
gripper.move_gripper("Basic",0,100,100)

print("Pinch mode")
print("close_gripper")
gripper.move_gripper("Pinch",110,100,100)
print("open_gripper")
gripper.move_gripper("Pinch",0,100,100)

print("Wide mode")
print("close_gripper")
gripper.move_gripper("Wide",200,100,100)
print("open_gripper")
gripper.move_gripper("Wide",0,100,100)

print("Scissor mode")
print("close_gripper")
gripper.move_gripper("Scissor",200,100,100)
print("open_gripper")
gripper.move_gripper("Scissor",0,100,100)

print("Basic mode")
print("close_gripper")
gripper.move_gripper("Basic",255,100,100)
print("open_gripper")
gripper.move_gripper("Basic",0,100,100)
#######################################################################

print("one finger move")
print("finger A")
gripper.individual_move_gripper([255,0,0],[255,0,0],[255,0,0])
gripper.individual_move_gripper(  [0,0,0],[255,0,0],[255,0,0])

print("finger B")
gripper.individual_move_gripper([0,255,0],[0,255,0],[0,255,0])
gripper.individual_move_gripper(  [0,0,0],[0,255,0],[0,255,0])

print("finger C")
gripper.individual_move_gripper([0,0,200],[0,0,255],[0,0,255])
gripper.individual_move_gripper(  [0,0,0],[0,0,255],[0,0,255])

gripper.deactive()

