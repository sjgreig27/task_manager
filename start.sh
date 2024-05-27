#!/bin/sh

piccolo migrations forward all
exec uvicorn app:app --proxy-headers --port 8000 --no-server-header --host "0.0.0.0" --loop "uvloop"

