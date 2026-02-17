FROM public.ecr.aws/docker/library/node:20.11.1-alpine

WORKDIR /app

COPY package.json ./
RUN npm install --omit=dev

COPY src ./src

ENV EXECUTOR_PORT=4000
EXPOSE 4000

CMD ["npm", "start"]


