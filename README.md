"# MaterialMe" 

# MaterialMe

A custom hybrid Android icon pack APK and build pipeline that merges two **Icon Pack Studio (IPS)** exports into a single standalone pack for **Smart Launcher**.

## Why This Exists

Icon Pack Studio 2.5 updated its rendering engine for its built-in **Minimal** theme, changing the look of icons compared to IPS 2.3 on older Android versions. Because Smart Launcher no longer falls back to an active IPS theme when applying a partial APK icon pack (falling back to default system icons instead), this project grafts an older IPS 2.3 export (`over.apk`) onto a complete IPS 2.5 export (`base.apk`):

* **Priority layer (`over.apk`):** Preserves 72 legacy IPS 2.3 icons and adds 119 extra app mappings from an older device export.
* **Fallback layer (`base.apk`):** Covers all remaining apps installed on the current device using the IPS 2.5 Minimal theme.
* **Output (`MaterialMe.apk`):** A single self-contained, aligned, and signed APK (`283` total icon mappings) that requires no manual per-app overrides.

## Repository Structure

```text
MaterialMe/
├── MaterialMe.apk          # Final rebuilt, zipaligned, and signed icon pack APK
├── base.apk                # Base icon pack exported from Icon Pack Studio 2.5
├── over.apk                # Legacy override icon pack exported from Icon Pack Studio 2.3
├── base/                   # Decompiled base.apk resources, assets, and smali
│   ├── assets/
│   │   ├── appfilter.xml   # Master ComponentInfo -> drawable mappings
│   │   └── drawable.xml    # Icon picker index
│   └── res/
│       ├── drawable-nodpi/ # Rendered icon PNGs (ic_0000.png – ic_0282.png)
│       ├── raw/            # Runtime appfilter.xml and config.json
│       ├── values/         # App metadata (strings.xml)
│       └── values-nodpi/   # Pre-allocated drawable resource definitions
├── over/                   # Decompiled over.apk used as the icon override source
├── merge.py                # Merges over/ icons & ComponentInfo mappings into base/
├── fix.py                  # Strips conflicting placeholder drawables in values-nodpi/drawables.xml
├── apktool.jar             # Apktool v3.0.3 for decompiling and rebuilding APKs
└── uber-apk-signer.jar     # Uber Apk Signer v1.3.0 for zipaligning and signing

```

*(Note: `*_unsigned.apk`, `merged_unsigned*`, and `.idsig` files in the workspace are intermediate build artifacts and can be safely ignored or removed.)*

## Installation

Install `MaterialMe.apk` directly on your Android device or via ADB:

```bash
adb install -r MaterialMe.apk

```

Then apply **MaterialMe** in **Smart Launcher** under **Settings → Global Appearance → Icon Appearance**.

## Rebuilding from Source

If you want to modify icons, update `appfilter.xml` mappings, or re-merge two different IPS exports:

1. **Decompile both APKs** (if starting from fresh `.apk` files):
```bash
java -jar apktool.jar d base.apk -o base
java -jar apktool.jar d over.apk -o over

```


2. **Merge icons and resolve `aapt2` drawable conflicts:**
```bash
python merge.py
python fix.py

```


3. **Rebuild, zipalign, and sign:**
```bash
java -jar apktool.jar b base -o MaterialMe_unsigned.apk
java -jar uber-apk-signer.jar -a MaterialMe_unsigned.apk

```



```

