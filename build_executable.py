import os
import shutil
import sys
import subprocess

def create_exe(source_script):
    # Create the executable using PyInstaller
    subprocess.call(['pyinstaller', '--onefile', source_script])
    
def install_pyinstaller():
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    except subprocess.CalledProcessError as e:
        print(f"Failed to install pyinstaller: {e}")
        sys.exit(1)

def move_exe_to_desktop(exe_name):
    # # Determine the desktop path
    # desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    # if not os.path.exists(desktop_path):
    #     print(f"Desktop path does not exist: {desktop_path}")
    #     return
    # # Determine the path of the generated executable
    # dist_path = os.path.join('dist', exe_name)
    # # Move the executable to the desktop
    # shutil.move(dist_path, desktop_path)
    # print(f"{exe_name} has been moved to your Desktop.")
    return True

if __name__ == "__main__":

    install_pyinstaller()
    
    source_script = 'ViralShare.py'
    exe_name = os.path.splitext(os.path.basename(source_script))[0] + '.exe'
    
    create_exe(source_script)
    move_exe_to_desktop(exe_name)
