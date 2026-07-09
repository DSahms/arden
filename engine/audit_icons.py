import os, hashlib

files = [
    'personalock_wellness/android/app/src/main/res/mipmap-hdpi/ic_launcher.png',
    'personalock_wellness/android/app/src/main/res/mipmap-mdpi/ic_launcher.png',
    'personalock_wellness/android/app/src/main/res/mipmap-xhdpi/ic_launcher.png',
    'personalock_wellness/android/app/src/main/res/mipmap-xxhdpi/ic_launcher.png',
    'personalock_wellness/android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png',
]

# Known MD5s for default Flutter "F" launcher icons (stock template)
# These are the standard sizes from the Flutter create template
DEFAULT_FLUTTER_MD5S = {
    # These vary by Flutter SDK version so we check size patterns instead
}

print("=== ANDROID MIPMAP ICONS ===")
for f in files:
    if os.path.exists(f):
        sz = os.path.getsize(f)
        with open(f, 'rb') as fh:
            data = fh.read()
            md5 = hashlib.md5(data).hexdigest()
        # Default Flutter F icons are typically very small (< 5KB for most densities)
        print(f'FOUND: {f}')
        print(f'  size={sz} bytes  md5={md5}')
    else:
        print(f'MISSING: {f}')

print()
print("=== iOS APPICON ===")
ios_dir = 'personalock_wellness/ios/Runner/Assets.xcassets/AppIcon.appiconset'
if os.path.exists(ios_dir):
    print(f'FOUND: {ios_dir}')
    for fn in sorted(os.listdir(ios_dir)):
        fp = os.path.join(ios_dir, fn)
        sz = os.path.getsize(fp)
        print(f'  {fn}  {sz} bytes')
else:
    print(f'MISSING: {ios_dir}')

print()
print("=== assets/icons DIRECTORY ===")
icons_dir = 'personalock_wellness/assets/icons'
if os.path.exists(icons_dir):
    print(f'FOUND: {icons_dir}')
    for fn in os.listdir(icons_dir):
        fp = os.path.join(icons_dir, fn)
        print(f'  {fn}  {os.path.getsize(fp)} bytes')
else:
    print(f'MISSING: {icons_dir}')
