"""
Enhanced Privacy Score Service - Unified Privacy Assessment
Combines VPN, Caller ID, Location, and Network Security into comprehensive score
"""

from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

from .vpn_service import vpn_service
from .caller_id_service import caller_id_service
from .location_service import location_service
from .network_security_service import network_security_service