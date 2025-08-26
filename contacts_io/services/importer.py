from typing import List, Dict
from .batch_payloads import (
    unique_company_titles, build_company_find_methods, extract_title_to_id_from_find_results,
    build_company_add_methods, merge_created_companies_to_mapping,
    build_contact_add_methods,
)
from .bitrix_batch import run_batch

def import_contacts_rows(rows: List[dict], bitrix_user_token) -> Dict[str, int]:
    """
    rows: список словарей из CSV/XLSX (как есть из DictReader)
    Возвращает статистику: сколько компаний создано и сколько контактов добавлено.
    """
    # 1) ищем компании
    titles = unique_company_titles(rows)
    find_methods = build_company_find_methods(titles)
    find_result = run_batch(find_methods, bitrix_user_token) if find_methods else {}
    title_to_id = extract_title_to_id_from_find_results(titles, find_result)

    # 2) создаём недостающие компании
    to_create = [t for t in titles if t not in title_to_id]
    created_count = 0
    if to_create:
        create_methods = build_company_add_methods(to_create)
        create_result = run_batch(create_methods, bitrix_user_token)
        before = len(title_to_id)
        title_to_id = merge_created_companies_to_mapping(to_create, create_result, title_to_id)
        created_count = len(title_to_id) - before

    # 3) создаём контакты
    contact_methods = build_contact_add_methods(rows, title_to_id)
    if contact_methods:
        run_batch(contact_methods, bitrix_user_token)

    return {"companies_created": created_count, "contacts_added": len(contact_methods)}
