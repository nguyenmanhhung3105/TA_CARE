"""Compatibility composition; product implementations live in their own packages."""
from .shared.routes import SharedControllers
from .shared.removal import AdminRemovalControllers
from ..sites.khovieclam.routes import KhoControllers
from ..sites.tuhoso.routes import ProfileControllers
from ..sites.tuhoso.recruitment import RecruitmentControllers
from ..sites.tacare.routes import HubControllers


class TacareLive(KhoControllers, ProfileControllers, RecruitmentControllers, HubControllers, AdminRemovalControllers, SharedControllers):
    pass
