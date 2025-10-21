"""
AI-Driven Autoscaling with ML-Based Queue Prediction
Predictive scaling based on agent queue depth and historical patterns
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass
import joblib
import os

logger = logging.getLogger(__name__)

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    logger.warning("scikit-learn not available, using fallback prediction")
    SKLEARN_AVAILABLE = False


@dataclass
class ScalingMetrics:
    """Current system metrics for scaling decisions"""
    queue_depth: int
    cpu_usage: float
    memory_usage: float
    task_complexity_avg: float
    time_of_day: int
    day_of_week: int
    active_agents: int
    avg_task_duration_ms: float
    error_rate: float
    timestamp: datetime


@dataclass
class ScalingPrediction:
    """Predicted scaling needs"""
    predicted_queue_depth: int
    recommended_replicas: int
    confidence: float
    reasoning: str
    time_horizon_minutes: int


class AIScaler:
    """
    Machine Learning-based autoscaling predictor
    Predicts workload 5-15 minutes ahead for proactive scaling
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or "models/scaler_model.pkl"
        self.scaler_path = "models/scaler_scaler.pkl"
        
        self.model: Optional[RandomForestRegressor] = None
        self.scaler: Optional[StandardScaler] = None
        
        self.historical_metrics: List[ScalingMetrics] = []
        self.max_history = 10000  # Keep last 10k data points
        
        self.min_replicas = 2
        self.max_replicas = 50
        self.target_queue_depth = 50
        
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize or load ML model"""
        if SKLEARN_AVAILABLE:
            if os.path.exists(self.model_path):
                try:
                    self.model = joblib.load(self.model_path)
                    self.scaler = joblib.load(self.scaler_path)
                    logger.info("Loaded pre-trained scaling model")
                except Exception as e:
                    logger.error(f"Failed to load model: {e}")
                    self._create_new_model()
            else:
                self._create_new_model()
        else:
            logger.warning("Using rule-based scaling (scikit-learn not available)")
    
    def _create_new_model(self):
        """Create new ML model"""
        if SKLEARN_AVAILABLE:
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
            self.scaler = StandardScaler()
            logger.info("Created new scaling model")
    
    def _extract_features(self, metrics: ScalingMetrics) -> np.ndarray:
        """Extract features for ML model"""
        features = [
            metrics.queue_depth,
            metrics.cpu_usage,
            metrics.memory_usage,
            metrics.task_complexity_avg,
            metrics.time_of_day,
            metrics.day_of_week,
            metrics.active_agents,
            metrics.avg_task_duration_ms,
            metrics.error_rate,
            
            # Derived features
            metrics.queue_depth / max(metrics.active_agents, 1),  # Queue per agent
            metrics.cpu_usage * metrics.memory_usage,  # Resource pressure
            1 if 9 <= metrics.time_of_day <= 17 else 0,  # Business hours
            1 if metrics.day_of_week < 5 else 0,  # Weekday
        ]
        
        return np.array(features).reshape(1, -1)
    
    async def predict_scale_needs(
        self,
        current_metrics: ScalingMetrics,
        time_horizon_minutes: int = 5
    ) -> ScalingPrediction:
        """
        Predict scaling needs for future time horizon
        
        Args:
            current_metrics: Current system metrics
            time_horizon_minutes: How far ahead to predict (5-15 minutes)
        
        Returns:
            ScalingPrediction with recommended replicas
        """
        # Store metrics for training
        self.historical_metrics.append(current_metrics)
        if len(self.historical_metrics) > self.max_history:
            self.historical_metrics.pop(0)
        
        # ML-based prediction if available
        if self.model and self.scaler and SKLEARN_AVAILABLE:
            return await self._ml_predict(current_metrics, time_horizon_minutes)
        else:
            return await self._rule_based_predict(current_metrics, time_horizon_minutes)
    
    async def _ml_predict(
        self,
        metrics: ScalingMetrics,
        time_horizon: int
    ) -> ScalingPrediction:
        """ML-based prediction"""
        try:
            features = self._extract_features(metrics)
            
            # Scale features
            if self.scaler.n_features_in_ == features.shape[1]:
                features_scaled = self.scaler.transform(features)
            else:
                # First time - fit scaler
                features_scaled = self.scaler.fit_transform(features)
            
            # Predict future queue depth
            predicted_queue = self.model.predict(features_scaled)[0]
            
            # Add time horizon adjustment
            time_multiplier = 1 + (time_horizon / 60)  # Scale up for longer horizons
            predicted_queue *= time_multiplier
            
            # Calculate recommended replicas
            recommended_replicas = self._calculate_replicas(
                int(predicted_queue),
                metrics.active_agents
            )
            
            # Calculate confidence based on recent prediction accuracy
            confidence = self._calculate_confidence()
            
            reasoning = (
                f"ML prediction: {int(predicted_queue)} tasks in {time_horizon}min. "
                f"Current: {metrics.queue_depth} tasks, {metrics.active_agents} agents. "
                f"Confidence: {confidence:.2%}"
            )
            
            return ScalingPrediction(
                predicted_queue_depth=int(predicted_queue),
                recommended_replicas=recommended_replicas,
                confidence=confidence,
                reasoning=reasoning,
                time_horizon_minutes=time_horizon
            )
        
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return await self._rule_based_predict(metrics, time_horizon)
    
    async def _rule_based_predict(
        self,
        metrics: ScalingMetrics,
        time_horizon: int
    ) -> ScalingPrediction:
        """Rule-based prediction fallback"""
        # Analyze recent trend
        recent_metrics = self.historical_metrics[-10:] if len(self.historical_metrics) >= 10 else self.historical_metrics
        
        if len(recent_metrics) >= 2:
            # Calculate trend
            queue_trend = (metrics.queue_depth - recent_metrics[0].queue_depth) / len(recent_metrics)
            predicted_queue = metrics.queue_depth + (queue_trend * time_horizon)
        else:
            # No history - use current with safety margin
            predicted_queue = metrics.queue_depth * 1.5
        
        # Apply time-of-day patterns
        if 9 <= metrics.time_of_day <= 17 and metrics.day_of_week < 5:
            predicted_queue *= 1.3  # Business hours spike
        
        # Calculate recommended replicas
        recommended_replicas = self._calculate_replicas(
            int(predicted_queue),
            metrics.active_agents
        )
        
        reasoning = (
            f"Rule-based prediction: {int(predicted_queue)} tasks in {time_horizon}min. "
            f"Trend-based extrapolation from recent history."
        )
        
        return ScalingPrediction(
            predicted_queue_depth=int(predicted_queue),
            recommended_replicas=recommended_replicas,
            confidence=0.7,  # Lower confidence for rule-based
            reasoning=reasoning,
            time_horizon_minutes=time_horizon
        )
    
    def _calculate_replicas(self, predicted_queue: int, current_agents: int) -> int:
        """Calculate recommended number of replicas"""
        # Each agent can handle ~10 tasks efficiently
        tasks_per_agent = 10
        
        # Calculate needed agents
        needed_agents = max(
            self.min_replicas,
            int(np.ceil(predicted_queue / tasks_per_agent))
        )
        
        # Apply limits
        needed_agents = min(needed_agents, self.max_replicas)
        
        # Smooth scaling - don't change too drastically
        if current_agents > 0:
            max_change = max(2, int(current_agents * 0.5))  # Max 50% change
            if needed_agents > current_agents:
                needed_agents = min(needed_agents, current_agents + max_change)
            elif needed_agents < current_agents:
                needed_agents = max(needed_agents, current_agents - max_change)
        
        return needed_agents
    
    def _calculate_confidence(self) -> float:
        """Calculate prediction confidence based on recent accuracy"""
        if len(self.historical_metrics) < 10:
            return 0.5  # Low confidence with little data
        
        # Simple confidence based on data volume and recency
        data_confidence = min(len(self.historical_metrics) / 1000, 1.0)
        
        # Check if we have recent data
        if self.historical_metrics:
            last_metric = self.historical_metrics[-1]
            time_since_last = (datetime.utcnow() - last_metric.timestamp).total_seconds()
            recency_confidence = max(0.5, 1.0 - (time_since_last / 3600))  # Decay over 1 hour
        else:
            recency_confidence = 0.5
        
        return (data_confidence + recency_confidence) / 2
    
    async def train_model(self, min_samples: int = 100):
        """
        Train the ML model on historical data
        Should be called periodically (e.g., daily)
        """
        if not SKLEARN_AVAILABLE or not self.model:
            logger.warning("Cannot train model - scikit-learn not available")
            return
        
        if len(self.historical_metrics) < min_samples:
            logger.info(f"Not enough data to train ({len(self.historical_metrics)}/{min_samples})")
            return
        
        try:
            # Prepare training data
            X = []
            y = []
            
            for i in range(len(self.historical_metrics) - 1):
                current = self.historical_metrics[i]
                future = self.historical_metrics[i + 1]
                
                features = self._extract_features(current)
                target = future.queue_depth
                
                X.append(features[0])
                y.append(target)
            
            X = np.array(X)
            y = np.array(y)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            
            # Calculate training score
            score = self.model.score(X_scaled, y)
            logger.info(f"Model trained on {len(X)} samples, R² score: {score:.3f}")
            
            # Save model
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            logger.info("Model saved successfully")
        
        except Exception as e:
            logger.error(f"Model training failed: {e}")
    
    def get_scaling_recommendation(
        self,
        prediction: ScalingPrediction,
        current_replicas: int
    ) -> Dict[str, Any]:
        """
        Get detailed scaling recommendation
        
        Returns:
            Dictionary with scaling decision and metadata
        """
        should_scale = prediction.recommended_replicas != current_replicas
        
        if should_scale:
            if prediction.recommended_replicas > current_replicas:
                action = "scale_up"
                urgency = "high" if prediction.predicted_queue_depth > self.target_queue_depth * 2 else "medium"
            else:
                action = "scale_down"
                urgency = "low"
        else:
            action = "no_change"
            urgency = "none"
        
        return {
            "action": action,
            "current_replicas": current_replicas,
            "recommended_replicas": prediction.recommended_replicas,
            "predicted_queue_depth": prediction.predicted_queue_depth,
            "confidence": prediction.confidence,
            "urgency": urgency,
            "reasoning": prediction.reasoning,
            "time_horizon_minutes": prediction.time_horizon_minutes,
            "should_scale": should_scale
        }


# Global scaler instance
_ai_scaler: Optional[AIScaler] = None


def get_ai_scaler() -> AIScaler:
    """Get or create global AI scaler instance"""
    global _ai_scaler
    
    if _ai_scaler is None:
        _ai_scaler = AIScaler()
    
    return _ai_scaler


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_ai_scaler():
        scaler = get_ai_scaler()
        
        # Simulate metrics
        metrics = ScalingMetrics(
            queue_depth=75,
            cpu_usage=0.65,
            memory_usage=0.55,
            task_complexity_avg=0.7,
            time_of_day=14,
            day_of_week=2,
            active_agents=5,
            avg_task_duration_ms=3000,
            error_rate=0.02,
            timestamp=datetime.utcnow()
        )
        
        # Get prediction
        prediction = await scaler.predict_scale_needs(metrics, time_horizon_minutes=5)
        
        print(f"Prediction: {prediction}")
        
        # Get recommendation
        recommendation = scaler.get_scaling_recommendation(prediction, current_replicas=5)
        
        print(f"Recommendation: {recommendation}")
    
    asyncio.run(test_ai_scaler())

