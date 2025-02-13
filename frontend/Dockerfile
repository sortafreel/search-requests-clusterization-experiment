FROM node:23.7.0-alpine

# install simple http server for serving static content
RUN npm install -g http-server

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $HOME
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# copy both 'package.json' and 'package-lock.json' (if available)
COPY package*.json $APP_HOME

# install project dependencies
RUN npm install

# copy project
COPY . $APP_HOME