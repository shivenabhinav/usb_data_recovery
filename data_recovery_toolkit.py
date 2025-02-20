import os
import sys
import time
import shutil
import struct
import logging
from pathlib import Path
import win32api
import win32file
import win32con
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc

# Set up logging
logging.basicConfig(
    filename='recovery.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class FileSignatures:
    """File signatures (magic numbers) for different file types"""
    SIGNATURES = {
        # Documents
        '.pdf': b'%PDF',
        '.doc': b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1',
        '.docx': b'PK\x03\x04',
        
        # Images
        '.jpg': b'\xFF\xD8\xFF',
        '.png': b'\x89PNG\r\n\x1A\n',
        '.gif': b'GIF8',
        
        # Audio/Video
        '.mp3': b'ID3',
        '.mp4': b'ftyp',
        
        # Archives
        '.zip': b'PK\x03\x04',
        '.rar': b'Rar!\x1A\x07'
    }

class DataRecoveryToolkit(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Data Recovery Toolkit')
        self.setGeometry(100, 100, 800, 600)
        
        # Main widget and layout
        main_widget = qtw.QWidget()
        self.setCentralWidget(main_widget)
        layout = qtw.QVBoxLayout(main_widget)
        
        # Drive selection
        drive_group = qtw.QGroupBox("Select Drive")
        drive_layout = qtw.QHBoxLayout()
        self.drive_combo = qtw.QComboBox()
        self.refresh_btn = qtw.QPushButton("Refresh Drives")
        drive_layout.addWidget(self.drive_combo)
        drive_layout.addWidget(self.refresh_btn)
        drive_group.setLayout(drive_layout)
        
        # File types selection
        filetype_group = qtw.QGroupBox("File Types to Recover")
        filetype_layout = qtw.QVBoxLayout()
        self.file_types = {
            "Documents": [".doc", ".docx", ".pdf", ".txt", ".rtf", ".xls", ".xlsx", ".ppt", ".pptx"],
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
            "Videos": [".mp4", ".avi", ".mov", ".wmv"],
            "Audio": [".mp3", ".wav", ".wma"],
            "Archives": [".zip", ".rar", ".7z"]
        }
        
        self.filetype_checks = {}
        for category, extensions in self.file_types.items():
            checkbox = qtw.QCheckBox(f"{category} ({', '.join(extensions)})")
            self.filetype_checks[category] = checkbox
            filetype_layout.addWidget(checkbox)
        
        filetype_group.setLayout(filetype_layout)
        
        # Recovery options
        recovery_group = qtw.QGroupBox("Recovery Options")
        recovery_layout = qtw.QVBoxLayout()
        self.deep_scan = qtw.QCheckBox("Deep Scan (Takes longer but more thorough)")
        self.save_location_btn = qtw.QPushButton("Select Save Location")
        self.save_location_label = qtw.QLabel("Save Location: Not Selected")
        recovery_layout.addWidget(self.deep_scan)
        recovery_layout.addWidget(self.save_location_btn)
        recovery_layout.addWidget(self.save_location_label)
        recovery_group.setLayout(recovery_layout)
        
        # Progress area
        self.progress_bar = qtw.QProgressBar()
        self.status_label = qtw.QLabel("Ready")
        
        # Start button
        self.start_btn = qtw.QPushButton("Start Recovery")
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        
        # Add all components to main layout
        layout.addWidget(drive_group)
        layout.addWidget(filetype_group)
        layout.addWidget(recovery_group)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addWidget(self.start_btn)
        
        # Connect signals
        self.refresh_btn.clicked.connect(self.refresh_drives)
        self.save_location_btn.clicked.connect(self.select_save_location)
        self.start_btn.clicked.connect(self.start_recovery)
        
        # Initialize drives
        self.refresh_drives()
        
        self.save_location = None
        
    def refresh_drives(self):
        """Refresh the list of available drives"""
        self.drive_combo.clear()
        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]
        for drive in drives:
            self.drive_combo.addItem(drive)
    
    def select_save_location(self):
        """Open dialog to select save location"""
        self.save_location = qtw.QFileDialog.getExistingDirectory(
            self, "Select Save Location"
        )
        if self.save_location:
            self.save_location_label.setText(f"Save Location: {self.save_location}")
    
    def start_recovery(self):
        """Start the recovery process"""
        if not self.save_location:
            qtw.QMessageBox.warning(self, "Error", "Please select a save location first!")
            return
            
        selected_drive = self.drive_combo.currentText()
        selected_types = []
        for category, checkbox in self.filetype_checks.items():
            if checkbox.isChecked():
                selected_types.extend(self.file_types[category])
        
        if not selected_types:
            qtw.QMessageBox.warning(self, "Error", "Please select at least one file type!")
            return
            
        self.status_label.setText("Recovery in progress...")
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Start recovery in a separate thread
        self.recovery_thread = RecoveryThread(
            selected_drive,
            selected_types,
            self.save_location,
            self.deep_scan.isChecked()
        )
        self.recovery_thread.progress_update.connect(self.update_progress)
        self.recovery_thread.finished.connect(self.recovery_finished)
        self.recovery_thread.start()
        
    def update_progress(self, value, max_value, message):
        """Update progress bar and status message"""
        self.progress_bar.setRange(0, max_value)
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
        
    def recovery_finished(self):
        """Handle recovery completion"""
        self.status_label.setText("Recovery completed!")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        qtw.QMessageBox.information(self, "Complete", "File recovery process has finished!")

class RecoveryThread(qtc.QThread):
    progress_update = qtc.pyqtSignal(int, int, str)
    
    def __init__(self, drive, file_types, save_location, deep_scan):
        super().__init__()
        self.drive = drive
        self.file_types = file_types
        self.save_location = save_location
        self.deep_scan = deep_scan
        self.recovered_files = 0
        self.BUFFER_SIZE = 64 * 1024  # 64KB buffer
    
    def run(self):
        """Run the recovery process"""
        try:
            logging.info(f"Starting recovery process on drive {self.drive}")
            
            # Create recovery directory
            recovery_dir = os.path.join(self.save_location, f"recovered_files_{int(time.time())}")
            os.makedirs(recovery_dir, exist_ok=True)
            
            # Basic file system scan
            self.scan_filesystem(recovery_dir)
            
            if self.deep_scan:
                # Raw disk scan
                self.scan_raw_disk(recovery_dir)
                
            logging.info(f"Recovery completed. {self.recovered_files} files recovered")
            self.progress_update.emit(100, 100, f"Recovery completed! Found {self.recovered_files} files")
                
        except Exception as e:
            logging.error(f"Error during recovery: {str(e)}")
            self.progress_update.emit(0, 100, f"Error: {str(e)}")
    
    def scan_filesystem(self, recovery_dir):
        """Scan the file system for deleted files"""
        try:
            drive_path = self.drive.rstrip('\\')
            
            # Get volume information
            volume_name = win32file.GetVolumeNameForVolumeMountPoint(drive_path + '\\')
            
            # Open volume handle
            handle = win32file.CreateFile(
                volume_name,
                win32con.GENERIC_READ,
                win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
                None,
                win32con.OPEN_EXISTING,
                0,
                None
            )
            
            self.progress_update.emit(0, 100, "Scanning filesystem...")
            
            # Scan for deleted files
            for root, dirs, files in os.walk(drive_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    if file_ext in self.file_types:
                        try:
                            self._recover_file(file_path, recovery_dir)
                        except Exception as e:
                            logging.warning(f"Could not recover {file_path}: {str(e)}")
            
            win32file.CloseHandle(handle)
            
        except Exception as e:
            logging.error(f"Filesystem scan error: {str(e)}")
            raise
    
    def scan_raw_disk(self, recovery_dir):
        """Perform raw disk scan for file signatures"""
        try:
            self.progress_update.emit(0, 100, "Performing deep scan...")
            
            # Open physical drive
            drive_path = f"\\\\.\\{self.drive[0]}:"
            handle = win32file.CreateFile(
                drive_path,
                win32con.GENERIC_READ,
                win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
                None,
                win32con.OPEN_EXISTING,
                0,
                None
            )
            
            # Get drive size
            drive_size = win32file.GetFileSizeEx(handle)
            
            # Read drive in chunks
            offset = 0
            while offset < drive_size:
                try:
                    # Seek to position
                    win32file.SetFilePointer(handle, offset, 0, win32con.FILE_BEGIN)
                    
                    # Read buffer
                    error, data = win32file.ReadFile(handle, self.BUFFER_SIZE)
                    
                    # Check for file signatures
                    self._check_signatures(data, offset, recovery_dir)
                    
                    # Update progress
                    progress = int((offset / drive_size) * 100)
                    self.progress_update.emit(progress, 100, f"Deep scanning: {progress}%")
                    
                    offset += self.BUFFER_SIZE
                    
                except Exception as e:
                    logging.warning(f"Error reading at offset {offset}: {str(e)}")
                    offset += self.BUFFER_SIZE
                    continue
            
            win32file.CloseHandle(handle)
            
        except Exception as e:
            logging.error(f"Raw disk scan error: {str(e)}")
            raise
    
    def _recover_file(self, file_path, recovery_dir):
        """Attempt to recover a single file"""
        try:
            file_name = os.path.basename(file_path)
            recovery_path = os.path.join(recovery_dir, f"recovered_{file_name}")
            
            # Try to copy the file
            shutil.copy2(file_path, recovery_path)
            
            self.recovered_files += 1
            logging.info(f"Recovered file: {file_path}")
            
        except Exception as e:
            logging.warning(f"Failed to recover {file_path}: {str(e)}")
    
    def _check_signatures(self, data, offset, recovery_dir):
        """Check for file signatures in data block"""
        for ext, signature in FileSignatures.SIGNATURES.items():
            if ext in self.file_types and data.startswith(signature):
                # Found a file signature
                try:
                    recovery_path = os.path.join(
                        recovery_dir,
                        f"recovered_file_{offset}_{int(time.time())}{ext}"
                    )
                    
                    with open(recovery_path, 'wb') as f:
                        f.write(data)
                    
                    self.recovered_files += 1
                    logging.info(f"Recovered file from offset {offset}")
                    
                except Exception as e:
                    logging.warning(f"Failed to recover file at offset {offset}: {str(e)}")

def main():
    app = qtw.QApplication(sys.argv)
    window = DataRecoveryToolkit()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 