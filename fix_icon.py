import struct, os, shutil

def fix_icon_pefile(exe_path, ico_path):
    import pefile
    
    pe = pefile.PE(exe_path)
    
    # Parse ICO
    with open(ico_path, 'rb') as f:
        ico = f.read()
    reserved, icotype, count = struct.unpack('<HHH', ico[:6])
    
    ico_entries = []
    pos = 6
    for i in range(count):
        w, h, colors, res, planes, bitcount, bytes_in_res, img_offset = struct.unpack('<BBBBHHII', ico[pos:pos+16])
        ico_entries.append({'w': w, 'h': h, 'bytes': bytes_in_res, 'offset': img_offset, 'id': i+1})
        pos += 16
    
    # Find RT_GROUP_ICON and RT_ICON resources in PE
    for entry in pe.DIRECTORY_ENTRY_RESOURCE.entries:
        if entry.id == 14:  # RT_GROUP_ICON
            for e2 in entry.directory.entries:
                for res in e2.directory.entries:
                    data_rva = res.data.struct.OffsetToData
                    size = res.data.struct.Size
                    old_data = pe.get_data(data_rva, size)
                    # Parse old group to get IDs
                    old_count = int.from_bytes(old_data[4:6], 'little')
                    # Build new group
                    new_grp = struct.pack('<HHH', 0, 1, count)
                    for e in ico_entries:
                        w = 0 if e['w'] == 256 else e['w']
                        h = 0 if e['h'] == 256 else e['h']
                        new_grp += struct.pack('<BBBBHHih', w, h, 0, 0, 1, 32, e['bytes'], e['id'])
                    # Pad to old size if needed
                    if len(new_grp) < size:
                        new_grp += b'\x00' * (size - len(new_grp))
                    elif len(new_grp) > size:
                        # Need to reallocate - just overwrite and let pefile handle
                        pass
                    pe.set_bytes_at_rva(data_rva, new_grp[:size] if len(new_grp) > size else new_grp)
                    print("Replaced RT_GROUP_ICON: %d entries -> %d" % (old_count, count))
        
        if entry.id == 3:  # RT_ICON
            for e2 in entry.directory.entries:
                for res in e2.directory.entries:
                    data_rva = res.data.struct.OffsetToData
                    size = res.data.struct.Size
                    # Find matching icon entry by ID
                    icon_id = res.id
                    matching = [e for e in ico_entries if e['id'] == icon_id]
                    if matching:
                        e = matching[0]
                        img_data = ico[e['offset']:e['offset']+e['bytes']]
                        if len(img_data) <= size:
                            pe.set_bytes_at_rva(data_rva, img_data)
                            print("  Replaced RT_ICON #%d: %dx%d" % (icon_id, e['w'], e['h']))
    
    pe.write(exe_path)
    print("SUCCESS")

script_dir = os.path.dirname(os.path.abspath(__file__))
exe = os.path.join(script_dir, 'dist', 'OW语音触发器.exe')
ico = os.path.join(script_dir, 'icon.ico')
fix_icon_pefile(exe, ico)
