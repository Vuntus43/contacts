from typing import Dict, List, Tuple, Optional

BatchMethod = Tuple[str, str, Optional[dict]]

def unique_company_titles(rows: List[dict]) -> List[str]:
    seen, titles = set(), []
    for r in rows:
        t = (r.get("компания") or r.get("company") or r.get("company_name") or "").strip()
        if t and t not in seen:
            seen.add(t); titles.append(t)
    return titles

def build_company_find_methods(titles: List[str]) -> List[BatchMethod]:
    return [
        (f"find_company_{i}", "crm.company.list",
         {"filter": {"TITLE": t}, "select": ["ID", "TITLE"]})
        for i, t in enumerate(titles)
    ]

def extract_title_to_id_from_find_results(titles: List[str], batch_result: Dict[str, dict]) -> Dict[str, str]:
    m: Dict[str, str] = {}
    for i, t in enumerate(titles):
        entry = batch_result.get(f"find_company_{i}", {})
        items = entry.get("result") or []
        if items:
            cid = str(items[0].get("ID") or "")
            if cid: m[t] = cid
    return m

def build_company_add_methods(titles_to_create: List[str]) -> List[BatchMethod]:
    return [
        (f"add_company_{i}", "crm.company.add", {"fields": {"TITLE": t}})
        for i, t in enumerate(titles_to_create)
    ]

def merge_created_companies_to_mapping(titles_to_create: List[str], batch_result: Dict[str, dict], mapping: Dict[str, str]) -> Dict[str, str]:
    for i, t in enumerate(titles_to_create):
        new_id = batch_result.get(f"add_company_{i}", {}).get("result")
        if new_id: mapping[t] = str(new_id)
    return mapping

def normalize_row(row: dict) -> dict:
    return {
        "first_name": (row.get("имя") or row.get("first_name") or "").strip(),
        "last_name": (row.get("фамилия") or row.get("last_name") or "").strip(),
        "phone": (row.get("номер телефона") or row.get("phone") or "").strip(),
        "email": (row.get("почта") or row.get("email") or "").strip(),
        "company_name": (row.get("компания") or row.get("company") or row.get("company_name") or "").strip(),
    }

def build_contact_add_methods(rows: List[dict], title_to_id: Dict[str, str]) -> List[BatchMethod]:
    methods: List[BatchMethod] = []
    for i, raw in enumerate(rows):
        r = normalize_row(raw)
        fields = {"NAME": r["first_name"], "LAST_NAME": r["last_name"], "OPENED": "Y"}
        if r["phone"]: fields["PHONE"] = [{"VALUE": r["phone"], "VALUE_TYPE": "WORK"}]
        if r["email"]: fields["EMAIL"] = [{"VALUE": r["email"], "VALUE_TYPE": "WORK"}]
        if r["company_name"] in title_to_id: fields["COMPANY_ID"] = title_to_id[r["company_name"]]
        methods.append((f"add_contact_{i}", "crm.contact.add", {"fields": fields}))
    return methods
