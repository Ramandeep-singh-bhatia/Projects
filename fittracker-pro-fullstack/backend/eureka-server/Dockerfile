# Multi-stage build for Eureka Server
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app

# Copy parent pom and common module first for better caching
COPY pom.xml .
COPY common/pom.xml ./common/
COPY common/src ./common/src

# Copy eureka-server
COPY eureka-server/pom.xml ./eureka-server/
COPY eureka-server/src ./eureka-server/src

# Build the application
RUN mvn clean package -pl eureka-server -am -DskipTests

# Runtime stage
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# Add application user
RUN addgroup -S spring && adduser -S spring -G spring
USER spring:spring

# Copy the built artifact
COPY --from=build /app/eureka-server/target/*.jar app.jar

# Expose port
EXPOSE 8761

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8761/actuator/health || exit 1

# Run the application
ENTRYPOINT ["java", "-jar", "app.jar"]
