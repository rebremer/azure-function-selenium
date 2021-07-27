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
`az functionapp create --resource-group $rg --os-type Linux --plan $plan --deployment-container-image-name $acr_id/selenium:latest --name $fun --storage-account $stor --docker-registry-server-user <<your acr username>> --docker-registry-server-password <<your acr password>> `

### 4. Run Azure Function as HTTP trigger

Test the Function in the portal or in your browser. The following code in __init__.py will return all URLs in the following webpage:

`import azure.functions as func`  
`from selenium import webdriver`  

`def main(req: func.HttpRequest) -> func.HttpResponse:`  

&nbsp;&nbsp;&nbsp;&nbsp;`chrome_options = webdriver.ChromeOptions()`  
&nbsp;&nbsp;&nbsp;&nbsp;`chrome_options.add_argument('--headless')`  
&nbsp;&nbsp;&nbsp;&nbsp;`chrome_options.add_argument('--no-sandbox')`  
&nbsp;&nbsp;&nbsp;&nbsp;`chrome_options.add_argument('--disable-dev-shm-usage')`  

&nbsp;&nbsp;&nbsp;&nbsp;`driver = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=chrome_options)`  
&nbsp;&nbsp;&nbsp;&nbsp;`driver.get('http://www.ubuntu.com/')`  
&nbsp;&nbsp;&nbsp;&nbsp;`links = driver.find_elements_by_tag_name("a")`  
