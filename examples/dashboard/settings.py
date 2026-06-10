from fastvk.dashboard import BaseDashboard, DashboardConfig

class Dashboard(BaseDashboard):
    config = DashboardConfig(
        dashboard=True,
    )
    
dashboard = Dashboard()