@echo off
echo Warming up Docker images in VrrifiHire_dind (Parallel)...
echo This will open multiple background processes to pull images simultaneously.
echo Please wait until all are done.

echo Pulling Python...
start /b docker exec VrrifiHire_dind docker pull public.ecr.aws/docker/library/python:3.12-alpine

echo Pulling Node.js...
start /b docker exec VrrifiHire_dind docker pull public.ecr.aws/docker/library/node:20-alpine

echo Pulling Java (Amazon Corretto 21)...
start /b docker exec VrrifiHire_dind docker pull public.ecr.aws/amazoncorretto/amazoncorretto:21

echo Pulling GCC (C/C++)...
start /b docker exec VrrifiHire_dind docker pull public.ecr.aws/docker/library/gcc:14

echo Pulling Go...
start /b docker exec VrrifiHire_dind docker pull public.ecr.aws/docker/library/golang:1.21-alpine

echo Pulling PHP...
start /b docker exec VrrifiHire_dind docker pull public.ecr.aws/docker/library/php:8.2-cli-alpine

echo Pulling Ruby...
start /b docker exec VrrifiHire_dind docker pull public.ecr.aws/docker/library/ruby:3.2-alpine

echo Pulling Rust...
start /b docker exec VrrifiHire_dind docker pull public.ecr.aws/docker/library/rust:1.75-bookworm

echo Pulling Swift...
start /b docker exec VrrifiHire_dind docker pull swift:5.10

echo Pulling Dart...
start /b docker exec VrrifiHire_dind docker pull dart:stable

echo Pulling Scala...
start /b docker exec VrrifiHire_dind docker pull sbtscala/scala-sbt:eclipse-temurin-17.0.4_1.7.1_3.2.0

echo Pulling C# (.NET SDK)...
start /b docker exec VrrifiHire_dind docker pull mcr.microsoft.com/dotnet/sdk:8.0

echo Pulling Postgres...
start /b docker exec VrrifiHire_dind docker pull public.ecr.aws/docker/library/postgres:15-alpine

echo Pulling MySQL...
start /b docker exec VrrifiHire_dind docker pull public.ecr.aws/docker/library/mysql:8.0-debian

echo.
echo All pull commands initiated in background.
echo Monitor your network usage or wait a few minutes before running code.
echo.
pause
