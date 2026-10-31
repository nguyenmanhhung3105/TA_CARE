"""Register models in compatibility order, grouped by business responsibility."""
from .foundation import identity
from .foundation import map_settings
from .foundation import taxonomy
from .jobs import hr_job
from .jobs import job_requirement
from .profiles import profile
from .profiles import profile_details
from .foundation import privacy
from .exchange import matching
from .exchange import connection
from .operations import operations
from .jobs import job_revision
from .exchange import profile_comparison
from .marketplace import flexible_work
from .profiles import recruitment_profile
from .marketplace import seasonal_scope
from .exchange import work_review
