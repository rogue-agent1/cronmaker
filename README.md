# cronmaker
Cron expression builder, explainer, and next-run calculator.
```bash
python cronmaker.py explain "*/5 * * * *"
python cronmaker.py next "0 9 * * 1-5" -n 10
python cronmaker.py presets
python cronmaker.py build --minute 30 --hour 9 --weekday 1-5
```
## Zero dependencies. Python 3.6+.
