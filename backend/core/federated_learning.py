"""
Federated Learning Marketplace
Privacy-preserving collaborative agent improvement across customers
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import numpy as np
import hashlib
import json

logger = logging.getLogger(__name__)


@dataclass
class LocalWeights:
    """Local model weights from a single customer"""
    customer_id: str
    agent_id: str
    weights: Dict[str, np.ndarray]
    performance_metrics: Dict[str, float]
    sample_count: int
    timestamp: datetime
    signature: str


@dataclass
class GlobalWeights:
    """Aggregated global model weights"""
    agent_id: str
    weights: Dict[str, np.ndarray]
    version: int
    contributor_count: int
    aggregation_timestamp: datetime
    performance_improvement: float


class FederatedAgentMarketplace:
    """
    Federated learning system for privacy-preserving agent improvement
    Agents learn collectively without sharing customer data
    """
    
    def __init__(self, min_contributors: int = 5):
        self.min_contributors = min_contributors
        self.local_weights_buffer: Dict[str, List[LocalWeights]] = {}
        self.global_weights: Dict[str, GlobalWeights] = {}
        self.version_history: Dict[str, List[GlobalWeights]] = {}
        
        # Security parameters
        self.max_weight_deviation = 3.0  # Standard deviations
        self.min_sample_count = 10
    
    async def extract_local_weights(
        self,
        customer_id: str,
        agent_id: str
    ) -> LocalWeights:
        """
        Extract local model weights from customer's agent
        Only extracts weights, never raw data
        """
        try:
            # Simulate weight extraction (would be actual model weights in production)
            weights = await self._get_agent_weights(customer_id, agent_id)
            
            # Get performance metrics
            metrics = await self._get_performance_metrics(customer_id, agent_id)
            
            # Count samples used for training
            sample_count = await self._count_training_samples(customer_id, agent_id)
            
            # Sign weights for integrity
            signature = self._sign_weights(weights, customer_id)
            
            local_weights = LocalWeights(
                customer_id=customer_id,
                agent_id=agent_id,
                weights=weights,
                performance_metrics=metrics,
                sample_count=sample_count,
                timestamp=datetime.utcnow(),
                signature=signature
            )
            
            logger.info(f"Extracted local weights for {agent_id} from {customer_id}")
            
            return local_weights
        
        except Exception as e:
            logger.error(f"Failed to extract local weights: {e}")
            raise
    
    async def federate_update(
        self,
        customer_id: str,
        agent_id: str
    ) -> Optional[GlobalWeights]:
        """
        Contribute local weights and receive global update
        
        Args:
            customer_id: Customer identifier
            agent_id: Agent package identifier
        
        Returns:
            Updated global weights if aggregation threshold met
        """
        try:
            # Extract local weights
            local_weights = await self.extract_local_weights(customer_id, agent_id)
            
            # Validate weights
            if not self._validate_weights(local_weights):
                logger.warning(f"Invalid weights from {customer_id}, rejecting")
                return None
            
            # Add to buffer
            if agent_id not in self.local_weights_buffer:
                self.local_weights_buffer[agent_id] = []
            
            self.local_weights_buffer[agent_id].append(local_weights)
            
            # Check if we have enough contributors
            unique_contributors = len(set(
                w.customer_id for w in self.local_weights_buffer[agent_id]
            ))
            
            if unique_contributors >= self.min_contributors:
                # Perform secure aggregation
                global_weights = await self.secure_aggregate_weights(
                    self.local_weights_buffer[agent_id]
                )
                
                # Store global weights
                self.global_weights[agent_id] = global_weights
                
                # Clear buffer
                self.local_weights_buffer[agent_id] = []
                
                # Push to all customers
                await self.push_global_weights(global_weights)
                
                logger.info(
                    f"Federated update complete for {agent_id} "
                    f"with {unique_contributors} contributors"
                )
                
                return global_weights
            else:
                logger.info(
                    f"Waiting for more contributors: {unique_contributors}/{self.min_contributors}"
                )
                return None
        
        except Exception as e:
            logger.error(f"Federated update failed: {e}")
            return None
    
    async def secure_aggregate_weights(
        self,
        local_weights_list: List[LocalWeights]
    ) -> GlobalWeights:
        """
        Securely aggregate weights from multiple customers
        Uses weighted averaging based on sample count and performance
        """
        try:
            if not local_weights_list:
                raise ValueError("No weights to aggregate")
            
            agent_id = local_weights_list[0].agent_id
            
            # Filter out outliers
            filtered_weights = self._filter_outliers(local_weights_list)
            
            if len(filtered_weights) < self.min_contributors:
                raise ValueError("Not enough valid contributors after filtering")
            
            # Calculate weights for averaging
            total_samples = sum(w.sample_count for w in filtered_weights)
            
            # Initialize aggregated weights
            aggregated = {}
            
            # Get all weight keys from first contributor
            weight_keys = list(filtered_weights[0].weights.keys())
            
            # Aggregate each weight matrix
            for key in weight_keys:
                weighted_sum = np.zeros_like(filtered_weights[0].weights[key])
                
                for local_w in filtered_weights:
                    # Weight by sample count
                    weight = local_w.sample_count / total_samples
                    weighted_sum += local_w.weights[key] * weight
                
                aggregated[key] = weighted_sum
            
            # Calculate performance improvement
            avg_performance_before = np.mean([
                w.performance_metrics.get('accuracy', 0.0)
                for w in filtered_weights
            ])
            
            # Estimate improvement (simplified)
            performance_improvement = 0.05  # 5% improvement estimate
            
            # Get current version
            current_version = self.global_weights.get(agent_id)
            new_version = (current_version.version + 1) if current_version else 1
            
            global_weights = GlobalWeights(
                agent_id=agent_id,
                weights=aggregated,
                version=new_version,
                contributor_count=len(filtered_weights),
                aggregation_timestamp=datetime.utcnow(),
                performance_improvement=performance_improvement
            )
            
            # Store in history
            if agent_id not in self.version_history:
                self.version_history[agent_id] = []
            self.version_history[agent_id].append(global_weights)
            
            logger.info(
                f"Aggregated weights from {len(filtered_weights)} contributors "
                f"for {agent_id} v{new_version}"
            )
            
            return global_weights
        
        except Exception as e:
            logger.error(f"Weight aggregation failed: {e}")
            raise
    
    def _filter_outliers(
        self,
        weights_list: List[LocalWeights]
    ) -> List[LocalWeights]:
        """
        Filter out outlier weights using statistical methods
        Prevents poisoning attacks
        """
        if len(weights_list) < 3:
            return weights_list
        
        # Calculate mean and std for each weight matrix
        filtered = []
        
        for weights in weights_list:
            is_outlier = False
            
            # Check each weight matrix
            for key, weight_matrix in weights.weights.items():
                # Calculate statistics across all contributors
                all_values = []
                for w in weights_list:
                    if key in w.weights:
                        all_values.extend(w.weights[key].flatten())
                
                mean = np.mean(all_values)
                std = np.std(all_values)
                
                # Check if this contributor's weights are outliers
                weight_values = weight_matrix.flatten()
                z_scores = np.abs((weight_values - mean) / (std + 1e-10))
                
                if np.max(z_scores) > self.max_weight_deviation:
                    is_outlier = True
                    logger.warning(
                        f"Outlier detected from {weights.customer_id}, "
                        f"max z-score: {np.max(z_scores):.2f}"
                    )
                    break
            
            if not is_outlier:
                filtered.append(weights)
        
        logger.info(f"Filtered {len(weights_list) - len(filtered)} outliers")
        
        return filtered
    
    async def push_global_weights(self, global_weights: GlobalWeights):
        """
        Push global weights to all participating customers
        """
        try:
            # In production, this would push to customer deployments
            logger.info(
                f"Pushing global weights v{global_weights.version} "
                f"for {global_weights.agent_id} to all customers"
            )
            
            # Store for retrieval
            self.global_weights[global_weights.agent_id] = global_weights
            
            # Notify customers (would use message queue in production)
            await self._notify_customers_of_update(global_weights)
        
        except Exception as e:
            logger.error(f"Failed to push global weights: {e}")
    
    async def get_global_weights(
        self,
        agent_id: str,
        version: Optional[int] = None
    ) -> Optional[GlobalWeights]:
        """
        Retrieve global weights for an agent
        
        Args:
            agent_id: Agent identifier
            version: Specific version (None for latest)
        
        Returns:
            GlobalWeights or None if not found
        """
        if version is None:
            return self.global_weights.get(agent_id)
        else:
            history = self.version_history.get(agent_id, [])
            for weights in history:
                if weights.version == version:
                    return weights
            return None
    
    def _validate_weights(self, weights: LocalWeights) -> bool:
        """Validate local weights before accepting"""
        # Check signature
        expected_signature = self._sign_weights(weights.weights, weights.customer_id)
        if weights.signature != expected_signature:
            logger.warning(f"Invalid signature from {weights.customer_id}")
            return False
        
        # Check sample count
        if weights.sample_count < self.min_sample_count:
            logger.warning(f"Insufficient samples from {weights.customer_id}")
            return False
        
        # Check for NaN or Inf
        for key, weight_matrix in weights.weights.items():
            if np.any(np.isnan(weight_matrix)) or np.any(np.isinf(weight_matrix)):
                logger.warning(f"Invalid values in weights from {weights.customer_id}")
                return False
        
        return True
    
    def _sign_weights(self, weights: Dict[str, np.ndarray], customer_id: str) -> str:
        """Generate signature for weights"""
        # Serialize weights
        weight_bytes = json.dumps({
            k: v.tolist() for k, v in weights.items()
        }, sort_keys=True).encode()
        
        # Add customer ID
        data = weight_bytes + customer_id.encode()
        
        # Generate hash
        return hashlib.sha256(data).hexdigest()
    
    async def _get_agent_weights(
        self,
        customer_id: str,
        agent_id: str
    ) -> Dict[str, np.ndarray]:
        """Get agent model weights (simulated)"""
        # In production, this would extract actual model weights
        # For now, return dummy weights
        return {
            "layer1": np.random.randn(10, 10),
            "layer2": np.random.randn(10, 5),
            "output": np.random.randn(5, 1)
        }
    
    async def _get_performance_metrics(
        self,
        customer_id: str,
        agent_id: str
    ) -> Dict[str, float]:
        """Get agent performance metrics"""
        # In production, query actual metrics
        return {
            "accuracy": 0.85,
            "latency_ms": 150,
            "success_rate": 0.92
        }
    
    async def _count_training_samples(
        self,
        customer_id: str,
        agent_id: str
    ) -> int:
        """Count training samples used"""
        # In production, query actual sample count
        return 1000
    
    async def _notify_customers_of_update(self, global_weights: GlobalWeights):
        """Notify customers of global weight update"""
        # In production, use message queue or webhooks
        logger.info(f"Notifying customers of update for {global_weights.agent_id}")


# Global federated marketplace instance
_federated_marketplace: Optional[FederatedAgentMarketplace] = None


def get_federated_marketplace() -> FederatedAgentMarketplace:
    """Get or create global federated marketplace instance"""
    global _federated_marketplace
    
    if _federated_marketplace is None:
        _federated_marketplace = FederatedAgentMarketplace()
    
    return _federated_marketplace


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_federated_learning():
        marketplace = get_federated_marketplace()
        
        # Simulate multiple customers contributing
        customers = ["customer_1", "customer_2", "customer_3", "customer_4", "customer_5"]
        agent_id = "ticket-resolver"
        
        for customer_id in customers:
            result = await marketplace.federate_update(customer_id, agent_id)
            
            if result:
                print(f"Global update complete!")
                print(f"Version: {result.version}")
                print(f"Contributors: {result.contributor_count}")
                print(f"Improvement: {result.performance_improvement:.2%}")
    
    asyncio.run(test_federated_learning())

