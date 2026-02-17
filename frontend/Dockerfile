FROM public.ecr.aws/docker/library/node:20.11.1-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

ARG REACT_APP_API_BASE_URL=http://localhost:8001/api
ENV REACT_APP_API_BASE_URL=$REACT_APP_API_BASE_URL

RUN npm run build

FROM public.ecr.aws/docker/library/nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf


COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

