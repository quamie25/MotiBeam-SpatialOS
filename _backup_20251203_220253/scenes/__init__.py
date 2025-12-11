"""
MotiBeam Spatial OS - Scenes/Realms Module
All available spatial computing realms
"""

# Consumer Realms
from .home_realm import HomeRealm
from .clinical_realm import ClinicalRealm
from .education_realm import EducationRealm
from .transport_realm import TransportRealm

# Operations Realms
from .emergency_realm import EmergencyRealm
from .security_realm import SecurityRealm
from .enterprise_realm import EnterpriseRealm
from .aviation_realm import AviationRealm
from .maritime_realm import MaritimeRealm

__all__ = [
    # Consumer
    'HomeRealm',
    'ClinicalRealm',
    'EducationRealm',
    'TransportRealm',
    # Operations
    'EmergencyRealm',
    'SecurityRealm',
    'EnterpriseRealm',
    'AviationRealm',
    'MaritimeRealm'
]
