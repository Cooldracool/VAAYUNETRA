from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse

from backend.models.schemas import LegalNoticeDocument
from backend.services.incident_manager import incident_manager

router = APIRouter(tags=["Legal Notices & Documents"])


@router.get("/api/v1/events/{event_id}/notice", response_model=LegalNoticeDocument, summary="Generate Legal Notice Dossier")
@router.get("/api/events/{event_id}/notice", response_model=LegalNoticeDocument, include_in_schema=False)
async def get_legal_notice(event_id: str, format: Optional[str] = Query("json", description="json or html")):
    """
    Generates a formal legal regulatory enforcement notice dossier under the
    Air (Prevention and Control of Pollution) Act, 1981 for the given event ID.
    Supports printable HTML output or structured JSON payload.
    """
    notice = incident_manager.generate_legal_notice(event_id)
    if not notice:
        raise HTTPException(status_code=404, detail=f"Environmental Event {event_id} not found for notice generation")
        
    if format and format.lower() == "html":
        return HTMLResponse(content=notice.html_document, status_code=200)
    elif format and format.lower() == "hindi":
        hindi_html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="UTF-8">
<title>वैधानिक नोटिस — {notice.reference_no}</title>
<style>
  body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; line-height: 1.6; color: #111; }}
  .header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 12px; margin-bottom: 20px; }}
  .gov-title {{ font-size: 18px; font-weight: bold; color: #0f172a; }}
  .box {{ background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 20px; font-size: 14px; white-space: pre-wrap; line-height: 1.8; }}
</style>
</head>
<body>
<div class="header">
  <div class="gov-title">दिल्ली राष्ट्रीय राजधानी क्षेत्र सरकार / राज्य पर्यावरण प्राधिकरण</div>
  <div style="font-weight: 600; color: #0284c7; margin-top: 4px;">वायुनेत्र स्वायत्त प्रवर्तन एवं वैधानिक प्रकोष्ठ</div>
  <div style="font-size: 12px; color: #64748b;">(वायु (प्रदूषण निवारण एवं नियंत्रण) अधिनियम, 1981 की धारा 31ए के अंतर्गत वैधानिक निर्देश)</div>
</div>
<div class="box">{notice.hindi_document}</div>
</body>
</html>"""
        return HTMLResponse(content=hindi_html, status_code=200)
        
    return notice
