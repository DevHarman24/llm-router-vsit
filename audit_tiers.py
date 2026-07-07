import sys
sys.path.insert(0, '.')
from router.models import get_catalog, CODING_MODELS, THINKING_MODELS, VISION_MODELS

catalog = get_catalog()

for tier_label, tier_num in [('MID (Tier 2)', 2), ('LOW (Tier 3)', 3)]:
    print(f'\n{"="*70}')
    print(f'  {tier_label} — missing capability flags')
    print(f'{"="*70}')

    tier_models = [m for m in catalog if m.tier == tier_num]
    
    missing_coding = []
    missing_vision = []
    missing_thinking = []
    
    for m in tier_models:
        # Check if model name suggests coding but flag is False
        coding_keywords = ['coder', 'code', 'codex', 'devstral', 'qwen-coder', 'starcoder', 'codellama']
        vision_keywords = ['vision', 'vl', 'visual', 'pixtral', 'llava', 'image']
        thinking_keywords = ['think', 'reason', 'r1', 'qwq', 'reflect', 'o1', 'o3']

        if not m.supports_coding and any(k in m.id.lower() for k in coding_keywords):
            missing_coding.append(m)
        if not m.supports_vision and any(k in m.id.lower() for k in vision_keywords):
            missing_vision.append(m)
        if not m.supports_thinking and any(k in m.id.lower() for k in thinking_keywords):
            missing_thinking.append(m)

    print(f'\n  --- Missing CODING flag ({len(missing_coding)} models) ---')
    for m in missing_coding:
        print(f'    {m.id:<55} price={m.price_per_million_tokens:.3f}/M')

    print(f'\n  --- Missing VISION flag ({len(missing_vision)} models) ---')
    for m in missing_vision:
        print(f'    {m.id:<55} price={m.price_per_million_tokens:.3f}/M')

    print(f'\n  --- Missing THINKING flag ({len(missing_thinking)} models) ---')
    for m in missing_thinking:
        print(f'    {m.id:<55} price={m.price_per_million_tokens:.3f}/M')
