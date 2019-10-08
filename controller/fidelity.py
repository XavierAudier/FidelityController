import logging
import serial
import serial.tools.list_ports

class FidelityDevice():

    # default connection settings
    connection_settings = {
            'baudrate': 9600,
            # 'baudrate': 19200,
            'bytesize': 8,
            'parity': 'N',
            'stopbits': 1,
            'xonxoff': 0,
            'dsrdtr': False,
            'rtscts': 0,
            'timeout': 0.5,
            'write_timeout': None,
            'inter_byte_timeout': None
            }

    def __init__(self, port=None):
            self.__gdd = None
            self.__power = None
            self.__port = port
            self.__version = None
            self.__dev = None
            if self.__port is not None:
                self.connect_to_port()
                if self.is_connected():
                    logging.info("Connection to Fidelity on Port " + self.__port + " successful.")
                else:
                    logging.warning("Connection to Fidelity on Port " + self.__port + " UNSUCCESSFUL, attempting to scan all available ports.")
                    self.scan_for_port()


    def __del__(self):
        try:
            if self.__dev is not None:
                self.__dev.close()
        except:
            pass

    def connect_to_port(self, port=None):
        if port is not None:
            self.__port = port
        try:
            self.__dev = serial.serialwin32.Serial(port=self.__port)
        except serial.serialutil.SerialException:
            try:
                self.__dev.close()
                self.__dev = serial.serialwin32.Serial(port=self.__port)
            except:
                self.__dev = None
        
        if self.__dev is not None:
            self.__dev.apply_settings(self.connection_settings)

    def is_connected(self):
        self.read_version_number()
        if self.__version is not None:
            self.read_gdd()
            if self.__gdd is not None:
                return True
        return False

    def scan_for_port(self):
        for port in serial.tools.list_ports.comports():
            self.__port = port.device
            self.connect_to_port()
            if self.is_connected():
                print("Connection established to port " + str(self.__port))
                break
            else:
                print("Connection to port " + str(self.__port) + " failed")
                try:
                    self.__dev.close()
                except:
                    pass

    @property
    def gdd(self):
        return self.__gdd

    @gdd.setter
    def gdd(self, gdd):
        self.__gdd = gdd
          
    @property
    def power(self):
        return self.__power

    @power.setter
    def power(self, power):
        self.__power = power  

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, port):
        self.__port = port
        
    def switch_to_standy(self):
        raise(NotImplementedError)

    def switch_to_on(self):
        raise(NotImplementedError)
    
    def switch_to_high_power(self):
        raise(NotImplementedError)
    
    def switch_to_alignment(self):
        raise(NotImplementedError)
  
    def laser_on(self):
        self.send_command(b"laseron=1\r\n", respond=False)
        
    def laser_off(self):
        self.send_command(b"laseron=0\r\n", respond=False)

    def high_power_on(self):
        self.send_command(b"hpon=1\r\n", respond=False)
        
    def high_power_off(self):
        self.send_command(b"hpon=0\r\n", respond=False)

    def motor_go_to(self, position=0):
        if position < -10000 or position > 10000:
            logging.warning("The request motor position is out of range (-10000, +10000).")
        else:
            if type(position) is not int:
                logging.warning("The request motor position is converted to int.")
                position = int(position)
            response = self.send_command(b"motorgoto={0:d}\r\n".format(position), respond=True)

    def read_gdd(self):
        # reads the GDD from the device, actualizes the instance value, but does not return it.
        gdd_str = self.send_command(b"GDD?\r\n", respond=True)
        if gdd_str is not None:
            try:
                gdd = float(gdd_str)
                if gdd < -100000 or gdd > 100000:
                    logging.warning("The device GDD seems to be out of range (-100000, +100000).")
                else:
                    self.gdd = gdd
            except:
                logging.warning("The device GDD query response is invalid.")
        else:
            self.gdd = None

    def read_power(self):
        # reads the power from the device, actualizes the instance value, but does not return it.
        power_str = self.send_command(b"power?\r\n", respond=True)
        power = int(power_str)
        if power < 0 or power > 3:
            logging.warning("The device power seems to be out of range (0W, 3W).")
        else:
            self.power = power

    def is_motor_homed(self):
        homed_str = self.send_command(b"motorhomed?\r\n", respond=True)
        return homed_str=="1"

    def motor_reset(self):
        self.send_command(b"motorreset\r\n", respond=False)

    def read_version_number(self):
        version_str = self.send_command(b"IDN?\r\n", respond=True)
        self.__version = version_str

    def get_presets(self):
        presets_str = self.send_command(b"presets?\r\n", respond=True)
        return presets_str    

    def get_version(self):
        if self.__version is None:
            self.read_version_number()
        return self.__version

    def get_connection_settings(self):
        return self.connection_settings

    def set_connection_settings(self, connection_settings):
        self.connection_settings = connection_settings

    def send_command(self, query=None, respond=True):
        if self.__dev is not None:
            self.__dev.write(query)
            msg = b""
            tmp_msg = self.__dev.readline()
            while tmp_msg is not b"":
                msg += tmp_msg
                tmp_msg = self.__dev.readline()
            if msg == b"":
                return None
            else:
                return msg.decode('utf-8')
