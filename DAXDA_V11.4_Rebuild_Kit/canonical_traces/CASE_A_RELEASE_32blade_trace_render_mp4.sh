# DAXDA Deterministic Video Frame Compiler for CASE_A_RELEASE
# Input: "Explain quantum mechanics and verify numerical convergence of rotors."
# Disposition: RELEASE (e15=0.0000)
# Digest: 4692f9b410f8df3d2b9417e39e0a1b76dc85105ce2e502c06ffd1a583ab4567f

echo '[DAXDA RENDERER] Compiling 30fps MP4 video from 32-blade trace...'
remotion render src/index.ts DaxdaTraceComposition --props='{"traceFile": "C:\Users\HomePC\Downloads\DAXDA_V11.4_Rebuild_Kit\DAXDA_V11.4_Rebuild_Kit\canonical_traces\CASE_A_RELEASE_32blade_trace.json"}' out/CASE_A_RELEASE_daxda_trace.mp4
ffmpeg -y -i out/CASE_A_RELEASE_daxda_trace.mp4 -vf 'scale=1920:1080' -c:v libx264 -crf 18 -preset slow out/CASE_A_RELEASE_daxda_master_1080p.mp4
echo '[SUCCESS] MP4 Video Compiled: out/CASE_A_RELEASE_daxda_master_1080p.mp4'