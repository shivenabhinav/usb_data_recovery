# Data Recovery Toolkit

A powerful and user-friendly data recovery tool designed to recover deleted files from USB drives and hard disks. Built with Python and PyQt5, this tool provides an intuitive graphical interface for file recovery operations.

## 🚀 Features

- 📁 Recover deleted files from USB drives and hard disks
- 🔍 Deep scanning capability for thorough recovery
- 📊 Real-time progress tracking
- 📝 Detailed recovery logging
- 🎯 Selective file type recovery
- 💻 User-friendly GUI interface

## 📋 Supported File Types

### Documents
- Microsoft Office (DOC, DOCX, XLS, XLSX, PPT, PPTX)
- PDF Documents
- Text Files (TXT, RTF)

### Media Files
- Images (JPG, JPEG, PNG, GIF, BMP)
- Videos (MP4, AVI, MOV, WMV)
- Audio (MP3, WAV, WMA)

### Archives
- ZIP
- RAR
- 7Z

## ⚙️ Requirements

- Windows Operating System
- Python 3.7 or higher
- Administrator privileges
- Minimum 4GB RAM
- Available disk space for recovered files

## 📥 Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/data-recovery-toolkit.git
   cd data-recovery-toolkit
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   ```

3. **Activate Virtual Environment**
   ```bash
   # Windows
   .\venv\Scripts\activate
   ```

4. **Install Dependencies**
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

## 🚦 Usage

1. **Launch the Application**
   ```bash
   python data_recovery_toolkit.py
   ```

2. **Recovery Steps**
   - Select the drive to scan
   - Choose file types to recover
   - Select destination folder for recovered files
   - Choose scan type (Quick/Deep)
   - Click "Start Recovery"

## 💡 Tips for Best Results

1. **Stop Using the Drive**
   - Immediately stop using the drive when data loss occurs
   - Don't save new files to the drive

2. **Choose Appropriate Scan**
   - Quick Scan: For recently deleted files
   - Deep Scan: For formatted drives or older deletions

3. **Save Location**
   - Always save recovered files to a different drive
   - Ensure enough free space at destination

## ⚠️ Important Notes

- Run as administrator for full functionality
- Deep scanning may take several hours for large drives
- Recovery success depends on drive condition
- Recovered files are saved with timestamp prefixes

## 🔍 Troubleshooting

### Common Issues and Solutions

1. **Installation Errors**
   ```bash
   # Alternative installation method
   python -m pip install --trusted-host pypi.org --trusted-host files.pythonproject.org -r requirements.txt
   ```

2. **Access Denied**
   - Run as administrator
   - Check drive permissions

3. **Slow Scanning**
   - Normal for deep scans
   - Consider using quick scan first

## 📝 Logging

- Logs are saved in `recovery.log`
- Contains detailed operation information
- Useful for troubleshooting

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚖️ Disclaimer

This tool is provided "as is" without warranty of any kind. Use at your own risk. The authors are not responsible for any data loss or damage.

## 👥 Support

For issues and feature requests:
- Create an issue on GitHub
- Email: shivenabhinav29@gmail.com

## 🙏 Acknowledgments

- PyQt5 team for the GUI framework
- Python community for various libraries
- All contributors and testers

---
Made with ❤️ by [ M.Shiven Abhinav Reddy ]
