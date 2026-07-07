import json

def load(f):
    with open(f) as fh:
        return json.load(fh)

for mode in ['cheap', 'best', 'standard']:
    d = load(f'evaluation_{mode}_results.json')
    rows = []
    for r in d:
        m_short = r['model'].split('/')[-1] if '/' in r['model'] else r['model']
        rows.append(
            f"  {{id:{r['id']},cat:\"{r['category']}\","
            f"query:\"{r['query_preview'][:70].replace(chr(34), chr(39))}\","
            f"model:\"{r['model']}\",tier:{r['tier']},"
            f"llm:{'true' if r['llm_used'] else 'false'},"
            f"src:\"{r['classifier_source']}\","
            f"v:{'true' if r['needs_vision'] else 'false'},"
            f"t:{'true' if r['needs_thinking'] else 'false'},"
            f"c:{'true' if r['needs_coding'] else 'false'},"
            f"ms:{round(r['total_time_ms'],1)},"
            f"pass:{'true' if r['is_correct'] else 'false'}}}"
        )
    print(f"// {mode.upper()} DATA START")
    print("[\n" + ",\n".join(rows) + "\n]")
    print(f"// {mode.upper()} DATA END")
