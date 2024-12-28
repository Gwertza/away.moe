# away.moe

**away.moe** is a simple web application that lets you upload files and text and share them using unique IDs. Files are accessible for a limited time based on expiration settings, ensuring secure and temporary sharing.

## Features

- **Upload Files or Text**: Upload any file or text to a unique ID.
- **Share via Unique ID**: Share the unique ID to allow others to access the uploaded content.
- **Temporary Access**: Content expires based on user-defined settings (e.g., 1 minute, 1 day, or after viewing).
- **Drag-and-Drop Upload**: Drag and drop your files directly into the upload box.

---

## How to Use

### 1. Upload Content
- Enter the unique ID of your choice or let the system generate one for you.
- Add text, select a file to upload, and specify an expiration time (e.g., delete after 1 minute or upon first viewing).
- Drag and drop files directly into the upload area or click to open the file picker.

### 2. Share the Unique ID
- Share the unique ID with others or save it for yourself for later access.

### 3. Access Uploaded Content
- Enter the unique ID on the website to check for uploaded content.
- If the ID contains an image, it will display as a preview. Otherwise, the file can be downloaded.
- Once the expiration time is reached or the file is viewed/downloaded, it is deleted automatically.

---

## Technical Details

### Frontend
- **React**: Built with React for an interactive user experience.
- **Drag-and-Drop File Upload**: Smooth and user-friendly interface for file uploads.
- **Dynamic Progress Bars**: Displays upload and download progress in real-time.

### Backend
- **Flask**: Backend server for handling uploads, downloads, and API requests.
- **SQLite3**: Database storing file and text data

