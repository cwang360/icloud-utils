# icloud-utils
Miscellaneous iCloud automation scripts
## icloud_export.py
Exports and saves all iCloud photos in folders organized by date. Preserves all EXIF metadata and file creation dates. 

Example directory tree:
```
out_dir/
├── 2020/
│   ├── 2020-01-05/
│   │   ├── IMG_1234.PNG
│   │   ├── IMG_1235.JPEG
│   │   ├── IMG_1236.MOV
│   │   └── ...
│   ├── 2020-01-09
│   ├── 2020-03-20
│   └── ...
├── 2021
├── 2022
└── ...
```