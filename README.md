# LOG FILE VIEWER

**Simple web based viewing of log files**

---

## Features
- Controlled with YAML
- Single log file viewer
- Break log files by specific configurable character to split logs
- Order by newest or oldest (TODO)
- Search through logs (TODO)
- Directory logs (TODO)
- Read compressed logs (TODO)
- Read remote logs (TODO)

## YAML
```yaml
hostaddress: localhost
hostport: 8888
logs:
  - name: single
    logfile: ./output.log
    breaksymbol: ---
  - name: Directory
    logfile: ./nginx/
    type: directory
```

