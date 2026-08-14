import os
import zipfile

pkg_dir = r'c:\Users\HomePC\Downloads\DAXDA_V11.4_Rebuild_Kit\daxda_hostinger_package'
zip_path = r'c:\Users\HomePC\Downloads\DAXDA_V11.4_Rebuild_Kit\daxda_v11.4_hostinger_deployment.zip'

print(f"Creating zip file: {zip_path}...")

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(pkg_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, pkg_dir)
            zf.write(full_path, rel_path)

size_mb = os.path.getsize(zip_path) / (1024 * 1024)
print(f"[SUCCESS] Zip file created! Size: {size_mb:.2f} MB")
