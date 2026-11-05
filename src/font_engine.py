"""
font_engine.py - Pure Python Font Embedding Rights & Checksum Engine
Reverse-engineered and enhanced from ttembed (Tom Murphy VII / hisdeedsaredust)
Includes Windows ReadOnly & System Lock handling, TrueType Collection (TTC) support,
and 100% OpenType checksum & head.checkSumAdjustment compliance.
"""

import os
import shutil
import stat
import struct
import uuid
from typing import Dict, List, Optional, Tuple, Any


# Standard OpenType / TrueType fsType embedding bitmasks
FSTYPE_INSTALLABLE = 0x0000        # Installable embedding (unrestricted)
FSTYPE_RESTRICTED = 0x0002         # Restricted License embedding (Bit 1)
FSTYPE_PREVIEW_PRINT = 0x0004      # Preview & Print embedding (Bit 2)
FSTYPE_EDITABLE = 0x0008           # Editable embedding (Bit 3)
FSTYPE_NO_SUBSET = 0x0100          # No subsetting allowed (Bit 8)
FSTYPE_BITMAP_ONLY = 0x0200        # Bitmap embedding only (Bit 9)

# Recognized SFNT signatures
SFNT_TRUETYPE_1 = b'\x00\x01\x00\x00'
SFNT_TRUETYPE_TRUE = b'true'
SFNT_TRUETYPE_TYP1 = b'typ1'
SFNT_OPENTYPE_CFF = b'OTTO'
SFNT_COLLECTION = b'ttcf'
SFNT_WOFF = b'wOFF'
SFNT_WOFF2 = b'wOF2'


def classify_file_format(file_path: str, header: bytes = b'') -> Tuple[str, str]:
    """
    Classifies unsupported or non-font files and provides clear, human-friendly guidance.
    Returns (format_name, human_friendly_explanation).
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if os.path.exists(file_path) and os.path.getsize(file_path) == 0:
        return "Empty File (0 Bytes)", "File is empty (0 bytes) and contains no font data."

    if len(header) < 12:
        return "Truncated File", "File is too small (< 12 bytes) to contain a valid font header."

    sfnt_tag = header[:4]
    
    if sfnt_tag == SFNT_WOFF or ext == '.woff':
        return "WOFF Web Font", "WOFF is a web-compressed font format and does not use desktop TrueType/OpenType fsType embedding flags. Please decompress to TTF/OTF first or use your original desktop font file."
    if sfnt_tag == SFNT_WOFF2 or ext == '.woff2':
        return "WOFF2 Web Font", "WOFF2 is a web-compressed font format and does not use desktop TrueType/OpenType fsType embedding flags. Please decompress to TTF/OTF first or use your original desktop font file."
    
    if ext == '.eot' or (len(header) >= 36 and header[34:36] == b'\x4c\x50'):
        return "Embedded OpenType (.EOT)", "Embedded OpenType (.eot) is a legacy Internet Explorer web font format and does not use standard desktop fsType tables. Use the source TrueType (.ttf) font."

    if header[:2] == b'MZ':
        if ext in ('.exe', '.dll', '.sys', '.scr', '.drv', '.ocx'):
            return f"Windows Executable ({ext.upper()})", f"'{os.path.basename(file_path)}' is an executable program, not a font file."
        elif ext == '.fon':
            return "Windows Bitmap Font (.FON)", "Legacy Windows .FON bitmap fonts do not contain OpenType SFNT tables or embedding flags."
        else:
            return "Binary Executable Container", "Legacy executable or bitmap container without OpenType tables."

    if ext == '.bdf' or header.startswith(b'STARTFONT'):
        return "Bitmap Font (.BDF)", "BDF is a legacy X11 bitmap font format without OpenType embedding tables."

    if ext in ('.pfa', '.pfb') or header.startswith(b'%!PS') or header.startswith(b'\x80\x01'):
        return f"PostScript Type 1 ({ext.upper()})", "PostScript Type 1 fonts (.pfa/.pfb) use Adobe Type 1 dictionaries rather than OpenType OS/2 fsType flags."

    if ext == '.svg' or b'<svg' in header.lower() or b'<?xml' in header.lower():
        return "SVG Font / Vector (.SVG)", "SVG fonts are XML vector specifications and do not use TrueType/OpenType binary embedding permissions."

    if ext in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.ico', '.tiff') or header.startswith(b'\x89PNG') or header.startswith(b'\xff\xd8\xff') or header.startswith(b'GIF'):
        return f"Image File ({ext.upper()})", f"Image file ({ext}) — only font files (.ttf, .otf, .ttc) are supported."

    if ext == '.pdf' or header.startswith(b'%PDF'):
        return "PDF Document", "PDF document — only font files (.ttf, .otf, .ttc) are supported."

    if ext in ('.txt', '.md', '.log', '.json', '.xml', '.csv', '.py', '.c', '.h', '.cpp', '.html', '.css', '.js'):
        return f"Text/Document ({ext.upper()})", f"Text/document file ({ext}) — only font files (.ttf, .otf, .ttc) are supported."

    if ext in ('.zip', '.rar', '.7z', '.tar', '.gz') or header.startswith(b'PK\x03\x04'):
        return f"Compressed Archive ({ext.upper()})", f"Compressed archive ({ext}) — please extract font files (.ttf/.otf) first."

    return "Unsupported Format", f"Unsupported file format (header signature: {sfnt_tag.hex()}). Only TrueType (.ttf), OpenType (.otf), and Collections (.ttc) are supported."



def decode_fstype(fstype: int) -> Dict[str, Any]:
    """
    Decodes an OS/2 fsType uint16 into human-readable details according to the OpenType spec.
    """
    base_bits = fstype & 0x000F
    
    if base_bits & FSTYPE_RESTRICTED:
        level_name = "Restricted License"
        level_desc = "Embedding prohibited without explicit legal license."
        level_code = FSTYPE_RESTRICTED
        status_category = "restricted"
    elif base_bits & FSTYPE_EDITABLE:
        level_name = "Editable Embedding"
        level_desc = "May be embedded in documents and used to edit documents."
        level_code = FSTYPE_EDITABLE
        status_category = "editable"
    elif base_bits & FSTYPE_PREVIEW_PRINT:
        level_name = "Preview & Print"
        level_desc = "May be embedded for viewing and printing only (read-only)."
        level_code = FSTYPE_PREVIEW_PRINT
        status_category = "preview"
    elif base_bits == 0:
        level_name = "Installable (Unrestricted)"
        level_desc = "May be embedded & permanently installed for all applications."
        level_code = FSTYPE_INSTALLABLE
        status_category = "installable"
    else:
        level_name = f"Legacy / Non-standard (0x{base_bits:02X})"
        level_desc = "Non-standard or legacy embedding flag."
        level_code = base_bits
        status_category = "custom"

    no_subset = bool(fstype & FSTYPE_NO_SUBSET)
    bitmap_only = bool(fstype & FSTYPE_BITMAP_ONLY)
    reserved_bits = fstype & (~(0x000E | FSTYPE_NO_SUBSET | FSTYPE_BITMAP_ONLY)) & 0xFFFF

    summary_parts = [level_name]
    if no_subset:
        summary_parts.append("No Subsetting")
    if bitmap_only:
        summary_parts.append("Bitmap Only")

    return {
        "raw_value": fstype,
        "hex_value": f"0x{fstype:04X}",
        "level_name": level_name,
        "level_desc": level_desc,
        "level_code": level_code,
        "status_category": status_category,
        "no_subset": no_subset,
        "bitmap_only": bitmap_only,
        "has_reserved": bool(reserved_bits),
        "reserved_bits": f"0x{reserved_bits:04X}",
        "summary": ", ".join(summary_parts)
    }


def compute_table_checksum(table_bytes: bytes) -> int:
    """
    Computes standard OpenType / TrueType 32-bit checksum for a table.
    Padded with zeros to a 4-byte boundary.
    Processes data in chunks to prevent high memory allocation on massive tables.
    """
    remainder = len(table_bytes) % 4
    if remainder != 0:
        table_bytes = table_bytes + (b'\x00' * (4 - remainder))
    
    total = 0
    chunk_size = 65536
    for i in range(0, len(table_bytes), chunk_size):
        chunk = table_bytes[i:i + chunk_size]
        num_words = len(chunk) // 4
        words = struct.unpack(f'>{num_words}I', chunk)
        total = (total + sum(words)) & 0xFFFFFFFF
    return total


def extract_names_from_table(name_bytes: bytes) -> Dict[str, str]:
    """
    Parses OpenType 'name' table bytes and returns common font metadata.
    """
    if len(name_bytes) < 6:
        return {}
    
    try:
        format_num, count, string_offset = struct.unpack('>HHH', name_bytes[:6])
    except Exception:
        return {}
        
    names: Dict[int, str] = {}
    
    for i in range(count):
        rec_offset = 6 + i * 12
        if rec_offset + 12 > len(name_bytes):
            break
        platform_id, encoding_id, language_id, name_id, length, offset = struct.unpack(
            '>HHHHHH', name_bytes[rec_offset:rec_offset + 12]
        )
        str_start = string_offset + offset
        str_end = str_start + length
        if str_end <= len(name_bytes):
            raw_str = name_bytes[str_start:str_end]
            val = None
            if platform_id == 3:  # Windows (always UTF-16BE)
                try:
                    val = raw_str.decode('utf-16-be')
                except Exception:
                    val = raw_str.decode('latin1', errors='replace')
            elif platform_id == 1:  # Macintosh (MacRoman)
                try:
                    val = raw_str.decode('mac_roman')
                except Exception:
                    val = raw_str.decode('latin1', errors='replace')
            elif platform_id == 0:  # Unicode (can be UTF-16BE or ASCII in legacy fonts)
                try:
                    val = raw_str.decode('utf-16-be')
                except Exception:
                    try:
                        val = raw_str.decode('mac_roman')
                    except Exception:
                        val = raw_str.decode('latin1', errors='replace')
            else:
                try:
                    val = raw_str.decode('utf-8')
                except Exception:
                    val = raw_str.decode('latin1', errors='replace')
            
            if val is not None:
                cleaned = val.strip().replace('\x00', '')
                if cleaned:
                    # Prefer Windows (3) or Unicode (0), then Mac (1)
                    if name_id not in names or platform_id == 3 or platform_id == 0:
                        names[name_id] = cleaned

    name_id_map = {
        0: "copyright",
        1: "family_name",
        2: "subfamily",
        3: "unique_id",
        4: "full_name",
        5: "version",
        6: "postscript_name",
        16: "typographic_family",
        17: "typographic_subfamily"
    }
    
    result = {}
    for nid, key in name_id_map.items():
        if nid in names:
            result[key] = names[nid]
            
    return result


class FontInfo:
    def __init__(self, file_path: str):
        self.file_path = os.path.abspath(file_path)
        self.file_name = os.path.basename(file_path)
        self.file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        self.is_valid = False
        self.error_message: Optional[str] = None
        self.format_type: str = "Unknown"
        self.tables: Dict[str, Dict[str, int]] = {}
        
        # OS/2 table data
        self.has_os2 = False
        self.os2_offset = 0
        self.os2_length = 0
        self.os2_version = 0
        self.current_fstype = 0
        self.decoded_fstype: Dict[str, Any] = {}
        
        # Name data
        self.family_name = os.path.splitext(self.file_name)[0]
        self.subfamily = "Regular"
        self.full_name = self.family_name
        self.font_version = ""
        self.postscript_name = ""
        self.typographic_family = ""
        self.typographic_subfamily = ""
        
        self._load()

    def _load(self):
        try:
            if not os.path.exists(self.file_path):
                self.error_message = "File does not exist."
                return

            with open(self.file_path, 'rb') as f:
                header = f.read(12)
                
            if len(header) < 12:
                fmt, msg = classify_file_format(self.file_path, header)
                self.format_type = fmt
                self.error_message = msg
                return

            sfnt_tag = header[:4]
            if sfnt_tag in (SFNT_TRUETYPE_1, SFNT_TRUETYPE_TRUE, SFNT_TRUETYPE_TYP1):
                self.format_type = "TrueType (TTF)"
            elif sfnt_tag == SFNT_OPENTYPE_CFF:
                self.format_type = "OpenType CFF (OTF)"
            elif sfnt_tag == SFNT_COLLECTION:
                self.format_type = "TrueType Collection (TTC)"
            else:
                fmt, msg = classify_file_format(self.file_path, header)
                self.format_type = fmt
                self.error_message = msg
                return

            with open(self.file_path, 'rb') as f:
                font_bytes = f.read()

            if sfnt_tag == SFNT_COLLECTION:
                self._load_ttc(font_bytes)
            else:
                self._load_sfnt(font_bytes, 0)

            if not self.error_message and self.has_os2:
                self.is_valid = True
            else:
                self.is_valid = False

        except Exception as e:
            self.error_message = f"Error reading font: {str(e)}"
            self.is_valid = False

    def _load_sfnt(self, data: bytes, base_offset: int):
        if base_offset + 12 > len(data):
            self.error_message = "SFNT header out of bounds."
            return
        num_tables = struct.unpack('>H', data[base_offset + 4:base_offset + 6])[0]
        if num_tables == 0:
            self.error_message = "Font contains 0 tables."
            return
        if base_offset + 12 + num_tables * 16 > len(data):
            self.error_message = "SFNT table directory is truncated."
            return
        self.tables = {}
        for i in range(num_tables):
            entry_offset = base_offset + 12 + i * 16
            tag = data[entry_offset:entry_offset + 4].decode('latin1', errors='replace')
            csum, toffset, length = struct.unpack('>III', data[entry_offset + 4:entry_offset + 16])
            self.tables[tag] = {
                'dir_entry_offset': entry_offset,
                'checksum': csum,
                'offset': toffset,
                'length': length
            }

        if 'OS/2' in self.tables:
            os2 = self.tables['OS/2']
            self.has_os2 = True
            self.os2_offset = os2['offset']
            self.os2_length = os2['length']
            
            if self.os2_length >= 10 and self.os2_offset + self.os2_length <= len(data):
                self.os2_version = struct.unpack('>H', data[self.os2_offset:self.os2_offset + 2])[0]
                self.current_fstype = struct.unpack('>H', data[self.os2_offset + 8:self.os2_offset + 10])[0]
                self.decoded_fstype = decode_fstype(self.current_fstype)
            else:
                self.error_message = "OS/2 table is truncated or out of bounds."
        else:
            self.error_message = "Font has no OS/2 table."

        if 'name' in self.tables:
            ntab = self.tables['name']
            if ntab['offset'] + ntab['length'] <= len(data):
                name_bytes = data[ntab['offset']:ntab['offset'] + ntab['length']]
                names = extract_names_from_table(name_bytes)
                self.family_name = names.get('family_name', self.family_name)
                self.subfamily = names.get('subfamily', self.subfamily)
                self.full_name = names.get('full_name', f"{self.family_name} {self.subfamily}".strip())
                self.font_version = names.get('version', '')
                self.postscript_name = names.get('postscript_name', '')
                self.typographic_family = names.get('typographic_family', '')
                self.typographic_subfamily = names.get('typographic_subfamily', '')

    def _load_ttc(self, data: bytes):
        if len(data) < 12:
            self.error_message = "Invalid TTC header."
            return
        num_fonts = struct.unpack('>I', data[8:12])[0]
        if num_fonts <= 0 or len(data) < 12 + num_fonts * 4:
            self.error_message = "Malformed TTC header or font offset table."
            return
        offsets = [struct.unpack('>I', data[12 + i * 4:16 + i * 4])[0] for i in range(num_fonts)]
        if offsets[0] + 12 > len(data):
            self.error_message = "First TTC font offset out of bounds."
            return
        self._load_sfnt(data, offsets[0])
        self.format_type = f"TrueType Collection ({num_fonts} fonts)"


def clear_readonly_attribute(path: str):
    """Clears Windows Read-Only file attribute if present."""
    if os.path.exists(path):
        try:
            os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
        except Exception:
            pass
        if os.name == 'nt':
            try:
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(str(path), 0x80)  # FILE_ATTRIBUTE_NORMAL
            except Exception:
                pass


def patch_font_fstype(
    input_path: str,
    target_fstype: int,
    output_path: Optional[str] = None,
    create_backup: bool = True
) -> Tuple[bool, str]:
    """
    Modifies OS/2 fsType in a TTF/OTF/TTC font file.
    Recalculates table checksum and head.checkSumAdjustment according to the OpenType specification.
    Safely handles Windows ReadOnly files, open shared read locks, and collections.
    """
    is_overwrite = (output_path is None or os.path.abspath(output_path) == os.path.abspath(input_path))
    dest_path = os.path.abspath(input_path if is_overwrite else output_path)

    # Pre-flight check: Is this an installed system font?
    p_lower = dest_path.lower().replace('\\', '/')
    is_system_font = (
        "windows/fonts" in p_lower or
        "microsoft/windows/fonts" in p_lower or
        "/system/library/fonts" in p_lower or
        "/library/fonts" in p_lower or
        "/usr/share/fonts" in p_lower or
        "/usr/local/share/fonts" in p_lower
    )

    if is_overwrite and is_system_font:
        return False, (
            "Cannot overwrite in-place: This font is installed in the operating system and actively locked by the system font cache. "
            "Please click 'Save As New Font...' or use 'Batch Apply' to export into a separate folder."
        )

    if not os.path.exists(input_path):
        return False, f"Source file does not exist: {input_path}"

    try:
        with open(input_path, 'rb') as f:
            data = bytearray(f.read())
    except Exception as e:
        return False, f"Could not read source font: {str(e)}"

    if len(data) < 12:
        return False, "File is too short to be a valid font."

    sfnt_tag = bytes(data[:4])
    is_ttc = (sfnt_tag == SFNT_COLLECTION)
    
    font_offsets = []
    if is_ttc:
        if len(data) < 12:
            return False, "Malformed TTC header."
        num_fonts = struct.unpack('>I', data[8:12])[0]
        if num_fonts <= 0 or len(data) < 12 + num_fonts * 4:
            return False, "Malformed TTC font offset table."
        font_offsets = [struct.unpack('>I', data[12 + i * 4:16 + i * 4])[0] for i in range(num_fonts)]
    elif sfnt_tag in (SFNT_TRUETYPE_1, SFNT_TRUETYPE_TRUE, SFNT_TRUETYPE_TYP1, SFNT_OPENTYPE_CFF):
        font_offsets = [0]
    else:
        return False, f"Unsupported font format (signature: {sfnt_tag.hex()})"

    # Parse and validate table directories for each font
    font_subtables = []
    for font_idx, base_offset in enumerate(font_offsets):
        if base_offset + 12 > len(data):
            return False, f"Font #{font_idx} SFNT header out of bounds."
        num_tables = struct.unpack('>H', data[base_offset + 4:base_offset + 6])[0]
        if num_tables == 0:
            return False, f"Font #{font_idx} contains 0 tables."
        if base_offset + 12 + num_tables * 16 > len(data):
            return False, f"Font #{font_idx} SFNT table directory is truncated."
        
        tables = {}
        for i in range(num_tables):
            entry_offset = base_offset + 12 + i * 16
            tag = bytes(data[entry_offset:entry_offset + 4])
            csum, toffset, length = struct.unpack('>III', data[entry_offset + 4:entry_offset + 16])
            tables[tag] = {
                'dir_offset': entry_offset,
                'checksum': csum,
                'offset': toffset,
                'length': length
            }
        font_subtables.append((base_offset, num_tables, tables))

    modified_any = False

    # Pass 1: Patch OS/2 tables and recalculate OS/2 table checksums
    for base_offset, num_tables, tables in font_subtables:
        if b'OS/2' not in tables:
            continue
        os2_entry = tables[b'OS/2']
        os2_off = os2_entry['offset']
        os2_len = os2_entry['length']
        if os2_len < 10 or os2_off + os2_len > len(data):
            return False, f"OS/2 table is truncated or out of bounds (offset: {os2_off}, len: {os2_len})."

        # Patch fsType (2 bytes, big-endian) at OS/2 + 8
        struct.pack_into('>H', data, os2_off + 8, target_fstype & 0xFFFF)
        modified_any = True

        # Recalculate OS/2 table checksum
        os2_bytes = bytes(data[os2_off:os2_off + os2_len])
        new_os2_csum = compute_table_checksum(os2_bytes)
        struct.pack_into('>I', data, os2_entry['dir_offset'] + 4, new_os2_csum)

    if not modified_any:
        return False, "No OS/2 table found to modify in font."

    # Pass 2: Recalculate head.checkSumAdjustment for each sub-font
    # According to the OpenType specification:
    # checkSumAdjustment = (0xB1B0AFBA - (sum(all_table_checksums) + dir_checksum)) & 0xFFFFFFFF
    for base_offset, num_tables, tables in font_subtables:
        if b'head' not in tables:
            continue
        head_entry = tables[b'head']
        head_off = head_entry['offset']
        head_len = head_entry['length']
        head_dir_off = head_entry['dir_offset']

        if head_len < 12 or head_off + head_len > len(data):
            return False, "head table is truncated or out of bounds."

        # A. Clear checkSumAdjustment in head table (offset 8)
        struct.pack_into('>I', data, head_off + 8, 0)

        # B. Compute head table checksum with checkSumAdjustment = 0
        head_bytes_zero = bytes(data[head_off:head_off + head_len])
        head_csum = compute_table_checksum(head_bytes_zero)
        struct.pack_into('>I', data, head_dir_off + 4, head_csum)

        # C. Compute directory checksum (OffsetTable + TableDirectory)
        dir_bytes = bytes(data[base_offset:base_offset + 12 + num_tables * 16])
        dir_csum = compute_table_checksum(dir_bytes)

        # D. Sum all table checksums from the updated directory
        table_csums = []
        for i in range(num_tables):
            entry_offset = base_offset + 12 + i * 16
            csum = struct.unpack('>I', data[entry_offset + 4:entry_offset + 8])[0]
            table_csums.append(csum)

        total_font_sum = (sum(table_csums) + dir_csum) & 0xFFFFFFFF
        adjustment = (0xB1B0AFBA - total_font_sum) & 0xFFFFFFFF
        struct.pack_into('>I', data, head_off + 8, adjustment)

    tmp_path = None
    try:
        dest_dir = os.path.dirname(dest_path)
        os.makedirs(dest_dir, exist_ok=True)
        clear_readonly_attribute(dest_path)

        # Temporary patch file with unique UUID token to guarantee race-free concurrency
        token = uuid.uuid4().hex[:8]
        tmp_path = dest_path + f".tmp_{os.getpid()}_{token}"
        clear_readonly_attribute(tmp_path)
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

        # Write modified font bytes to temp file first
        with open(tmp_path, 'wb') as f:
            f.write(data)

        backup_created = False
        backup_path = dest_path + ".bak"

        if is_overwrite:
            # Overwrite in-place: use atomic rename-swap to bypass Windows open read locks (e.g. InDesign / DirectWrite)
            if os.path.exists(backup_path):
                clear_readonly_attribute(backup_path)
                try:
                    os.remove(backup_path)
                except Exception:
                    pass

            if create_backup:
                # Rename current file directly to .bak (succeeds even if locked for reading by InDesign)
                os.rename(dest_path, backup_path)
                backup_created = True
                try:
                    os.rename(tmp_path, dest_path)
                except Exception:
                    # Rollback: restore backup_path to dest_path
                    if os.path.exists(backup_path) and not os.path.exists(dest_path):
                        try:
                            os.rename(backup_path, dest_path)
                        except Exception:
                            pass
                    raise
            else:
                old_trash = dest_path + f".old_{os.getpid()}_{token}"
                if os.path.exists(old_trash):
                    clear_readonly_attribute(old_trash)
                    try:
                        os.remove(old_trash)
                    except Exception:
                        pass
                os.rename(dest_path, old_trash)
                try:
                    os.rename(tmp_path, dest_path)
                except Exception:
                    # Rollback
                    if os.path.exists(old_trash) and not os.path.exists(dest_path):
                        try:
                            os.rename(old_trash, dest_path)
                        except Exception:
                            pass
                    raise
                try:
                    clear_readonly_attribute(old_trash)
                    os.remove(old_trash)
                except Exception:
                    pass
        else:
            # Save as new font
            if os.path.exists(dest_path):
                clear_readonly_attribute(dest_path)
                try:
                    os.remove(dest_path)
                except Exception:
                    pass
            os.rename(tmp_path, dest_path)

        action_str = f"Successfully overwritten in-place" if is_overwrite else f"Saved as new font: {dest_path}"
        if is_overwrite and backup_created:
            action_str += f" (Backup created: {os.path.basename(backup_path)})"
        
        return True, action_str

    except PermissionError:
        if is_system_font:
            return False, "Windows locked this installed font in the system fonts folder. Please use 'Save As New Font' or export to a folder."
        return False, f"Permission Denied: File is locked by an external program or Read-Only ({dest_path})"
    except Exception as e:
        return False, f"Failed to write font: {str(e)}"
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                clear_readonly_attribute(tmp_path)
                os.remove(tmp_path)
            except Exception:
                pass
