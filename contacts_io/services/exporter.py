from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from .bitrix_batch import run_batch

def _contact_fields_to_export(c: dict, companies: Dict[str, str]) -> Dict[str, str]:
    def first_val(lst, key="VALUE"):
        if not lst:
            return ""
        work = next((x for x in lst if str(x.get("VALUE_TYPE")).upper() == "WORK"), None)
        item = work or lst[0]
        return str(item.get(key) or "").strip()

    first_name = str(c.get("NAME") or "").strip()
    last_name  = str(c.get("LAST_NAME") or "").strip()
    phone      = first_val(c.get("PHONE") or [])
    email      = first_val(c.get("EMAIL") or [])
    comp_id    = str(c.get("COMPANY_ID") or "").strip()
    if comp_id == "0":
        comp_id = ""
    company    = companies.get(comp_id, "") if comp_id else ""

    return {
        "имя": first_name,
        "фамилия": last_name,
        "номер телефона": phone,
        "почта": email,
        "компания": company,
    }

def _list_contacts_chunk(bitrix_user_token, filter_payload: dict, start: int = 0) -> Dict:
    methods = [(
        "contacts",
        "crm.contact.list",
        {
            "order": {"ID": "ASC"},
            "filter": filter_payload,
            "select": ["ID", "NAME", "LAST_NAME", "COMPANY_ID", "PHONE", "EMAIL", "DATE_CREATE"],
            "start": start,
        }
    )]
    res = run_batch(methods, bitrix_user_token)
    return res.get("contacts", {}) or {}

def _fallback_company_ids_for_contacts(bitrix_user_token, contact_ids: List[str]) -> Dict[str, str]:
    """
    Для контактов без COMPANY_ID берём первую связанную компанию через crm.contact.company.items.get.
    Возвращает mapping contact_id -> company_id.
    """
    mapping: Dict[str, str] = {}
    if not contact_ids:
        return mapping

    for i in range(0, len(contact_ids), 50):
        chunk = contact_ids[i:i+50]
        methods = []
        for j, cid in enumerate(chunk):
            methods.append((
                f"links_{j}",
                "crm.contact.company.items.get",
                {"id": cid}  # в Bitrix24 обычно параметр называется id
            ))
        res = run_batch(methods, bitrix_user_token)
        for j, cid in enumerate(chunk):
            items = (res.get(f"links_{j}", {}) or {}).get("result") or []
            if items:
                # берём первую связь
                comp_id = str(items[0].get("COMPANY_ID") or "").strip()
                if comp_id and comp_id != "0":
                    mapping[str(cid)] = comp_id
    return mapping

def _get_companies_titles(bitrix_user_token, company_ids: List[str]) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    ids = [cid for cid in company_ids if cid and cid != "0"]
    if not ids:
        return mapping

    for i in range(0, len(ids), 50):
        chunk = ids[i:i+50]
        methods = []
        for j, cid in enumerate(chunk):
            methods.append((f"get_company_{j}", "crm.company.get", {"ID": cid}))
        res = run_batch(methods, bitrix_user_token)
        for j, cid in enumerate(chunk):
            comp = (res.get(f"get_company_{j}", {}) or {}).get("result") or {}
            title = str(comp.get("TITLE") or "").strip()
            if title:
                mapping[str(cid)] = title
    return mapping

def export_contacts(bitrix_user_token, period: str = "all") -> List[Dict[str, str]]:
    print(f"[DEBUG] export_contacts: старт, period={period}")
    flt = {}
    if period == "24h":
        since = datetime.utcnow() - timedelta(hours=24)
        flt[">DATE_CREATE"] = since.strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[DEBUG] export_contacts: фильтр: {flt}")

    start = 0
    prev_start = None
    all_contacts: List[dict] = []
    while True:
        print(f"[DEBUG] export_contacts: запрашиваем контакты, start={start}")
        try:
            part = _list_contacts_chunk(bitrix_user_token, flt, start=start)
        except Exception as e:
            print(f"[DEBUG] export_contacts: ошибка при запросе chunk: {e}")
            import traceback; traceback.print_exc()
            break
        items = part.get("result") or []
        print(f"[DEBUG] export_contacts: получено {len(items)} контактов")
        all_contacts.extend(items)
        next_val = part.get("next") or part.get("result_next")
        print(f"[DEBUG] next_val={next_val}, prev_start={prev_start}, items={len(items)}")
        if next_val and next_val != prev_start:
            prev_start = next_val
            start = int(next_val)
        else:
            break

    print(f"[DEBUG] export_contacts: всего контактов: {len(all_contacts)}")
    company_ids = []
    contacts_without_company = []
    for c in all_contacts:
        cid = str(c.get("COMPANY_ID") or "").strip()
        if cid and cid != "0":
            company_ids.append(cid)
        else:
            contacts_without_company.append(str(c.get("ID") or "").strip())
    print(f"[DEBUG] export_contacts: company_ids: {len(company_ids)}, contacts_without_company: {len(contacts_without_company)}")

    contact_to_company_fb = _fallback_company_ids_for_contacts(bitrix_user_token, contacts_without_company)
    print(f"[DEBUG] export_contacts: contact_to_company_fb: {len(contact_to_company_fb)}")

    all_company_ids = list({*company_ids, *contact_to_company_fb.values()})
    print(f"[DEBUG] export_contacts: all_company_ids: {len(all_company_ids)}")

    companies_map = _get_companies_titles(bitrix_user_token, all_company_ids)
    print(f"[DEBUG] export_contacts: companies_map: {len(companies_map)}")

    rows: List[Dict[str, str]] = []
    for c in all_contacts:
        if not c.get("COMPANY_ID"):
            fb = contact_to_company_fb.get(str(c.get("ID") or ""))
            if fb:
                c = dict(c)
                c["COMPANY_ID"] = fb
        row = _contact_fields_to_export(c, companies_map)
        rows.append(row)
    print(f"[DEBUG] export_contacts: итоговых строк: {len(rows)}")
    return rows
