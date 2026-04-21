To install dependencies run:

```bash
pip install PyInstaller
pip install bleak
pip install numpy
```

To compile python script run:

```
py -m PyInstaller --onefile --noconsole --windowed glove_driver.py
```

To modify the UI that runs on it's own thread use:

```
    window.after(0, method_to_modify)
```
