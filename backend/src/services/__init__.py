# Services module for ODG Platform
from .blockchain_service import (
    BlockchainService,
    BlockchainConfig,
    get_blockchain_service,
    simulate_blockchain_record,
    WEB3_AVAILABLE
)

__all__ = [
    'BlockchainService',
    'BlockchainConfig',
    'get_blockchain_service',
    'simulate_blockchain_record',
    'WEB3_AVAILABLE'
]
