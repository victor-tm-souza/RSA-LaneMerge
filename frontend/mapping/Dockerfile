# Use an official Node.js runtime as a parent image
FROM node:14

# Set the working directory to /app
WORKDIR /app

# Copy package.json and package-lock.json to the container
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code to the container
COPY . .

# Build the React app
RUN npm run build

RUN apt-get update && apt-get install -y python3 python3-pip
COPY server.py ./
COPY startFrontend.sh ./
RUN pip3 install websockets

# Expose port 3000 for the React app
EXPOSE 3000

# Start the React app
CMD ./startFrontend.sh
