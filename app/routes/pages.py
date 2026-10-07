"""
routes/pages.py — HTML page routes served via Jinja2 templates.
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

page_router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@page_router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@page_router.get("/members", response_class=HTMLResponse)
async def members_page(request: Request):
    return templates.TemplateResponse(request=request, name="members.html")


@page_router.get("/sports", response_class=HTMLResponse)
async def sports_page(request: Request):
    return templates.TemplateResponse(request=request, name="sports.html")


@page_router.get("/teams", response_class=HTMLResponse)
async def teams_page(request: Request):
    return templates.TemplateResponse(request=request, name="teams.html")


@page_router.get("/tournaments", response_class=HTMLResponse)
async def tournaments_page(request: Request):
    return templates.TemplateResponse(request=request, name="tournaments.html")


@page_router.get("/equipment", response_class=HTMLResponse)
async def equipment_page(request: Request):
    return templates.TemplateResponse(request=request, name="equipment.html")


@page_router.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    return templates.TemplateResponse(request=request, name="reports.html")
