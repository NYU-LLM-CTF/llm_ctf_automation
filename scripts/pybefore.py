import sys
import requests
from datetime import datetime, timezone
import re

def pep_503_normalize(name):
    return re.sub(r"[-_.]+", "-", name).lower()

def get_latest_version_before_date(package_name, cutoff_date, recurse=True):
    """
    Fetch the latest version of the package that was released before the specified cutoff_date.

    Args:
    package_name (str): The name of the package on PyPI.
    cutoff_date (str): The cutoff date in ISO 8601 format (YYYY-MM-DD).

    Returns:
    str: The version of the latest release before the cutoff date or None if no release matches.
    """
    # Convert cutoff_date to a datetime object for comparison
    cutoff_datetime = datetime.fromisoformat(cutoff_date).replace(tzinfo=timezone.utc)

    # Normalize the package name per PEP 503
    package_name = pep_503_normalize(package_name)

    # Request package information from PyPI
    response = requests.get(f'https://pypi.org/pypi/{package_name}/json')
    if response.status_code != 200:
        return None

    data = response.json()
    releases = data.get('releases', {})

    # Initialize variables to find the latest version before the cutoff date
    latest_version = None
    latest_release_date = datetime.min.replace(tzinfo=timezone.utc)

    # Iterate over all versions and their releases
    for version, release_info in releases.items():
        for release in release_info:
            release_date = datetime.fromisoformat(release['upload_time_iso_8601'].replace('Z', '+00:00'))
            # Check if this release is before the cutoff and after the last found release
            if release_date < cutoff_datetime and release_date > latest_release_date:
                latest_version = version
                latest_release_date = release_date

    version_info = {package_name: latest_version}
    if recurse:
        # Use deps.dev to find the dependencies of this package, and then check their versions
        url = f'https://api.deps.dev/v3/systems/pypi/packages/{package_name}/versions/{latest_version}:dependencies'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for dep in data.get('nodes', []):
                if dep['relation'] == 'SELF':
                    continue
                dep_name = dep['versionKey']['name']
                dep_version = get_latest_version_before_date(dep_name, cutoff_date, recurse=False)
                version_info.update(dep_version)

    return version_info

# Example usage
cutoff_date = sys.argv[1]
for package_name in sys.argv[2:]:
    version_info = get_latest_version_before_date(package_name, cutoff_date)
    print(" ".join(f"{name}=={version}" for name, version in version_info.items()))
