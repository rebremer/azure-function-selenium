FROM mcr.microsoft.com/azure-functions/python:4-python3.12

# 0. Install essential packages
RUN apt-get update \
    && apt-get install -y \
        wget \
        sudo
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN sudo apt-get install -y ./google-chrome-stable_current_amd64.deb

# 2. Install Chrome driver used by Selenium
RUN pip3 install selenium
RUN pip3 install webdriver-manager

# 4. Finally, copy python code to image
COPY . /home/site/wwwroot

# 5. Install other packages in requirements.txt
RUN cd /home/site/wwwroot && \
    pip install -r requirements.txt