## Azure Function in Python running selenium webdriver using a custom docker image
The base Azure Function image does not contain the necessary chromium packages to run selenium webdriver. This project creates a custom docker image with the required libraries such that it can be run as Azure Function.

- For more details, see blog https://towardsdatascience.com/how-to-create-a-selenium-web-scraper-in-azure-functions-f156fd074503

### 1. Prerequisites

- [Docker desktop](https://docs.docker.com/get-docker/)
- [Azure Container Registry](https://docs.microsoft.com/nl-nl/azure/container-registry/container-registry-get-started-portal)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
- [Azure Core Tools version 2.x](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash#v2)
- [(optional) Visual Studio Code](https://code.visualstudio.com/)

### 2. Create custom docker image using the DockerFile in docker desktop

Run the following commands that installs chromium, chrome driver and selenium on top of the Azure Function base image:

`$acr_id = "<<your acr>>.azurecr.io"`  
`docker login $acr_id -u <<your username>> -p <<your password>>`  
`docker build --tag $acr_id/selenium .`  
`docker push $acr_id/selenium:latest`

### 3. Create Azure Function using docker image

Run the following commands:

`$rg = "<<your resource group name>>"`  
`$loc = "<<your location>>"`  
`$plan = "<<your azure function plan P1v2>>"`  
`$stor = "<<your storage account adhering to function>>"`  
`$fun = "<<your azure function name>>"`  
`$acr_id = "<<your acr>>.azurecr.io"`  

`az group create -n $rg -l $loc`  
`az storage account create -n $stor -g $rg --sku Standard_LRS`  
`az appservice plan create --name $plan --resource-group $rg --sku P1v2 --is-linux`  
`az functionapp create --resource-group $rg --os-type Linux --plan $plan --deployment-container-image-name $acr_id/selenium:latest --name $fun --storage-account $stor --docker-registry-server-user <<your acr username>> --docker-registry-server-password <<your acr password>> --functions-version 4`

### 4. Add Data Lake Account to store scraping results

Run the following commands:

`$rg = "<<your resource group name>>"`
`$fun = "<<your azure function name>>"`
`$adls = "<<your storage account>>"`
`$sub_id = "<<your subscription id>>"`
`$container_name = "scraperesults"`
`# Create adlsgen2`
`az storage account create --name $adls --resource-group $rg --location $loc --sku Standard_RAGRS --kind StorageV2 --enable-hierarchical-namespace true`
`az storage container create --account-name $adls -n $container_name# Assign identity to function and set params`
`az webapp identity assign --name $fun --resource-group $rg`
`az functionapp config appsettings set --name $fun --resource-group $rg --settings par_storage_account_name=$adls par_storage_container_name=$container_name# Give fun MI RBAC role to ADLS gen 2 account`
`$fun_object_id = az functionapp identity show --name $fun --resource-group $rg --query 'principalId' -o tsv`
`New-AzRoleAssignment -ObjectId $fun_object_id -RoleDefinitionName "Storage Blob Data Contributor" -Scope  "/subscriptions/$sub_id/resourceGroups/$rg/providers/Microsoft.Storage/storageAccounts/$adls/blobServices/default"`

### 4. Run Azure Function as HTTP trigger

Test the Function in the portal or in your browser. The following code in __init__.py will return all URLs in the following webpage:

`import azure.functions as func`
`from selenium import webdriver`
`from selenium.webdriver.chrome.options import Options`
`from selenium.webdriver.chrome.service import Service`
`from selenium.webdriver.common.by import By`
`from webdriver_manager.chrome import ChromeDriverManager`

`def main(req: func.HttpRequest) -> func.HttpResponse:`  

&nbsp;&nbsp;&nbsp;&nbsp;`options = Options()`
&nbsp;&nbsp;&nbsp;&nbsp;`options.add_argument('--headless')`
&nbsp;&nbsp;&nbsp;&nbsp;`options.add_argument('--no-sandbox')`
&nbsp;&nbsp;&nbsp;&nbsp;`options.add_argument('--disable-dev-shm-usage')`
&nbsp;&nbsp;&nbsp;&nbsp;`driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)`

&nbsp;&nbsp;&nbsp;&nbsp;`driver.get('http://www.ubuntu.com/')`
&nbsp;&nbsp;&nbsp;&nbsp;`links = driver.find_elements(By.TAG_NAME, "a")`