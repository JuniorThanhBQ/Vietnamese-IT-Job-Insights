FROM node:20-alpine

WORKDIR /app

RUN addgroup -S app && adduser -S appuser -G app

COPY package*.json ./
RUN npm install && chown -R appuser:app /app

COPY . .

USER appuser

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
