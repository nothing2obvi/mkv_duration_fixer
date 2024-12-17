# mkv_duration_fixer
A simple script to resolve incorrect MKV file durations caused by MKVToolNix when embedding subtitles. Skips already-processed files, supports dry-run mode, and is highly configurable. Made for personal use — feel free to fork and adapt!

# MKV Duration Fixer

**MKV Duration Fixer** is a lightweight Python script to resolve a very specific issue where MKV files show incorrect durations (double or even triple the actual length) after embedding subtitles using MKVToolNix. This script identifies affected files, fixes the durations, and skips files it has already processed for efficiency.

I’m not a coder, but I encountered this issue and thought I'd share this solution in case it’s useful for anyone else. ChatGPT helped me put this together, so feel free to fork and tweak it as needed.

---

## 🎯 **Who This Is For**  
- Users who frequently use MKVToolNix for embedding subtitles into `.mkv` files.  
- Those experiencing **incorrect general durations** in MKV files (e.g., a video says it's 4 hours when it's actually 2 hours).  
- People looking for an automated way to clean up their MKV library.  

---

## 🛠️ **The Problem**  
When subtitles are embedded using MKVToolNix, the *general duration* metadata in some `.mkv` files may become inaccurate - sometimes showing **double or triple the actual length of the video file**. This can cause problems for media servers (e.g. Jellyfin displays the double-length duration; when ErsatzTV plays past the *actual* video's duration, it's just a black screen).

This script automates the process of identifying and fixing such files without manual intervention. It uses `mkvmerge` to reprocess the affected files and correct the duration.

---

## ⚠️ **Disclaimer**  
- I’m not a programmer; this was made with ChatGPT's help.  
- It fixes a very specific issue that I faced. If you find it helpful, great!  
- **Feel free to fork it** and tweak it to suit your needs.  
- Use at your own risk. I am not responsible for any issues, such as data loss or unintended changes. Always back up your media beforehand — this is a best practice for any automated batch processing. Test it with a small sample of MKV files first. — I have successfully used it on **over 1,000 files**.

---

## 🖥️ **Features**  
1. **Fixes Incorrect Durations**: Reprocesses MKV files to correct inaccurate general durations.  
2. **Skips Already-Processed Files**: Prevents redundant work by logging processed files.  
3. **Dry-Run Mode**: See what changes would be made without modifying files.  
4. **Highly Configurable**: Customize directories, logs, and preferences easily.  

---

## 🚀 **Installation**

### **Dependencies**  
Ensure the following are installed:  
1. **MKVToolNix** (includes `mkvmerge`)  
   - Installation guide: [MKVToolNix Downloads](https://mkvtoolnix.download/)  
2. Python 3.x  

Install the required Python libraries:  
```bash
pip install tqdm
```

## 🛠️ **Configuration**
Edit the script’s configuration section at the top:

```python
DRY_RUN = True  # Set to False to enable full-run mode
INPUT_DIRECTORY = "/path/to/your/files"  # Directory containing MKV files
LOG_DIRECTORY = "/path/to/your/logs"  # Directory for log files
PROCESSED_LOG = "processed_files.log"  # File to track processed MKVs
RENDERED_DIRECTORY = "/path/to/rendered files" # Where the rendered files should go; if you want them to overwrite the originals, just put "None" (without quotes)
```

## 📄 **Usage**
1. Dry-Run Mode (Preview Changes)
By default, the script runs in dry-run mode to show what it would do without modifying files.

Run the script:

```bash
python mkv_duration_fixer.py
```

Example Output (Dry-Run):

```yaml
Starting MKV Duration Fixer in DRY-RUN mode.
Processing Files: 10%|██         | 1/10 [00:01<00:09,  1.00s/file]
Dry-run: Would execute: mkvmerge -o /path/to/temp_fixed.mkv /path/to/file.mkv
Processing complete: Files that would be adjusted: 3, Files skipped: 7
```

2. Full-Run Mode (Make Changes)
To enable full-run mode, set `DRY_RUN = False` in the script:

```python
DRY_RUN = False
```
Then run the script:

```bash
python mkv_duration_fixer.py
```

Example Output (Full-Run):

```bash
File: /path/to/file/with/wrong/duration.mkv
  General Duration: 6611s
  Video Duration: 3367s
  Discrepancy: 3244s
  Discrepancy exceeds threshold of 300s.
```

Then ffmpeg would fix the duration of the file.

## 📂 **Logs**
`mkv_optimizer.log`: Records all operations and errors.
`processed_files.log`: Keeps track of files that have already been fixed.

## 🚀 **Take It a Step Further**
To ensure your MKV library always has accurate durations, consider running this script as a cron job (Linux/macOS):

```bash
0 2 * * * /usr/bin/python3 /path/to/mkv_duration_fixer.py
```

## 💬 **Let Me Know What You Think**
I created this script for my own use to solve a frustrating problem. It's not perfect. I may look at issues or feature requests if time allows and if ChatGPT cooperates with me.

If you find this script useful or have ideas for improvements, let me know! Feel free to fork the project and make it even better.
