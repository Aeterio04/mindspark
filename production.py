# use_in_production.py
import torch
import pandas as pd
import numpy as np
from algorithm import TwinHeadNN
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import joblib

class ProductionPredictor:
    def __init__(self, model_path='twin_head_model.pth'):
        # Load the saved model
        self.model = torch.load(model_path, map_location='cpu')
        self.model.eval()  # Set to evaluation mode
        print("✅ Production model loaded successfully!")
    
    def predict_for_new_order(self, buffer, priority, hour, color, oven):
        """
        Predict processing time and downtime risk for a new manufacturing order
        
        Args:
            buffer: Which buffer line (1-9)
            priority: 1 for high priority, 0 for normal
            hour: Hour of day (0-23)
            color: Product color (C1, C2, C3, etc.)
            oven: Which oven (O1 or O2)
        """
        # Prepare features (you'll need to save scaler/encoder from training)
        # For now, using dummy preprocessing - in real case, save these with model
        features = self._prepare_features(buffer, priority, hour, color, oven)
        
        with torch.no_grad():
            features_tensor = torch.tensor(features, dtype=torch.float32)
            processing_time, downtime_risk = self.model(features_tensor)
        
        return {
            'processing_time_seconds': round(processing_time.item(), 1),
            'downtime_risk_percent': round(downtime_risk.item() * 100, 1),
            'recommended_buffer': buffer,
            'estimated_completion': f"{processing_time.item()/60:.1f} minutes"
        }
    
    def _prepare_features(self, buffer, priority, hour, color, oven):
        # This is simplified - in production, you'd save the actual scaler/encoder
        # For demo purposes, using basic preprocessing
        num_features = np.array([[buffer, priority, hour]])
        # Simple scaling (replace with your actual scaler)
        num_features = (num_features - np.array([5, 0.5, 12])) / np.array([3, 0.5, 6])
        
        # One-hot encoding (simplified)
        color_encoded = [0] * 12  # 12 colors in original
        oven_encoded = [0] * 2    # 2 ovens
        
        # Mock encoding - in real case, use saved encoder
        if color in [f'C{i}' for i in range(1,13)]:
            color_idx = int(color[1:]) - 1
            color_encoded[color_idx] = 1
        
        if oven == 'O1': oven_encoded[0] = 1
        else: oven_encoded[1] = 1
        
        features = np.hstack([num_features[0], color_encoded, oven_encoded])
        return features.reshape(1, -1)

# Example usage
if __name__ == "__main__":
    print("🏭 Manufacturing AI - Production Deployment")
    print("=" * 50)
    
    # Initialize the predictor
    predictor = ProductionPredictor('twin_head_model.pth')
    
    # Test cases - real manufacturing scenarios
    test_orders = [
        {"buffer": 3, "priority": 0, "hour": 14, "color": "C1", "oven": "O1", "desc": "Normal order - Color C1"},
        {"buffer": 1, "priority": 1, "hour": 9, "color": "C2", "oven": "O2", "desc": "Rush order - Morning"},
        {"buffer": 5, "priority": 0, "hour": 18, "color": "C3", "oven": "O1", "desc": "Evening batch - Complex color"},
        {"buffer": 2, "priority": 1, "hour": 22, "color": "C1", "oven": "O2", "desc": "Night shift priority"}
    ]
    
    print("📊 Production Predictions:")
    print("-" * 50)
    
    for i, order in enumerate(test_orders, 1):
        result = predictor.predict_for_new_order(
            buffer=order["buffer"],
            priority=order["priority"], 
            hour=order["hour"],
            color=order["color"],
            oven=order["oven"]
        )
        
        print(f"Order {i}: {order['desc']}")
        print(f"   ⏱️  Processing Time: {result['processing_time_seconds']} sec")
        print(f"   ⚠️  Downtime Risk: {result['downtime_risk_percent']}%")
        print(f"   📍 Buffer: {result['recommended_buffer']}")
        print(f"   🎯 ETA: {result['estimated_completion']}")
        print()