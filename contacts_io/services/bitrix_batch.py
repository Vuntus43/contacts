# contacts_io/services/bitrix_batch.py
from typing import List, Tuple, Optional, Dict

# твой batch лежит тут:
from integration_utils.bitrix24.functions.batch_api_call import _batch_api_call

BatchMethod = Tuple[str, str, Optional[dict]]

def run_batch(
    methods: List[BatchMethod],
    bitrix_user_token,
    halt: int = 0,
    chunk_size: int = 50,
) -> Dict[str, dict]:
    """
    Обёртка над _batch_api_call.
    Возвращает обычный dict:
      {'name': {'result': ..., 'error': ..., 'total': ..., 'next': ...}, ...}
    """
    if not methods:
        return {}

    res = _batch_api_call(
        methods=methods,
        bitrix_user_token=bitrix_user_token,
        function_calling_from_bitrix_user_token_think_before_use=True,
        halt=halt,
        chunk_size=chunk_size,  # Bitrix максимум 50
    )
    # _batch_api_call возвращает BatchResultDict (OrderedDict-подобный) — приведём к dict
    return dict(res)
