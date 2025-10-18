# quick_test.py
from deploy import ManufacturingAISystem

def main():
    # Initialize once
    ai = ManufacturingAISystem()
    
    # Test some predictions
    test_cases = [
        (3, 0, 14, 'C1', 'O1'),
        (1, 1, 9, 'C2', 'O2'), 
        (5, 0, 18, 'C3', 'O1')
    ]
    
    print("🔧 Quick Predictions Test:")
    for buffer, priority, hour, color, oven in test_cases:
        result = ai.predict_processing(buffer, priority, hour, color, oven)
        print(f"Buffer {buffer}, {color}, {oven}: {result['processing_time_seconds']:.1f}s, {result['downtime_risk_percent']:.1f}% risk")
    
    # Get a smart recommendation
    print("\n🤖 Smart Recommendation:")
    occupancies = {1: 5, 2: 10, 3: 2, 4: 12, 5: 8, 6: 6, 7: 9, 8: 4, 9: 7}
    rec = ai.recommend_best_buffer(0, 14, 'C1', 'O1', occupancies)
    print(f"Recommended: Buffer {rec['recommended_buffer']}")
    print(f"Expected: {rec['expected_processing_time']:.1f}s, {rec['expected_downtime_risk']:.1f}% risk")

if __name__ == "__main__":
    main()