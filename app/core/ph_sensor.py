import io
import fcntl
import time
import string


class PHSensor(object):
    _long_timeout = 1.5
    _short_timeout = .5
    _default_bus = 1
    _default_address = 98
    _current_addr = _default_address

    _file_read = None
    _file_write = None


    def __init__(self, address=_default_address, bus=_default_bus):
        try:
            self._file_read = io.open("/dev/i2c-"+str(bus), "rb", buffering=0)
            self._file_write = io.open("/dev/i2c-"+str(bus), "wb", buffering=0)

            self._set_i2c_address(address)

        except:
            print("Couldn't initialize PH sensor. Possibly unsupported OS.")

    def start(self):
        self._set_i2c_address(self._default_address)


    def get_reading(self):
        query_resp = self._query("R")

        return self._read()

    #
    # INTERNAL METHODS
    #

    def _activate_i2c_mode(self):
        # Reboots and sets I2C address, using _default_address for now

        # TODO: think through making this dynamic

        return self._query('I2C,%s' % self._default_address)

    def _activate_uart_mode(self):
        return self._query('BAUD,9600')

    def _set_i2c_address(self, addr):
        I2C_SLAVE = 0x703

        fcntl.ioctl(self._file_read, I2C_SLAVE, addr)
        fcntl.ioctl(self._file_write, I2C_SLAVE, addr)

        self._current_addr = addr

    def _query(self, string):
        self._write(string)

        if((string.upper().startswith("R")) or (string.upper().startswith("CAL"))):
            time.sleep(self._long_timeout)

        elif string.upper().startswith("SLEEP"):
            return "sleep mode"

        else:
            time.sleep(self._short_timeout)

        return self._read()

    def get_led_status(self):
        r = None
        query_resp = self._query('L,?')

        if query_resp == '?L,1':
            r = True
        else:
            r = False

        return r

    def set_led_status(self, status=True):
        query_format = 'L,%s'
        q = None

        if status:
            q = query_format % '1'
        else:
            q = query_format % '0'

        return self._query(q)

    def find(self):
        # Blinks the onboard LED rapidly to visually identify

        self._query('FIND')

    def _write(self, cmd):
        cmd += "\00"
        self._file_write.write(cmd)

    def _read(self, num_of_bytes=31):
        res = self._file_read.read(num_of_bytes)
        response = filter(lambda x: x != '\x00', res)

        if ord(response[0]) == 1:
            char_list = map(lambda x: chr(ord(x) & ~0x80), list(response[1:]))

            return "Command succeeded " + ''.join(char_list)
        else:
            return "Error " + str(ord(response[0]))
