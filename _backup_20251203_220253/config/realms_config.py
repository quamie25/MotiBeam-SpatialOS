"""
MotiBeam Spatial OS - Realms Configuration
Configuration for all available realms in the system
"""

# Realm symbols with emoji and ASCII fallbacks
# Note: Actual rendering handled by theme_neon.py with emoji font support
REALM_SYMBOLS = {
    'home': {'emoji': '🏡', 'fallback': '[H]'},
    'clinical': {'emoji': '⚕️', 'fallback': '[+]'},
    'education': {'emoji': '📚', 'fallback': '[E]'},
    'transport': {'emoji': '🚗', 'fallback': '[T]'},
    'emergency': {'emoji': '🚨', 'fallback': '[!]'},
    'security': {'emoji': '🛡️', 'fallback': '[S]'},
    'enterprise': {'emoji': '🏢', 'fallback': '[B]'},
    'aviation': {'emoji': '✈️', 'fallback': '[A]'},
    'maritime': {'emoji': '⚓', 'fallback': '[M]'},
}

# REALM ORDER FOR AUTO-DEMO: Consumer realms first, then ops realms
AUTO_DEMO_ORDER = [
    "home",
    "clinical",
    "education",
    "transport",
    "emergency",
    "security",
    "enterprise",
    "aviation",
    "maritime"
]

REALMS_CONFIG = {
    # ========== CONSUMER REALMS ==========
    "home": {
        "name": "Home Realm",
        "description": "Smart Home, Family Management, Ambient Living",
        "icon": "🏡",
        "priority": "NORMAL",
        "module_path": "scenes.home_realm",
        "class_name": "HomeRealm",
        "sensors": ["presence", "environmental", "security", "energy", "devices"],
        "ai_modules": ["routine_automation", "family_coordination", "energy_optimization"]
    },
    "clinical": {
        "name": "Clinical Realm",
        "description": "Health Monitoring, Wellness Tracking, Medical Assistance",
        "icon": "⚕️",
        "priority": "HIGH",
        "module_path": "scenes.clinical_realm",
        "class_name": "ClinicalRealm",
        "sensors": ["vitals", "activity", "sleep", "glucose", "blood_pressure"],
        "ai_modules": ["health_monitoring", "predictive_wellness", "medication_management"]
    },
    "education": {
        "name": "Education Realm",
        "description": "Learning Environments, Study Focus, Knowledge Management",
        "icon": "📚",
        "priority": "NORMAL",
        "module_path": "scenes.education_realm",
        "class_name": "EducationRealm",
        "sensors": ["focus", "comprehension", "environmental", "devices"],
        "ai_modules": ["adaptive_learning", "knowledge_mapping", "study_optimization"]
    },
    "transport": {
        "name": "Transport Realm",
        "description": "Automotive HUD, Navigation, Driver Assistance",
        "icon": "🚗",
        "priority": "HIGH",
        "module_path": "scenes.transport_realm",
        "class_name": "TransportRealm",
        "sensors": ["cameras", "radar", "lidar", "gps", "vehicle_telemetry"],
        "ai_modules": ["navigation", "collision_avoidance", "traffic_prediction"]
    },

    # ========== OPERATIONS REALMS ==========
    "emergency": {
        "name": "Emergency Response Realm",
        "description": "911 Dispatch, Crisis Response, Medical Emergency",
        "icon": "🚨",
        "priority": "CRITICAL",
        "module_path": "scenes.emergency_realm",
        "class_name": "EmergencyRealm",
        "sensors": ["thermal", "audio", "motion", "vital_signs", "location"],
        "ai_modules": ["triage", "resource_allocation", "crisis_prediction"]
    },
    "security": {
        "name": "Security & Surveillance Realm",
        "description": "Perimeter Defense, Access Control, Threat Detection",
        "icon": "🛡️",
        "priority": "HIGH",
        "module_path": "scenes.security_realm",
        "class_name": "SecurityRealm",
        "sensors": ["cameras", "motion", "biometric", "acoustic", "radar"],
        "ai_modules": ["facial_recognition", "behavior_analysis", "threat_assessment"]
    },
    "enterprise": {
        "name": "Enterprise Workspace Realm",
        "description": "Office Environments, Collaboration, Productivity",
        "icon": "🏢",
        "priority": "NORMAL",
        "module_path": "scenes.enterprise_realm",
        "class_name": "EnterpriseRealm",
        "sensors": ["presence", "activity", "environmental", "devices"],
        "ai_modules": ["scheduling", "resource_optimization", "collaboration_assist"]
    },
    "aviation": {
        "name": "Aviation Control Realm",
        "description": "Air Traffic Control, Cockpit Integration, Flight Safety",
        "icon": "✈️",
        "priority": "CRITICAL",
        "module_path": "scenes.aviation_realm",
        "class_name": "AviationRealm",
        "sensors": ["radar", "altimeter", "weather", "collision_avoidance", "navigation"],
        "ai_modules": ["traffic_control", "flight_path_optimization", "weather_prediction"]
    },
    "maritime": {
        "name": "Maritime Operations Realm",
        "description": "Vessel Navigation, Port Operations, Marine Safety",
        "icon": "⚓",
        "priority": "HIGH",
        "module_path": "scenes.maritime_realm",
        "class_name": "MaritimeRealm",
        "sensors": ["sonar", "gps", "weather", "collision_radar", "depth"],
        "ai_modules": ["navigation", "traffic_management", "weather_routing"]
    }
}

# System-wide settings
SYSTEM_CONFIG = {
    "version": "MOS-1.0",
    "codename": "Kickstarter Demo",
    "demo_cycle_duration": 12,  # seconds per realm (optimized for wall readability)
    "auto_loop_delay": 2,  # seconds between realms in auto-loop
    "max_sensor_refresh": 1.0,  # seconds
    "ai_processing_delay": 0.5  # seconds
}
