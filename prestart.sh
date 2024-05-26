#!/bin/sh

piccolo migrations forward session_auth
piccolo migrations forward user
piccolo migrations forward tasks
piccolo fixtures load fixture.json

