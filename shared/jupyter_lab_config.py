# JupyterLab configuration for system theme
# This configuration enables JupyterLab to respect the system theme preference

c = get_config()

# Set the default URL to open JupyterLab
c.LabApp.default_url = '/lab'

# Note: In JupyterLab 4.x, theme is configured through browser settings
# The actual theme configuration is done via overrides.json
