FROM node:20-alpine
WORKDIR /app
COPY package.json tsconfig.json next.config.js next-env.d.ts ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "run", "start"]
