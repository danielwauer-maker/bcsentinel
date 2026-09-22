"""Run-scoped finding identities; legacy fallback never exposes business contents."""
from collections import Counter
import hashlib
import json

from fastapi import HTTPException


def resolve_finding_ids(issues) -> list[str]:
    counts = Counter(str(issue.code).strip().upper() for issue in issues)
    occurrences, seen, result = Counter(), set(), []
    for issue in issues:
        code = str(issue.code).strip().upper()
        explicit = getattr(issue, 'finding_id', None)
        if explicit is not None:
            identity = str(explicit)
        elif counts[code] == 1:
            identity = 'legacy:' + code
        else:
            # Old clients have no group identifier. Preserve the full multiset,
            # independent of order, including indistinguishable identical rows.
            value = issue.model_dump(mode='json', exclude={'finding_id', 'estimated_impact_eur'})
            value['code'] = code
            digest = hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
            occurrences[digest] += 1
            identity = f'legacy-group:{digest}:{occurrences[digest]}'
        if identity in seen:
            raise HTTPException(status_code=422, detail='Duplicate finding identity in scan snapshot.')
        seen.add(identity)
        result.append(identity)
    return result
