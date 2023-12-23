version=$(python -c 'import sky; print(sky.clouds.service_catalog.constants.CATALOG_SCHEMA_VERSION)')
mkdir -p ~/.sky/catalogs/${version}
cd ~/.sky/catalogs/${version}

# GCP
#pip install lxml
# Fetch U.S. regions for GCP
#python -m sky.clouds.service_catalog.data_fetchers.fetch_gcp
# Fetch the specified zones for GCP
#python -m sky.clouds.service_catalog.data_fetchers.fetch_gcp --zones northamerica-northeast1-a us-east1-b us-east1-c
# Fetch U.S. zones for GCP, excluding the specified zones
#python -m sky.clouds.service_catalog.data_fetchers.fetch_gcp --exclude us-east1-a us-east1-b
# Fetch all regions for GCP
#python -m sky.clouds.service_catalog.data_fetchers.fetch_gcp --all-regions
# Run in single-threaded mode. This is useful when multiple processes don't work well with the GCP client due to SSL issues.
#python -m sky.clouds.service_catalog.data_fetchers.fetch_gcp --single-threaded

# Azure
# Fetch U.S. regions for Azure
#python -m sky.clouds.service_catalog.data_fetchers.fetch_azure
# Fetch all regions for Azure
python -m sky.clouds.service_catalog.data_fetchers.fetch_azure --all-regions
# Run in single-threaded mode. This is useful when multiple processes don't work well with the Azure client due to SSL issues.
#python -m sky.clouds.service_catalog.data_fetchers.fetch_azure --single-threaded
# Fetch the specified regions for Azure
#python -m sky.clouds.service_catalog.data_fetchers.fetch_azure --regions japaneast australiaeast uksouth
# Fetch U.S. regions for Azure, excluding the specified regions
#python -m sky.clouds.service_catalog.data_fetchers.fetch_azure --exclude centralus eastus