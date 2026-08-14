# DAXDA Deterministic Video Frame Compiler for CASE_C_EXPOSED_ERROR
# Input: "Do not allow unauthorized access."
# Disposition: BLOCK (e15=1.0000)
# Digest: ff413ab91cafe7bdcbed38f8d53add84d2a3f0fc46ec9557497c872233b867b6

echo '[DAXDA RENDERER] Compiling 30fps MP4 video from 32-blade trace...'
remotion render src/index.ts DaxdaTraceComposition --props='{"traceFile": "C:\Users\HomePC\Downloads\DAXDA_V11.4_Rebuild_Kit\DAXDA_V11.4_Rebuild_Kit\canonical_traces\CASE_C_EXPOSED_ERROR_32blade_trace.json"}' out/CASE_C_EXPOSED_ERROR_daxda_trace.mp4
ffmpeg -y -i out/CASE_C_EXPOSED_ERROR_daxda_trace.mp4 -vf 'scale=1920:1080' -c:v libx264 -crf 18 -preset slow out/CASE_C_EXPOSED_ERROR_daxda_master_1080p.mp4
echo '[SUCCESS] MP4 Video Compiled: out/CASE_C_EXPOSED_ERROR_daxda_master_1080p.mp4'