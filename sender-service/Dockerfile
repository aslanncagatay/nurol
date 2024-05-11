FROM openjdk:17-jdk-alpine
ARG JAR_FILE=target/*.jar
COPY ${JAR_FILE} sender-service.jar
ENTRYPOINT ["java","-jar","/sender-service.jar"]
EXPOSE 8090