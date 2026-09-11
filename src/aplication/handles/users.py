"""
handles de users
"""
from fastapi import APIRouter, HTTPException
from src.service.module import control_db
from src.aplication.dependences.depends import depends_user