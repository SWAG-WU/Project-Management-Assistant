#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')

from planner import generate_plan
from project import save_project

name = "Todo Manager"
description = "A simple todo list management tool"
days = 7

print(f"Creating project: {name}")
print(f"Description: {description}")
print(f"Days: {days}\n")

print("Calling LLM to generate plan...")
project = generate_plan(name, description, days)
save_project(project)

print("\n[Done] Project plan created and saved!")
print(f"\nProject: {project['project_name']}")
print(f"Total days: {project['total_days']}")
print(f"Tasks: {len(project['tasks'])}")
