"""
PersonaLock Wellness — App Icon Generator
Creates a 1024x1024 PNG with teal-to-purple gradient + white lock icon.
Uses only Python built-ins (struct, zlib, math, os). No Pillow needed.
"""
import struct, zlib, math, os

W, H = 1024, 1024

# PersonaLock brand colors
TEAL   = (0, 188, 212)    # #00BCD4
PURPLE = (123, 31, 162)   # #7B1FA2

# ── Lock geometry ─────────────────────────────────────────────────────────────
# Shackle (U-shape made of rectangles)
SH_LEFT_X1,  SH_LEFT_X2  = 382, 452   # left arm x-range
SH_RIGHT_X1, SH_RIGHT_X2 = 572, 642   # right arm x-range
SH_Y1      = 252                        # top of shackle
SH_TOP_Y2  = 322                        # bottom of top bar (70 px tall)
SH_Y2      = 492                        # bottom of arms (enters body)

# Lock body (rectangle)
BODY_X1, BODY_X2 = 292, 732
BODY_Y1, BODY_Y2 = 472, 762

# Keyhole (circle + rect below)
KH_CX, KH_CY, KH_R  = 512, 580, 54
KH_RECT_X1, KH_RECT_X2 = 494, 530
KH_RECT_Y1, KH_RECT_Y2 = 622, 715
# ─────────────────────────────────────────────────────────────────────────────

WHITE3 = b'\xff\xff\xff'

os.makedirs('personalock_wellness/assets/icons', exist_ok=True)
print("Generating PersonaLock icon (1024x1024) — pure Python PNG...")

rows = []
for y in range(H):
    t = y / (H - 1)
    br = round(TEAL[0] + (PURPLE[0] - TEAL[0]) * t)
    bg = round(TEAL[1] + (PURPLE[1] - TEAL[1]) * t)
    bb = round(TEAL[2] + (PURPLE[2] - TEAL[2]) * t)
    bg_px = bytes([br, bg, bb])

    # Start with background row (filter byte 0 = no filter, then W RGB pixels)
    row = bytearray(b'\x00' + bg_px * W)

    # ── Draw white lock regions via fast slice assignment ──────────────────────
    if SH_Y1 <= y <= SH_Y2:
        if y <= SH_TOP_Y2:
            # Top bar spans full shackle width
            s = 1 + SH_LEFT_X1 * 3
            e = 1 + (SH_RIGHT_X2 + 1) * 3
            row[s:e] = WHITE3 * (SH_RIGHT_X2 - SH_LEFT_X1 + 1)
        else:
            # Left arm
            s = 1 + SH_LEFT_X1 * 3
            e = 1 + (SH_LEFT_X2 + 1) * 3
            row[s:e] = WHITE3 * (SH_LEFT_X2 - SH_LEFT_X1 + 1)
            # Right arm
            s = 1 + SH_RIGHT_X1 * 3
            e = 1 + (SH_RIGHT_X2 + 1) * 3
            row[s:e] = WHITE3 * (SH_RIGHT_X2 - SH_RIGHT_X1 + 1)

    if BODY_Y1 <= y <= BODY_Y2:
        s = 1 + BODY_X1 * 3
        e = 1 + (BODY_X2 + 1) * 3
        row[s:e] = WHITE3 * (BODY_X2 - BODY_X1 + 1)

    # ── Punch keyhole (restore background color) ───────────────────────────────
    kh_x1 = kh_x2 = None
    dy = y - KH_CY
    if abs(dy) <= KH_R:
        dx = int(math.sqrt(KH_R * KH_R - dy * dy))
        kh_x1 = KH_CX - dx
        kh_x2 = KH_CX + dx
    elif KH_RECT_Y1 <= y <= KH_RECT_Y2:
        kh_x1 = KH_RECT_X1
        kh_x2 = KH_RECT_X2

    if kh_x1 is not None:
        s = 1 + kh_x1 * 3
        e = 1 + (kh_x2 + 1) * 3
        row[s:e] = bg_px * (kh_x2 - kh_x1 + 1)

    rows.append(bytes(row))

print("Joining rows and compressing...")
raw        = b''.join(rows)
compressed = zlib.compress(raw, 6)

def png_chunk(name: bytes, data: bytes) -> bytes:
    payload = name + data
    return (struct.pack('>I', len(data))
            + payload
            + struct.pack('>I', zlib.crc32(payload) & 0xFFFFFFFF))

out = 'personalock_wellness/assets/icons/app_icon.png'
with open(out, 'wb') as f:
    f.write(b'\x89PNG\r\n\x1a\n')
    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    f.write(png_chunk(b'IHDR', ihdr))
    f.write(png_chunk(b'IDAT', compressed))
    f.write(png_chunk(b'IEND', b''))

sz = os.path.getsize(out)
print(f"Done! {out}  ({sz:,} bytes)")
print("Icon design: teal-to-purple gradient background, white lock + keyhole, 1024x1024 RGB PNG")
