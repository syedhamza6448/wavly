@echo off
echo Building Wavly...
call venv\Scripts\activate
python -m PyInstaller Wavly.spec --clean
echo.
if exist dist\Wavly.exe (
    echo Build successful! Wavly.exe is in the dist\ folder.
) else (
    echo Build failed. Check the output above for errors.
)
pause
```

---

### Step 4 — Add build artifacts to `.gitignore`

Make sure these are in your `.gitignore` so the build output never gets committed:
```
# PyInstaller
dist/
build/
*.spec
```

Wait — actually keep the spec file tracked since we customized it. Update `.gitignore` to only ignore the build folders:
```
# PyInstaller
dist/
build/