from router.models import get_best_model_for_tier
import router.models

print("--- TESTING EPOCH BENCHMARKS ---")
router.models.USE_EPOCH_BENCHMARKS = True
best = get_best_model_for_tier(tier=1, mode="best")
print("Best tier 1 model (Epoch):", best.id if best else None, best.name if best else None)

print("\n--- TESTING OPENROUTER BENCHMARKS ---")
router.models.USE_EPOCH_BENCHMARKS = False
best = get_best_model_for_tier(tier=1, mode="best")
print("Best tier 1 model (OpenRouter):", best.id if best else None, best.name if best else None)
