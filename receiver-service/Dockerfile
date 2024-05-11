FROM openjdk:17-jdk-alpine
ARG JAR_FILE=target/*.jar
COPY ${JAR_FILE} receiver-service.jar
ENTRYPOINT ["java","-jar","/receiver-service.jar"]
EXPOSE 8091