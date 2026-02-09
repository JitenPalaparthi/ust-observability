# ---- build stage ----
FROM maven:3.9-eclipse-temurin-22 AS build
WORKDIR /workspace
COPY pom.xml .
COPY src ./src
RUN mvn -q -DskipTests package

# ---- runtime stage ----
FROM eclipse-temurin:22-jre
WORKDIR /app
COPY --from=build /workspace/target/demo-observability-0.1.0.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java","-jar","/app/app.jar"]
