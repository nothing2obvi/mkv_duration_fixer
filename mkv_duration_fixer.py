import os
import subprocess
import shutil
from datetime import datetime

# Configurable paths and dry-run toggle
DRY_RUN = True  # Set to False to apply changes
INPUT_FILE_PATH = "/path/to/your/files"
OUTPUT_FILE_PATH = "/path/to/your/logs"  # Directory where logs go
LOG_FILE = os.path.join(OUTPUT_FILE_PATH, "duration_fix.log")  # Define the name of the log file
DISCREPANCY_THRESHOLD = 300  # 5 minutes in seconds
RENDERED_DIRECTORY = None  # Define rendered file output directory, or set to None for overwriting

# Ensure the logs directory exists
os.makedirs(OUTPUT_FILE_PATH, exist_ok=True)

# Create rendered directory if it doesn't exist
os.makedirs(RENDERED_DIRECTORY, exist_ok=True) if RENDERED_DIRECTORY else None

# Define a function to log messages
def log(message):
	with open(LOG_FILE, "a") as log_file:
		log_file.write(f"{datetime.now()}: {message}\n")
	print(message)

# Read the list of already processed files from the log
def get_logged_files():
	if not os.path.exists(LOG_FILE):
		return {}
	
	logged_files = {}
	with open(LOG_FILE, "r") as log_file:
		for line in log_file:
			try:
				if "STATUS:" in line and "FILE:" in line:
					parts = line.strip().split(" | ")
					file_path = parts[1].replace("FILE:", "").strip()
					status = parts[2].replace("STATUS:", "").strip()
					logged_files[file_path] = status
			except IndexError:
				log(f"Warning: Malformed log entry skipped: {line.strip()}")
	return logged_files

# Function to get duration information
def get_durations(file_path):
	try:
		result = subprocess.run(
			["mediainfo", "--Inform=General;%Duration%", file_path],
			capture_output=True,
			text=True,
			check=True
		)
		general_duration = int(float(result.stdout.strip()) / 1000)  # Convert from ms to seconds

		result = subprocess.run(
			["mediainfo", "--Inform=Video;%Duration%", file_path],
			capture_output=True,
			text=True,
			check=True
		)
		video_duration = int(float(result.stdout.strip()) / 1000)  # Convert from ms to seconds

		return general_duration, video_duration
	except Exception as e:
		log(f"Error extracting durations from {file_path}: {e}")
		return None, None

# Function to process a file
def process_file(file_path, logged_files):
	# Skip files that have already been processed (not dry-run)
	if file_path in logged_files and logged_files[file_path] == "adjusted":
		log(f"Skipping file already processed: {file_path} | STATUS: adjusted")
		return False

	general_duration, video_duration = get_durations(file_path)

	if general_duration is None or video_duration is None:
		log(f"Skipping file {file_path} due to missing duration data. | STATUS: error")
		return False

	discrepancy = abs(general_duration - video_duration)
	log(f"File: {file_path}")
	log(f"  General Duration: {general_duration}s")
	log(f"  Video Duration: {video_duration}s")
	log(f"  Discrepancy: {discrepancy}s")

	if discrepancy > DISCREPANCY_THRESHOLD:
		log(f"  Discrepancy exceeds threshold of {DISCREPANCY_THRESHOLD}s.")
		if DRY_RUN:
			log(f"  Dry-run: No action taken. | FILE: {file_path} | STATUS: dry-run")
		else:
			# Create a temporary file with the correct extension
			temp_output_path = f"{file_path}.temp{os.path.splitext(file_path)[1]}"
			try:
				# Trim all streams to match the video duration
				ffmpeg_command = [
					"ffmpeg",
					"-y",  # Overwrite existing files without confirmation
					"-i", file_path,
					"-t", str(video_duration),  # Set duration to match the video duration
					"-c", "copy",  # Copy streams without re-encoding
					temp_output_path
				]
				subprocess.run(ffmpeg_command, check=True)

				# Replace the original file with the temporary file
				shutil.move(temp_output_path, file_path)
				log(f"  Adjusted file saved and replaced original: {file_path} | FILE: {file_path} | STATUS: adjusted")
			except subprocess.CalledProcessError as e:
				log(f"  Error adjusting file {file_path}: {e} | STATUS: error")
				# Clean up temporary file if something goes wrong
				if os.path.exists(temp_output_path):
					os.remove(temp_output_path)
		return True
	else:
		log(f"  Discrepancy within acceptable range. No action taken. | FILE: {file_path} | STATUS: skipped")
		return False

# Recursively process files in the input directory
def process_directory(directory):
	logged_files = get_logged_files()
	processed_files = []
	skipped_files = []

	processed_count = 0
	skipped_count = 0

	for root, _, files in os.walk(directory):
		for file in files:
			if file.lower().endswith((".mkv", ".mp4", ".avi", ".mov")):
				file_path = os.path.join(root, file)
				if process_file(file_path, logged_files):
					processed_files.append(file_path)
					processed_count += 1
				else:
					skipped_files.append(file_path)
					skipped_count += 1

	if DRY_RUN:
		log(f"Process completed. {processed_count} files would be adjusted, {skipped_count} files would be skipped.")
		log("Dry-run mode summary:")
		log(f"  Total files that would be processed: {processed_count}")
		log(f"  Total files that would be skipped: {skipped_count}")
	else:
		log(f"Process completed. {processed_count} files adjusted, {skipped_count} files skipped.")
		log("Full-run mode summary:")
		log(f"  Total files processed: {processed_count}")
		log(f"  Total files skipped: {skipped_count}")

# Main function
def main():
	if not os.path.exists(INPUT_FILE_PATH):
		log(f"Input directory {INPUT_FILE_PATH} not found. Exiting.")
		return

	log("Starting duration-check process.")
	process_directory(INPUT_FILE_PATH)
	log("Process completed.")

if __name__ == "__main__":
	main()
