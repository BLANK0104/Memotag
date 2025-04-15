# Audio Analysis Setup Guide

This document provides instructions for setting up the acoustic analysis functionality in MemoTag.

## Required Dependencies

For the acoustic analysis to work properly, you need to install these libraries:

```bash
pip install librosa soundfile jaraco.text
```

## Troubleshooting Common Issues

### "No module named 'jaraco'" Error

If you see this error:
```
Error loading audio file: No module named 'jaraco'
```

Install the missing dependency:
```bash
pip install jaraco.text
```

### Audio File Loading Issues

If you encounter problems loading audio files:

1. Ensure you have FFmpeg installed on your system
   - Windows: Download from https://www.gyan.dev/ffmpeg/builds/ and add to PATH
   - macOS: `brew install ffmpeg`
   - Linux: `apt-get install ffmpeg` (Ubuntu/Debian) or `yum install ffmpeg` (CentOS/RHEL)

2. Check that soundfile is properly installed:
   ```bash
   pip uninstall soundfile
   pip install soundfile
   ```

### Windows-specific Issues

On Windows, you may need specific versions of PyAudio:

```bash
pip install PyAudio==0.2.11
```

If that fails, try:
```bash
pip install pipwin
pipwin install pyaudio
```

## Testing Your Setup

To verify your audio setup is working correctly:

```bash
python -c "import librosa; import soundfile; print('Audio libraries loaded successfully')"
```

If this runs without errors, your audio analysis setup should work properly.
