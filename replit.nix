{ pkgs }: {
  deps = [
    pkgs.python312    # ou python3 selon ton runtime
    pkgs.ffmpeg       # FFmpeg pour l’audio
    pkgs.libopus      # Opus pour Discord voice
  ];
}