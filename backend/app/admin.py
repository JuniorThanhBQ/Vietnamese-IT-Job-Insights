"""
SQLAdmin backoffice configuration module.
Provides admin dashboard and CRUD operations for Companies and Jobs.
"""

import psutil
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sqladmin import Admin, ModelView, BaseView, expose
from app.models.db_models import Company, Job
from app.models.database import engine


class CompanyAdmin(ModelView, model=Company):  # type: ignore[call-arg]
    """SQLAdmin view configuration for the Company model."""

    column_list = ["id", "name", "source_site", "created_date"]
    column_searchable_list = ["name", "industry"]
    column_filters = ["source_site", "industry"]
    form_columns = [
        "name",
        "source_id",
        "source_site",
        "logo_url",
        "website_url",
        "company_size",
        "industry",
        "address",
        "raw_metadata",
    ]
    name = "Company"
    name_plural = "Companies"
    icon = "fa fa-building"


class JobAdmin(ModelView, model=Job):  # type: ignore[call-arg]
    """SQLAdmin view configuration for the Job model."""

    column_list = [
        "id",
        "title",
        "source_site",
        "salary_raw",
        "seniority",
        "is_active",
        "created_date",
    ]
    column_searchable_list = ["title", "salary_raw"]
    column_filters = ["source_site", "seniority", "remote_policy", "is_active"]
    form_columns = [
        "company_id",
        "source_id",
        "source_site",
        "title",
        "url",
        "salary_min",
        "salary_max",
        "salary_currency",
        "salary_raw",
        "seniority",
        "remote_policy",
        "employment_type",
        "description",
        "requirements",
        "is_active",
        "raw_metadata",
    ]
    name = "Job"
    name_plural = "Jobs"
    icon = "fa fa-briefcase"


class SystemMonitorAdmin(BaseView):
    """Custom SQLAdmin view to monitor server health, CPU, and RAM consumption."""

    name = "System Monitor"
    icon = "fa fa-heartbeat"

    # pylint: disable=unused-argument
    @expose("/monitor", methods=["GET"])
    async def monitor_page(self, request):
        """Render a system status dashboard page using Bootstrap."""
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory()._asdict()
        ram_mb = {
            k: f"{v / (1024 * 1024):.1f} MB" if isinstance(v, (int, float)) else v
            for k, v in ram.items()
        }

        html_content = f"""
        <html>
        <head>
            <title>System Monitor</title>
            <link rel="stylesheet"
                  href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
            <link rel="stylesheet"
                  href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        </head>
        <body class="p-4 bg-light">
            <div class="container bg-white p-4 rounded shadow-sm mt-4">
                <h1 class="mb-4 text-primary">
                    <i class="fa-solid fa-heartbeat"></i> System Monitor & Health
                </h1>
                <p class="text-muted">
                    Real-time status for the Vietnamese IT Job Insights backend server.
                </p>
                <hr>
                <div class="row">
                    <div class="col-md-6 mb-4">
                        <div class="card border-0 bg-light p-4 rounded-3">
                            <h4 class="text-secondary mb-3">
                                <i class="fa-solid fa-microchip"></i> CPU Usage
                            </h4>
                            <div class="progress mb-3" style="height: 35px;">
                                <div class="progress-bar progress-bar-striped progress-bar-animated
                                            bg-success" role="progressbar" style="width: {cpu}%"
                                     aria-valuenow="{cpu}" aria-valuemin="0" aria-valuemax="100">
                                     {cpu}%
                                </div>
                            </div>
                            <span class="text-muted small">
                                Current load percentage across all virtual cores.
                            </span>
                        </div>
                    </div>
                    <div class="col-md-6 mb-4">
                        <div class="card border-0 bg-light p-4 rounded-3">
                            <h4 class="text-secondary mb-3">
                                <i class="fa-solid fa-memory"></i> RAM Usage
                            </h4>
                            <div class="mb-3">
                                <strong>Total Memory:</strong> {ram_mb.get('total')}<br>
                                <strong>Used:</strong> {ram_mb.get('used')}
                                (<strong>{ram_mb.get('percent')}%</strong>)<br>
                                <strong>Available:</strong> {ram_mb.get('available')}
                            </div>
                            <div class="progress" style="height: 35px;">
                                <div class="progress-bar progress-bar-striped progress-bar-animated
                                            bg-info" role="progressbar"
                                     style="width: {ram_mb.get('percent')}%"
                                     aria-valuenow="{ram_mb.get('percent')}"
                                     aria-valuemin="0" aria-valuemax="100">
                                     {ram_mb.get('percent')}%
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="mt-4">
                    <a href="/admin" class="btn btn-secondary">
                        <i class="fa-solid fa-arrow-left"></i> Back to Dashboard
                    </a>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)


def init_admin(app: FastAPI) -> None:
    """Initialize SQLAdmin with registered views."""
    admin = Admin(app, engine, title="IT Job Insights Admin")
    admin.add_view(CompanyAdmin)
    admin.add_view(JobAdmin)
    admin.add_view(SystemMonitorAdmin)
