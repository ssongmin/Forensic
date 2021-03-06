#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys


try:
    input = raw_input
except:
    pass


class MBRParser:
    def __init__(self):
        print("")
    

    def _get_num(self):
        num = None
        try:
            num = int(input("[~] Enter the hard number to analyze  : "))
        except ValueError:
            print("[!] Enter a number ")
            self._get_num()
        self.start_parse(num)

    def start_parse(self, num):
        f = open('\\\\.\\PhysicalDrive'+str(num), 'rb')
        f.seek(0)
        self.show_hex_view(f)
        f.seek(0)
        buf = bytearray(f.read(0x200))

        self.PartitionEntry1 = PartitionEntry(buf[0x01BE:0x01CE], 1)
        self.PartitionEntry2 = PartitionEntry(buf[0x01CE:0x01DE], 2)
        self.PartitionEntry3 = PartitionEntry(buf[0x01DE:0x01EE], 3)
        self.PartitionEntry4 = PartitionEntry(buf[0x01EE:0x01FE], 4)

        num = int(input("[~] Enter the NTFS partition area to analyze  : "))
        f.seek(0)
        startVbr = 0
        choices = {
            1   :   self.PartitionEntry1.StartLBA*512,
            2   :   self.PartitionEntry2.StartLBA*512,
            3   :   self.PartitionEntry3.StartLBA*512,
            4   :   self.PartitionEntry4.StartLBA*512,
        }

        startVbr = choices.get(num)
        f.seek(startVbr)
        NTFSParser(f, startVbr)

    def show_hex_view(self, f):
        
        offset = 0
        while True:
            
            data = f.read(16)
            ldata = len(data)
            
            if ldata==0:break
            output = '%08X : ' % (offset)
            for i in range(ldata) : output += '%02X ' % data[i]
            if ldata != 16:
                for i in range(16 - ldata): output += '   '
            for i in range(ldata):
                if(data[i])>=0x20 and (data[i])<=0x7E : output += chr(data[i])
                else: output+='.'
            print(output)

            offset+=16
            if (offset%512 == 0): break


class PartitionEntry:

    def __init__(self, data, num):
        a = CustomMath()
        self.BootableFlag = data[0x00]
        self.StartCHS = a.CgLittleEndian(data[0x01:0x04])
        self.PartitionType = data[0x04]
        self.EndCHS = a.CgLittleEndian(data[0x05:0x08])
        self.StartLBA = a.CgLittleEndian(data[0x08:0x0C])
        self.SizeInSector = a.CgLittleEndian(data[0x0C:0x10])
        if(self.is_empty() is False):
            print("----------------PartitionEntry%d------------------------" % num)
            self.show_partition_table()

    def show_partition_table(self):
        print ("[+] BootableFlag : 0x%x" % self.BootableFlag)
        print ("[+] StartCHS : %d" % self.StartCHS)
        print ("[+] PartitionType : 0x%x" % self.PartitionType)
        print ("[+] EndCHS : %d" % self.EndCHS)
        print ("[+] StartLBA : %d" % self.StartLBA)
        print ("[+] SizeInSector : %d" % self.SizeInSector)

    def is_empty(self):
        if self.PartitionType == 0:
            return True
        else:
            return False

class CustomMath:
    def CgLittleEndian(self, buf):
        val=0
        for i in range(0,len(buf)):
            multi=1
            for j in range(0,i):
                multi *= 256
            val += buf[i] * multi
        return val

    def CgBigEndian(self, buf):
        val =0
        for i in range(0, len(buf)):
            multi= pow(256, len(buf)-1)
            for j in range(0,i):
                multi /= 256
            val += buf[i] * multi
        return int(val)

class NTFSParser:
    def __init__(self, f, startVbr):
        data = bytearray(f.read(0x200))
        self.show_hex_view(data, startVbr)
        a = CustomMath()
        self.JumpBootCode = a.CgBigEndian(data[0x00:0x03])
        self.OEMID = a.CgBigEndian(data[0x03:0x0B])
        self.BytesPerSector = a.CgLittleEndian(data[0x0B:0x0D])
        self.SectorsPerCluster = data[0x0D]
        self.ReservedSectors = a.CgLittleEndian(data[0x0E:0x10])
        self.HiddenSectors = a.CgLittleEndian(data[0x1C:0x20])
        self.TotalSectors = a.CgLittleEndian(data[0x28:0x30])
        self.MFTClusterNumberForFile = a.CgLittleEndian(data[0x30:0x38])
        self.VolumeSerialNumber = a.CgLittleEndian(data[0x48:0x50])
        self.Signature = a.CgBigEndian(data[0x01FE:0x0200])
        self.show_ntfs()

    def show_ntfs(self):
        print ("[+] JumpBootCode : 0x%x" % self.JumpBootCode)
        print ("[+] OEMID : 0x%x" % self.OEMID)
        print ("[+] BytesPerSector : %d" % self.BytesPerSector)
        print ("[+] SectorsPerCluster : %d" % self.SectorsPerCluster)
        print ("[+] ReservedSectors : %d" % self.ReservedSectors)
        print ("[+] HiddenSectors : %d" % self.HiddenSectors)
        print ("[+] TotalSectors : %d" % self.TotalSectors)
        print ("[+] MFTClusterNumberForFile : %d" % self.MFTClusterNumberForFile)
        print ("[+] VolumeSerialNumber : %d" % self.VolumeSerialNumber)
        print ("[+] Signature : 0x%x" % self.Signature)
    

    def show_hex_view(self, f, startVbr):

        offset = startVbr
        s =0
        while True:
            data = f[s : (s+16)]
            ldata = len(data)

            if ldata==0:break
            output = '%08X : ' % (offset)
            for i in range(ldata) : output += '%02X ' % data[i]
            if ldata != 16:
                for i in range(16 - ldata): output += '   '
            for i in range(ldata):
                if(data[i])>=0x20 and (data[i])<=0x7E : output += chr(data[i])
                else: output+='.'

            print(output)

            offset+=16
            s+=16
            if (offset%512 == 0): break

def main():
    parser = MBRParser()
    parser._get_num()

if __name__ == "__main__":
    main()