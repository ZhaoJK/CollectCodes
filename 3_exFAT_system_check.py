# -*- coding: utf-8 -*-
#to check exFAT system
#Modification needed if try to look for CHECK files


# -*-coding:utf-8-*-
import binascii
import re
import os

"""
device_type={'type_guid':'',' lba_start','lba_end':'','partition_mbyte'}
"""
DISK_IS_GPT = 0
DISK_IS_MBR = 1
PARTITION_TABLE_SECTOR = 32
ONE_SECTOR_BYTES = 512


def check_gpt_or_mbr(device):
    """
    this is device is gpt or mbr
    :param device: mount device
    :return:0 is gpt，1 is mbr
    """
    with open(device, 'rb') as disk:
        disk_type = disk.read(ONE_SECTOR_BYTES)[450]
        if disk_type == 238:  # ee的十进制为238
            return DISK_IS_GPT
        else:
            return DISK_IS_MBR


def sort_out_partition_item_guid(guid_str):
    """
    this is calc guid
    :param guid_str:guid_str is hex str
    :return: update_guid
    """
    test = str(guid_str)
    guid = "".join([i for index, i in enumerate(test) if index != 0]).replace('\'', '')
    footer = guid[-12:]
    intermediate1 = guid[-16:-12]
    intermediate0 = guid[12:16]  # d211
    result = re.sub(r"(?<=\w)(?=(?:\w\w)+$)", " ", guid[:12]).split(' ')
    result1 = re.sub(r"(?<=\w)(?=(?:\w\w)+$)", " ", intermediate0).split(' ')
    intermediate0 = "".join(result1[::-1])  # 11d2
    header = "".join(result[:4][::-1])
    intermediate = "".join(result[4:][::-1])
    update_guid = header + '-' + intermediate + '-' + intermediate0 + '-' + intermediate1 + '-' + footer
    return update_guid


def split_first_sector(b_stream, device_type):
    step = 128 if device_type == DISK_IS_GPT else 16
    for _i in range(0, len(b_stream), step):
        yield b_stream[_i:_i + step]


def partition_info_gpt(disk, device_type):
    device_info = []  # Used to store disk information
    for i in range(PARTITION_TABLE_SECTOR):  # Iterate through the sectors of 32 partition table entries
        byte_stream = disk.read(ONE_SECTOR_BYTES)
        if i > 1 and int(binascii.b2a_hex(byte_stream), 16) != 0:
            for partition in split_first_sector(byte_stream, device_type):
                check = binascii.b2a_hex(partition)
                partition_info = {
    }  # Used to store partition information
                if int(check, 16) != 0:
                    partition_info['type_guid'] = sort_out_partition_item_guid(
                        binascii.b2a_hex(partition[0:16]))
                    partition_info['lba_start'] = int.from_bytes(partition[32:40], 'little')
                    partition_info['lba_end'] = int.from_bytes(partition[40:48], 'little')
                    partition_mbyte = (partition_info['lba_end'] - partition_info[
                        'lba_start'] + 1) * ONE_SECTOR_BYTES // (
                                              1024 * 1024)
                    partition_info['partition_mbyte'] = partition_mbyte
                    device_info.append(partition_info)
    return device_info


def partition_info_mbr(disk, device_type):
    device_info = []
    header_bytes = disk.read(ONE_SECTOR_BYTES)
    partition_info = header_bytes[446:510]
    for partition in split_first_sector(partition_info, device_type):
        check = binascii.b2a_hex(partition)
        partition_info = {
    }
        check_activity = hex(partition[0])
        if int(check,16) != 0:  # Check if the partition table entry is a meaningful partition table entry and is the active partition

            partition_info['check_activity'] = check_activity
            partition_info['check_main'] = hex(partition[4])
            partition_info['lba_start'] = int.from_bytes(partition[8:12], 'little')
            sum_sector = int.from_bytes(partition[12:16], 'little')
            partition_info['lba_end'] = sum_sector + partition_info['lba_start']
            partition_info['partition_GB'] = (partition_info['lba_end'] - partition_info[
                'lba_start'] + 1) * ONE_SECTOR_BYTES // (1024 * 1024 *1024)
            device_info.append(partition_info)
    return device_info

def partition_detail_mbr(device):
    partition_detail = {}
    
    device_type = check_gpt_or_mbr(device)
    with open(device, 'rb') as disk:    
        partition_info = partition_info_mbr(disk, device_type)[0]
        
        disk.seek(partition_info['lba_start'] * ONE_SECTOR_BYTES, 0)
        header_bytes = disk.read(ONE_SECTOR_BYTES)
        
        check = binascii.b2a_hex(header_bytes)
        if int(check,16) != 0:
            partition_detail['partition_offset'] = int.from_bytes(header_bytes[64:67],"little")
            partition_detail['volume_length'] = int.from_bytes(header_bytes[72:79], 'little')
            partition_detail['fat_offset'] = int.from_bytes(header_bytes[80:83], 'little')
            partition_detail['fat_length'] = int.from_bytes(header_bytes[84:87], 'little')
            partition_detail['cluster_heap_offset'] = int.from_bytes(header_bytes[88:91], 'little')            
            partition_detail['cluster_count'] = int.from_bytes(header_bytes[92:95], 'little')
            partition_detail['root_dir_1stcluster'] = int.from_bytes(header_bytes[96:99], 'little')
            partition_detail['bytes_per_sector'] = 2 ** int(header_bytes[108])
            partition_detail['sectors_per_cluster'] = 2 ** int(header_bytes[109])
    return partition_detail

def root_vol_recorder(b_name):
    root_vol = ""
    if hex(b_name[0]) == "0x83":
        name_size = int(b_name[1])
        root_vol = b_name[2:(2 + 2*name_size)].decode('unicode_escape')
    return root_vol

#read_time_stamp did not work
#should be re-write according to Linux io core.
def read_time_stamp(b_name):
    t_second = int(b_name[0] & 0b00011111) * 2
    t_minute = int((b_name[0] & 0b11100000 >> 5) | (b_name[1] & 0b00000111 << 3))
    t_hour = int(b_name[1] & 0b11111000 >> 3)
    t_day = int(b_name[2] & 0b00011111)
    t_month = int((b_name[2] & 0b11100000 >> 5) | (b_name[3] & 0b00000001 << 3))
    t_year = int(b_name[3] & 0b01111110 >> 1) + 1984
    #print(t_year)
    return ""

def byte_to_unicode(b_name):
    length_byte = len(b_name)
    str_unicode = ""
    for i in range(length_byte//2):
        int_cha = int.from_bytes(b_name[2*i:(2*i+1)], 'big')

        #print(hex(int_cha))        
        #print(str(int.from_bytes(b_name[i:(i+1)], "little")).encode("utf-8").decode("utf-8") )
        #str_unicode = str_unicode + str(int_cha).encode("utf-8").decode("utf-8") 
        str_unicode = str_unicode + chr(int_cha)
    return str_unicode

def read_file_name(b_name, file_name_size):
    seg_file_name = file_name_size // 15
    remainder_file_name = file_name_size % 15
    file_name = ""
    seg_from = 64
    seg_end = 93
    #print(file_name_size)
    if seg_file_name > 0:
        for i in range(seg_file_name):
            file_name = file_name + byte_to_unicode(b_name[seg_from:seg_end])
            seg_from = seg_from + 32 * (i+1)
            seg_end = seg_end + 32 * (i+1)
    seg_end = seg_from  + remainder_file_name * 2 + 1
    file_name = file_name + byte_to_unicode(b_name[seg_from:seg_end])
    return file_name.replace("\x00", "")

def f_detail_read(b_name):
    f_detail = {}    
    check = binascii.b2a_hex(b_name)
    if int(check,16) != 0:       
        f_detail['file_att'] = int.from_bytes(b_name[2:3], 'little')
        # f_detail['create_time'] = read_time_stamp(b_name[6:10])
        # f_detail['modify_time'] = int(b_name[10:13], 8)
        # f_detail['visit_time'] = int(b_name[14:17], 8)
        # f_detail['create_time_ms'] = int(b_name[18])            
        f_detail['secondary_flags'] = int(b_name[31])
        f_detail['file_name_size'] = int(b_name[33])
        f_detail['file_size'] = int.from_bytes(b_name[54:61], 'little')
        f_detail['cluster_start'] = int.from_bytes(b_name[50:53], 'little')
        f_detail['file_name'] = read_file_name(b_name, f_detail['file_name_size']) 
        #print(f_detail['file_name_size'])
        #print(f_detail['file_name'])
    return f_detail   

# def root_del_recorder(b_name):
#     return root_vol


def dir_detail_mbr(device, cluster_start_dir):
    f_detail = {}
    root_detial = []
    partition_detail = partition_detail_mbr(device)
    
    with open(device, 'rb') as disk:      
        #disk.seek((partition_detail['partition_offset'] + partition_detail['cluster_heap_offset'] + (partition_detail['root_dir_1stcluster'] - 2) * partition_detail['sectors_per_cluster']) * partition_detail['bytes_per_sector'], 0)
        disk.seek((partition_detail['partition_offset'] + partition_detail['cluster_heap_offset'] + (cluster_start_dir - 2) * partition_detail['sectors_per_cluster']) * partition_detail['bytes_per_sector'], 0)
        header_bytes = disk.read(2)
        while int(header_bytes[0]) > 0:
            #print(hex(header_bytes[0]))
            #print(int(header_bytes[1]))
            dir_offset = disk.tell() - 2
            entry_type = hex(header_bytes[0])
            entry_type_count = int(header_bytes[1])
            if  entry_type == "0x5" or entry_type == "0x85":
                disk.seek(-2,1)
                header_bytes = disk.read(32 + entry_type_count * 32 )
                f_detail = f_detail_read(header_bytes[2:])
                f_detail["file_dir_offset"] = dir_offset 
                f_detail["file_dir_del_sign"] = entry_type
                f_detail["CheckSum"] = EntrySetChecksum(header_bytes)
                root_detial.append(f_detail)
                #break
            else:
                disk.seek(30,1)
            header_bytes = disk.read(2)
    return root_detial


def from_sector_partition_item(device):
    """
    statistics disk information
    :param device:mount device
    :return:device_info
    """
    device_type = check_gpt_or_mbr(device)

    with open(device, 'rb') as disk:
        if device_type == DISK_IS_GPT:  # Gpt partition when equal to 0
            return partition_info_gpt(disk, device_type), device_type
        else:
            result = partition_info_mbr(disk, device_type)
            return result, device_type
def copy_data(device, partition_detail, img_offset, img_size, out_file_name):
    
    with open(device, 'rb') as disk:      
        #disk.seek((partition_detail['partition_offset'] + partition_detail['cluster_heap_offset'] + (partition_detail['root_dir_1stcluster'] - 2) * partition_detail['sectors_per_cluster']) * partition_detail['bytes_per_sector'], 0)
        disk.seek((partition_detail['partition_offset'] + partition_detail['cluster_heap_offset'] + (img_offset - 2) * partition_detail['sectors_per_cluster']) * partition_detail['bytes_per_sector'], 0)
        print(out_file_name)
        with open(out_file_name,'wb') as f2:
            len_coped = 0
            buf_size = 2048
            while True:
                len_coped = len_coped + 2048
                if len_coped > img_size:
                    buf_size = img_size - len_coped + 2048
                    buf=disk.read(buf_size)
                    f2.write(buf)
                    break
                buf=disk.read(buf_size)
                f2.write(buf)

#Implement based on linux C code
def EntrySetChecksum(header_bytes):
        entry_type = hex(header_bytes[0])
        #print("----------------")

        entry_count = int(header_bytes[1])
        bytes_count = (entry_count + 1)* 32
        
        #print(entry_type)
        #print(bytes_count)
         
        Checksum = 0
        for i in range(bytes_count):
            if i == 2 or i == 3:
                continue 
            #print(hex(Checksum))
            #Checksum = (((Checksum & 1) << 15) | ((Checksum & 0xFFFE) >> 1)) + int(header_bytes[i])
            Checksum = ((Checksum << 15) | (Checksum >> 1)) + int(header_bytes[i])
            Checksum = Checksum & 0xFFFF
        return hex(Checksum)    
      
#no permison to write any bites               
def partition_write(device):
    """
    statistics disk information
    :param device:mount device
    :return:device_info
    """

    with open(device, 'wb') as disk:
        disk.seek(66068416, 0)
        disk.write(0x85)
        return True

if __name__ == "__main__":
    # gpt_or_mbr=0 is gpt or gpt_or_mbr=mbr
    
    device = '\\\\.\\PHYSICALDRIVE1'
    partition_detail = partition_detail_mbr(device)
    
    for key in partition_detail:
        print(key, '->', partition_detail[key])
        
    print("------------------------")
    
    root_detail = dir_detail_mbr(device, partition_detail["root_dir_1stcluster"])
    for file in root_detail:
       if str(file.get('file_name')).__contains__("20211129"):  
           print("*************************")
           for key in file:
               print(key, '->', file[key])        
    # dir_detail = dir_detail_mbr(device, 9832672)
    # for file in dir_detail:
    #     print(file)
        # if file['file_size'] > 0 and file['file_name'].__contains__('Exif'):
        #     out_file_name = "f:\\\\mSkin_label_Feo_20211129_Gpx\\\\OMETIFF_Gpx4-Sc7ac\\\\" + file['file_name'].replace("-Exif", ".tif")
        #     out_file_name = out_file_name.encode("utf-8").decode("utf-8")
        #     #print(out_file_name)
        #     copy_data(device, partition_detail, file['cluster_start'], file['file_size'],out_file_name)
    
