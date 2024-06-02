# Welcome to ViralShare!

ViralShare is a lightweight peer-to-peer file sharing application designed to facilitate easy and secure sharing of files among users on a network. With ViralShare, you can quickly set up your own file sharing server, connect to other peers, share your files, and download files shared by others.

## Getting Started

To start using ViralShare, follow these simple steps:

### 1. Create the Executable

- Make sure you have Python installed on your system. You can download it from the official Python website.

- Open a terminal or command prompt.

- Download the `ViralShare.py` and `build_executable.py` scripts to your local machine.

- Run the following command to create the executable:
   ```python build_executable.py```

- This will install executable file `ViralShare.exe` in `dict` folder, and copy and paste it to your desired location.

### 2. Installing and Running ViralShare

- Once the download is complete, locate the downloaded ViralShare.exe file on your computer.
- Double-click on the ViralShare.exe file to launch the application.
- A terminal window will also open along with file sharing interface, displaying all information and error logging that happens live while running application.
- Two logging files, `access.log` and `error.log`, will be created at the same level as the application file.

### 3. Setting Up Your Server

- Upon launching ViralShare, you will be prompted to set up your server. Enter a port number and a password for your server. This will allow other users to connect to your server and share files.
- Click on the "Start Server" button to initiate your server.

### 4. Connecting to Other Peers

- To connect to other peers, you'll need their server information, including their host address, port number, and password.
- Enter the host address, port number, and password of the peer you want to connect to in the provided fields.
- Click on the "Connect to Peer" button to establish a connection with the peer.

### 5. Sharing Your Files

- ViralShare allows you to share files from a specific folder on your computer.
- All files that need to be shared must be in the folder `share` on the same level as the application file, which will be automatically build when you start the server.
- Click on the "List Files" button to view the files available for sharing from your designated share folder.

### 6. Downloading Files from Peers

- To download files shared by other connected peers, click on the "List All Files" button.
- This will display a list of files shared by other peers connected to your server.
- Enter the filename you want to download in the download box and hit the download button.
- The downloaded file will be stored in the `download` folder on the same level as the application file, which will be automatically build when you start the server.

## Additional Features

- **Password Protection:** ViralShare ensures that only authorized users can access and use the application. The application cannot be modified or distributed without explicit permission from the owner.
- **License:** Users are granted the right to use ViralShare for personal use only. Any modifications or distributions require prior approval from the owner.
- **Contributors:** This application was developed by:
  - [Biyawala Viral Deven](https://github.com/ViralBiyawala)
  - [Shivam Sikotra](https://github.com/ShivamSikotra11)
  - [Patel Shyam](https://github.com/shyam2024)

## For contributions, please contact [Biyawala Viral Deven](https://github.com/ViralBiyawala).

That's it! You're now ready to use ViralShare to share and download files securely with other users on your network. If you encounter any issues or have feedback, feel free to reach out to the owner for support.
