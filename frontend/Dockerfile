FROM node:18-alpine

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./
RUN npm install --production

COPY . /app

EXPOSE 3000

CMD ["npm", "start"]
