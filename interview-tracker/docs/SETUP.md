# Setup Guide

Comprehensive installation and configuration guide for the Interview Preparation Tracker application.

## Table of Contents

- [System Requirements](#system-requirements)
- [Prerequisites Installation](#prerequisites-installation)
- [Application Installation](#application-installation)
- [Configuration](#configuration)
- [Verification](#verification)
- [Troubleshooting Setup Issues](#troubleshooting-setup-issues)
- [IDE Setup](#ide-setup)
- [Database Setup](#database-setup)

## System Requirements

### Minimum Requirements
- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+, CentOS 7+)
- **RAM**: 4 GB minimum, 8 GB recommended
- **Disk Space**: 2 GB free space
- **CPU**: Dual-core processor (2.0 GHz+)
- **Network**: Internet connection for dependency downloads

### Recommended Requirements
- **RAM**: 16 GB
- **Disk Space**: 5 GB free space (for dependencies and data)
- **CPU**: Quad-core processor (2.5 GHz+)
- **SSD**: Recommended for better performance

## Prerequisites Installation

### 1. Java Development Kit (JDK) 17+

#### Check if Java is already installed
```bash
java -version
```

If you see Java version 17 or higher, you can skip this step.

#### Installation

**Windows:**
1. Download JDK 17 from [Adoptium](https://adoptium.net/)
2. Run the installer
3. Add Java to PATH:
   - Right-click "This PC" → Properties → Advanced System Settings
   - Click "Environment Variables"
   - Under "System Variables", find "Path" and click "Edit"
   - Add `C:\Program Files\Eclipse Adoptium\jdk-17.X.X-hotspot\bin`
4. Verify: Open new Command Prompt and run `java -version`

**macOS:**
```bash
# Using Homebrew
brew install openjdk@17

# Add to PATH
echo 'export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Verify
java -version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install openjdk-17-jdk

# Verify
java -version
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install java-17-openjdk-devel

# Verify
java -version
```

### 2. Apache Maven 3.9+

#### Check if Maven is already installed
```bash
mvn -version
```

#### Installation

**Windows:**
1. Download Maven from [Apache Maven](https://maven.apache.org/download.cgi)
2. Extract to `C:\Program Files\Apache\maven`
3. Add Maven to PATH:
   - Add `C:\Program Files\Apache\maven\bin` to PATH (same steps as Java)
4. Verify: `mvn -version`

**macOS:**
```bash
# Using Homebrew
brew install maven

# Verify
mvn -version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install maven

# Verify
mvn -version
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install maven

# Verify
mvn -version
```

### 3. Node.js 18+ and npm

#### Check if Node.js is already installed
```bash
node -v
npm -v
```

#### Installation

**Windows:**
1. Download installer from [Node.js](https://nodejs.org/)
2. Run installer (includes npm automatically)
3. Verify: `node -v` and `npm -v`

**macOS:**
```bash
# Using Homebrew
brew install node@18

# Verify
node -v
npm -v
```

**Linux (Ubuntu/Debian):**
```bash
# Using NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify
node -v
npm -v
```

**Linux (CentOS/RHEL):**
```bash
# Using NodeSource repository
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# Verify
node -v
npm -v
```

### 4. Git

#### Check if Git is already installed
```bash
git --version
```

#### Installation

**Windows:**
1. Download from [Git for Windows](https://git-scm.com/download/win)
2. Run installer with default options

**macOS:**
```bash
# Using Homebrew
brew install git

# Or use Xcode Command Line Tools
xcode-select --install
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install git
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install git
```

## Application Installation

### 1. Clone or Download the Repository

```bash
# If using Git
git clone <repository-url>
cd interview-tracker

# Or download and extract the ZIP file
```

### 2. Backend Setup

#### Step 1: Navigate to backend directory
```bash
cd backend
```

#### Step 2: Build the application
```bash
mvn clean install -DskipTests
```

This command:
- `clean` - Removes previous build artifacts
- `install` - Compiles code, runs tests, and packages the application
- `-DskipTests` - Skips tests for faster initial setup

**Expected output:**
```
[INFO] BUILD SUCCESS
[INFO] Total time: 45.123 s
[INFO] Finished at: 2024-XX-XXTXX:XX:XX
```

#### Step 3: Start the backend server
```bash
mvn spring-boot:run
```

**Expected output:**
```
  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::               (v3.2.0)

...
Started InterviewTrackerApplication in 8.345 seconds
```

**The backend is now running on `http://localhost:8080`**

### 3. Frontend Setup

Open a **new terminal window** (keep the backend running).

#### Step 1: Navigate to frontend directory
```bash
cd interview-tracker/frontend
```

#### Step 2: Install dependencies
```bash
npm install
```

This will download all required npm packages (~200 MB).

**Expected output:**
```
added 1234 packages in 45s
```

#### Step 3: Start the development server
```bash
npm run dev
```

**Expected output:**
```
  VITE v5.0.0  ready in 1234 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**The frontend is now running on `http://localhost:3000`**

### 4. Access the Application

Open your web browser and navigate to:
```
http://localhost:3000
```

You should see the Interview Tracker dashboard.

## Configuration

### Backend Configuration

Configuration file: `backend/src/main/resources/application.properties`

#### Default Settings
```properties
# Server Configuration
server.port=8080

# Database Configuration
spring.datasource.url=jdbc:h2:file:./database/interviewtracker
spring.datasource.driverClassName=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=

# JPA/Hibernate
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=false
spring.jpa.database-platform=org.hibernate.dialect.H2Dialect

# H2 Console
spring.h2.console.enabled=true
spring.h2.console.path=/h2-console

# File Upload
spring.servlet.multipart.max-file-size=10MB
spring.servlet.multipart.max-request-size=10MB

# CORS
app.cors.allowed-origins=http://localhost:3000,http://localhost:5173

# File Storage
app.file-storage.upload-dir=./uploads
app.file-storage.backup-dir=./uploads/backups
```

#### Customization Options

**1. Change Server Port**
```properties
server.port=9090
```

**2. Change Database Location**
```properties
spring.datasource.url=jdbc:h2:file:/custom/path/database
```

**3. Increase File Upload Limit**
```properties
spring.servlet.multipart.max-file-size=50MB
spring.servlet.multipart.max-request-size=50MB
```

**4. Enable SQL Logging (for debugging)**
```properties
spring.jpa.show-sql=true
logging.level.org.hibernate.SQL=DEBUG
```

### Frontend Configuration

Configuration file: `frontend/vite.config.ts`

#### Default Settings
```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
})
```

#### Customization Options

**1. Change Frontend Port**
```typescript
server: {
  port: 5173,  // Change to any available port
}
```

**2. Change Backend API URL**
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:9090',  // Match your backend port
    changeOrigin: true,
  },
}
```

**3. Enable Network Access**
```typescript
server: {
  port: 3000,
  host: true,  // Expose to network
}
```

## Verification

### 1. Verify Backend

#### Check Health Endpoint
```bash
curl http://localhost:8080/api/topics
```

Expected: JSON response with empty array `[]` or existing topics

#### Access H2 Console
1. Navigate to: `http://localhost:8080/h2-console`
2. Use these credentials:
   - JDBC URL: `jdbc:h2:file:./database/interviewtracker`
   - Username: `sa`
   - Password: (leave blank)
3. Click "Connect"
4. You should see database tables listed

### 2. Verify Frontend

1. Open browser: `http://localhost:3000`
2. Check browser console (F12) for errors
3. Verify you can see the dashboard page
4. Try navigating to different pages (Topics, Analytics, Settings)

### 3. Test Integration

1. Create a new topic:
   - Click "Topics" → "Add New Topic"
   - Fill in details and save
   - Verify it appears in the list

2. Check backend received data:
   ```bash
   curl http://localhost:8080/api/topics
   ```
   You should see your created topic in the JSON response

## Troubleshooting Setup Issues

### Issue: "java: command not found"

**Solution:**
- Java is not installed or not in PATH
- Follow [Java Installation](#1-java-development-kit-jdk-17) steps
- Restart terminal/IDE after installation

### Issue: "mvn: command not found"

**Solution:**
- Maven is not installed or not in PATH
- Follow [Maven Installation](#2-apache-maven-39) steps
- Restart terminal after installation

### Issue: Port 8080 already in use

**Error:**
```
Web server failed to start. Port 8080 was already in use.
```

**Solutions:**

**Option 1:** Find and kill process using port 8080
```bash
# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8080 | xargs kill -9
```

**Option 2:** Change backend port
- Edit `application.properties`
- Set `server.port=9090`
- Update frontend `vite.config.ts` proxy target to match

### Issue: Port 3000 already in use

**Solution:**

**Option 1:** Kill process using port 3000
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:3000 | xargs kill -9
```

**Option 2:** Change frontend port
- Edit `vite.config.ts`
- Set `server.port: 5173`

### Issue: npm install fails with permission errors

**Solution:**

**macOS/Linux:**
```bash
sudo npm install -g npm
npm config set prefix ~/.npm-global
export PATH=~/.npm-global/bin:$PATH
```

**Windows:**
Run Command Prompt/PowerShell as Administrator

### Issue: Maven build fails - "cannot find symbol" errors for getters/setters

**Solution:**
This indicates Lombok annotation processor is not configured.

1. Verify `pom.xml` contains maven-compiler-plugin with Lombok:
```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <version>3.11.0</version>
    <configuration>
        <source>17</source>
        <target>17</target>
        <annotationProcessorPaths>
            <path>
                <groupId>org.projectlombok</groupId>
                <artifactId>lombok</artifactId>
                <version>1.18.30</version>
            </path>
        </annotationProcessorPaths>
    </configuration>
</plugin>
```

2. Run: `mvn clean install`

### Issue: Frontend shows "Cannot connect to backend"

**Symptoms:**
- Browser console shows network errors
- API calls return 404 or connection refused

**Solutions:**

1. Verify backend is running:
   ```bash
   curl http://localhost:8080/api/topics
   ```

2. Check browser console for actual error

3. Verify CORS configuration in `application.properties`:
   ```properties
   app.cors.allowed-origins=http://localhost:3000
   ```

4. Clear browser cache and reload

5. Check firewall settings allow port 8080 and 3000

### Issue: Database not persisting data

**Solution:**

1. Check database directory exists:
   ```bash
   ls -la database/
   ```

2. Verify file permissions:
   ```bash
   # macOS/Linux
   chmod -R 755 database/
   ```

3. Check `application.properties`:
   ```properties
   spring.jpa.hibernate.ddl-auto=update
   ```

4. Check H2 console for data

## IDE Setup

### IntelliJ IDEA

1. **Open Project:**
   - File → Open → Select `interview-tracker` folder

2. **Import Maven Project:**
   - IntelliJ should auto-detect and import
   - If not: Right-click `pom.xml` → Add as Maven Project

3. **Install Lombok Plugin:**
   - File → Settings → Plugins
   - Search "Lombok"
   - Install and restart

4. **Enable Annotation Processing:**
   - File → Settings → Build, Execution, Deployment → Compiler → Annotation Processors
   - Check "Enable annotation processing"

5. **Run Backend:**
   - Find `InterviewTrackerApplication.java`
   - Right-click → Run

6. **Run Frontend:**
   - Open Terminal in IntelliJ
   - `cd frontend && npm run dev`

### Visual Studio Code

1. **Open Project:**
   - File → Open Folder → Select `interview-tracker`

2. **Install Extensions:**
   - Extension Pack for Java
   - Spring Boot Extension Pack
   - ESLint
   - Prettier
   - Tailwind CSS IntelliSense

3. **Run Backend:**
   - Open integrated terminal
   - `cd backend && mvn spring-boot:run`

4. **Run Frontend:**
   - Open new terminal
   - `cd frontend && npm run dev`

### Eclipse

1. **Import Maven Project:**
   - File → Import → Maven → Existing Maven Projects
   - Select `backend` folder

2. **Install Lombok:**
   - Download `lombok.jar` from [projectlombok.org](https://projectlombok.org/)
   - Run: `java -jar lombok.jar`
   - Select Eclipse installation directory
   - Install

3. **Run Application:**
   - Right-click project → Run As → Spring Boot App

## Database Setup

### Default H2 Database

The application uses H2 database with file-based persistence.

**Location:** `./database/interviewtracker.mv.db`

**No setup required** - Database is created automatically on first run.

### Accessing H2 Console

1. Ensure backend is running
2. Navigate to: `http://localhost:8080/h2-console`
3. Connection settings:
   - JDBC URL: `jdbc:h2:file:./database/interviewtracker`
   - Username: `sa`
   - Password: (blank)
4. Click "Connect"

### Database Tables

The following tables are created automatically:

- `topic` - Interview topics
- `practice_session` - Study sessions
- `file_metadata` - Uploaded files
- `settings` - Application settings
- `pomodoro` - Pomodoro sessions
- `mock_interview` - Mock interview records
- `confidence_decay_rule` - Decay configuration
- `confidence_history` - Confidence changes audit
- `flashcard` - Spaced repetition flashcards
- `voice_note` - Audio recordings metadata

### Resetting Database

To start fresh:

1. Stop the backend server
2. Delete database directory:
   ```bash
   rm -rf database/
   ```
3. Start backend again - fresh database will be created

### Backing Up Database

**Manual Backup:**
```bash
cp -r database/ database_backup_$(date +%Y%m%d)/
```

**Using Application:**
1. Open Settings page
2. Click "Export Data"
3. JSON file with all data will be downloaded

## Next Steps

After successful setup:

1. Read [USER_GUIDE.md](USER_GUIDE.md) to learn how to use features
2. Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API reference
3. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
4. See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment

## Getting Help

If you encounter issues not covered here:

1. Check the main [README.md](../README.md) troubleshooting section
2. Review application logs:
   - Backend: Check terminal output
   - Frontend: Browser console (F12)
3. Search existing issues on GitHub
4. Open a new issue with:
   - Operating system
   - Java, Maven, Node versions
   - Complete error message
   - Steps to reproduce

---

**Setup complete!** You're ready to start using the Interview Preparation Tracker.
