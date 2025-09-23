#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect if running in Cygwin
if [[ $(uname -o) == "Cygwin" ]]; then
    IS_CYGWIN=true
    print_status "Cygwin environment detected"
else
    IS_CYGWIN=false
fi

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Function to create directory if it doesn't exist
create_dir() {
    if [ ! -d "$1" ]; then
        mkdir -p "$1"
        print_status "Created directory: $1"
    else
        print_warning "Directory already exists: $1"
    fi
}

# Function to create file with content
create_file() {
    if [ ! -f "$1" ]; then
        cat > "$1" << EOL
$2
EOL
        print_status "Created file: $1"
    else
        print_warning "File already exists: $1"
    fi
}

# Function to convert Cygwin path to Windows path
cygpath_to_win() {
    if [ "$IS_CYGWIN" = true ]; then
        cygpath -w "$1"
    else
        echo "$1"
    fi
}

# Function to find Java installations on Windows
find_java_windows() {
    local java_versions=()
    
    # Check common Java installation paths
    local possible_paths=(
        "/cygdrive/c/Program Files/Java"
        "/cygdrive/c/Program Files (x86)/Java"
        "/cygdrive/c/Java"
    )
    
    for path in "${possible_paths[@]}"; do
        if [ -d "$path" ]; then
            for jdk in "$path"/*; do
                if [ -d "$jdk" ] && [[ "$jdk" =~ jdk[0-9] ]]; then
                    local version=$(basename "$jdk" | grep -o '[0-9]\+' | head -1)
                    if [ -n "$version" ]; then
                        java_versions+=("$version:$jdk")
                    fi
                fi
            done
        fi
    done
    
    echo "${java_versions[@]}"
}

# Main script
print_step "Starting MSSQL JDBC Client Project Setup for Cygwin..."

# Create project directory
PROJECT_DIR="mssql-jdbc-client"
create_dir "$PROJECT_DIR"
cd "$PROJECT_DIR"

print_step "Creating directory structure..."
create_dir "src"
create_dir "lib"
create_dir "classes"

print_step "Creating Java source files..."

# DatabaseConfig.java
create_file "src/DatabaseConfig.java" 'import java.io.FileInputStream;
import java.io.IOException;
import java.util.Properties;

public class DatabaseConfig {
    private String server;
    private int port;
    private String databaseName;
    private String username;
    private String password;
    private String instanceName;
    private boolean trustServerCertificate;
    private boolean encrypt;
    private int loginTimeout;

    public DatabaseConfig(String configFile) throws IOException {
        Properties props = new Properties();
        try (FileInputStream fis = new FileInputStream(configFile)) {
            props.load(fis);
        }
        
        this.server = props.getProperty("server", "localhost");
        this.port = Integer.parseInt(props.getProperty("port", "1433"));
        this.databaseName = props.getProperty("databaseName", "");
        this.username = props.getProperty("username", "");
        this.password = props.getProperty("password", "");
        this.instanceName = props.getProperty("instanceName", "");
        this.trustServerCertificate = Boolean.parseBoolean(
            props.getProperty("trustServerCertificate", "true"));
        this.encrypt = Boolean.parseBoolean(props.getProperty("encrypt", "false"));
        this.loginTimeout = Integer.parseInt(props.getProperty("loginTimeout", "30"));
    }

    // Getters
    public String getServer() { return server; }
    public int getPort() { return port; }
    public String getDatabaseName() { return databaseName; }
    public String getUsername() { return username; }
    public String getPassword() { return password; }
    public String getInstanceName() { return instanceName; }
    public boolean isTrustServerCertificate() { return trustServerCertificate; }
    public boolean isEncrypt() { return encrypt; }
    public int getLoginTimeout() { return loginTimeout; }

    public String getConnectionUrl() {
        StringBuilder url = new StringBuilder();
        url.append("jdbc:sqlserver://").append(server).append(":").append(port);
        
        if (!instanceName.isEmpty()) {
            url.append(";instanceName=").append(instanceName);
        }
        
        url.append(";databaseName=").append(databaseName);
        url.append(";trustServerCertificate=").append(trustServerCertificate);
        url.append(";encrypt=").append(encrypt);
        url.append(";loginTimeout=").append(loginTimeout);
        
        return url.toString();
    }
}'

# MSSQLClient.java
create_file "src/MSSQLClient.java" 'import java.sql.*;
import java.io.IOException;

public class MSSQLClient {
    private DatabaseConfig config;
    private Connection connection;

    public MSSQLClient(String configFile) throws IOException {
        this.config = new DatabaseConfig(configFile);
    }

    public boolean connect() {
        try {
            // Load SQL Server JDBC driver
            Class.forName("com.microsoft.sqlserver.jdbc.SQLServerDriver");
            
            // Establish connection
            connection = DriverManager.getConnection(
                config.getConnectionUrl(), 
                config.getUsername(), 
                config.getPassword()
            );
            
            System.out.println("Connected to SQL Server successfully!");
            return true;
            
        } catch (ClassNotFoundException e) {
            System.err.println("SQL Server JDBC Driver not found: " + e.getMessage());
            return false;
        } catch (SQLException e) {
            System.err.println("Connection failed: " + e.getMessage());
            return false;
        }
    }

    public void disconnect() {
        if (connection != null) {
            try {
                connection.close();
                System.out.println("Disconnected from SQL Server.");
            } catch (SQLException e) {
                System.err.println("Error closing connection: " + e.getMessage());
            }
        }
    }

    public ResultSet executeQuery(String sql) throws SQLException {
        if (connection == null || connection.isClosed()) {
            throw new SQLException("Connection is not established");
        }
        
        Statement statement = connection.createStatement();
        return statement.executeQuery(sql);
    }

    public int executeUpdate(String sql) throws SQLException {
        if (connection == null || connection.isClosed()) {
            throw new SQLException("Connection is not established");
        }
        
        Statement statement = connection.createStatement();
        return statement.executeUpdate(sql);
    }

    public PreparedStatement prepareStatement(String sql) throws SQLException {
        if (connection == null || connection.isClosed()) {
            throw new SQLException("Connection is not established");
        }
        
        return connection.prepareStatement(sql);
    }

    // Test database connection
    public boolean testConnection() {
        try {
            if (connection != null && !connection.isClosed()) {
                String testQuery = "SELECT 1 AS test_result";
                ResultSet rs = executeQuery(testQuery);
                if (rs.next()) {
                    System.out.println("Database connection test: PASSED");
                    return true;
                }
            }
            return false;
        } catch (SQLException e) {
            System.err.println("Connection test failed: " + e.getMessage());
            return false;
        }
    }

    // Get database metadata
    public void printDatabaseInfo() {
        try {
            if (connection != null && !connection.isClosed()) {
                DatabaseMetaData metaData = connection.getMetaData();
                System.out.println("Database Product: " + metaData.getDatabaseProductName());
                System.out.println("Database Version: " + metaData.getDatabaseProductVersion());
                System.out.println("Driver Name: " + metaData.getDriverName());
                System.out.println("Driver Version: " + metaData.getDriverVersion());
            }
        } catch (SQLException e) {
            System.err.println("Error getting database info: " + e.getMessage());
        }
    }
}'

# MSSQLClientExample.java
create_file "src/MSSQLClientExample.java" 'import java.sql.ResultSet;
import java.sql.SQLException;

public class MSSQLClientExample {
    public static void main(String[] args) {
        MSSQLClient client = null;
        
        try {
            // Initialize client with configuration file
            client = new MSSQLClient("JDBS_Connection.ini");
            
            // Connect to database
            if (client.connect()) {
                // Test connection
                client.testConnection();
                
                // Print database information
                client.printDatabaseInfo();
                
                // Example: Execute a simple query
                System.out.println("\\nExecuting sample query:");
                String query = "SELECT name FROM sys.databases WHERE database_id > 4";
                ResultSet rs = client.executeQuery(query);
                
                System.out.println("User databases:");
                while (rs.next()) {
                    System.out.println("- " + rs.getString("name"));
                }
                
                // Example: Using prepared statement
                String preparedQuery = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = ?";
                var pstmt = client.prepareStatement(preparedQuery);
                pstmt.setString(1, "BASE TABLE");
                
                ResultSet tables = pstmt.executeQuery();
                System.out.println("\\nTables in database:");
                while (tables.next()) {
                    System.out.println("- " + tables.getString("TABLE_NAME"));
                }
            }
            
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        } finally {
            if (client != null) {
                client.disconnect();
            }
        }
    }
}'

print_step "Creating configuration file..."

# JDBS_Connection.ini
create_file "JDBS_Connection.ini" '[database]
server=localhost
port=1433
databaseName=master
username=sa
password=your_password_here
instanceName=
trustServerCertificate=true
encrypt=false
loginTimeout=30'

print_step "Creating Cygwin-optimized run script..."

# run-cygwin.sh
create_file "run-cygwin.sh" '#!/bin/bash

# MSSQL JDBC Client Runner for Cygwin

# Colors for output
RED="\\033[0;31m"
GREEN="\\033[0;32m"
YELLOW="\\033[1;33m"
BLUE="\\033[0;34m"
NC="\\033[0m" # No Color

echo -e "${GREEN}MSSQL JDBC Client Runner (Cygwin)${NC}"

# Detect Cygwin
if [[ $(uname -o) != "Cygwin" ]]; then
    echo -e "${RED}This script is designed for Cygwin environment${NC}"
    exit 1
fi

# Function to find Java installations
find_java_installations() {
    local java_versions=()
    
    echo -e "${BLUE}Searching for Java installations...${NC}"
    
    # Check Windows Java installations
    local possible_paths=(
        "/cygdrive/c/Program Files/Java"
        "/cygdrive/c/Program Files (x86)/Java"
        "/cygdrive/c/Java"
    )
    
    for path in "${possible_paths[@]}"; do
        if [ -d "$path" ]; then
            for jdk in "$path"/*; do
                if [ -d "$jdk" ] && [[ "$jdk" =~ jdk[0-9] ]]; then
                    local version=$(basename "$jdk" | grep -o '[0-9]\+' | head -1)
                    if [ -n "$version" ] && [ -f "$jdk/bin/javac.exe" ]; then
                        java_versions+=("$version:$jdk")
                        echo -e "  Found Java $version: $jdk"
                    fi
                fi
            done
        fi
    done
    
    # Check if java is in PATH
    if command -v java > /dev/null 2>&1; then
        local path_java=$(which java)
        local path_javac=$(which javac 2>/dev/null || echo "")
        echo -e "  Found Java in PATH: $path_java"
        if [ -n "$path_javac" ]; then
            java_versions+=("PATH:$path_java")
        fi
    fi
    
    if [ ${#java_versions[@]} -eq 0 ]; then
        echo -e "${YELLOW}No Java installations found!${NC}"
        return 1
    fi
    
    return 0
}

# Function to set up Java environment
setup_java() {
    echo ""
    echo -e "${BLUE}Available Java options:${NC}"
    echo "1. Use Java from PATH (if available)"
    echo "2. Auto-detect and use highest Java version"
    echo "3. Manual Java path selection"
    echo -n "Select option (1-3): "
    read option
    
    case $option in
        1)
            if command -v java > /dev/null 2>&1; then
                JAVA_CMD="java"
                JAVAC_CMD="javac"
                echo -e "${GREEN}Using Java from PATH${NC}"
                java -version
            else
                echo -e "${RED}Java not found in PATH${NC}"
                return 1
            fi
            ;;
        2)
            # Auto-detect highest Java version
            highest_version=0
            highest_path=""
            
            for entry in $(find "/cygdrive/c/Program Files/Java" "/cygdrive/c/Program Files (x86)/Java" -name "jdk*" -type d 2>/dev/null); do
                version=$(echo "$entry" | grep -o '[0-9]\+' | head -1)
                if [ -n "$version" ] && [ "$version" -gt "$highest_version" ] && [ -f "$entry/bin/javac.exe" ]; then
                    highest_version=$version
                    highest_path=$entry
                fi
            done
            
            if [ -n "$highest_path" ]; then
                JAVA_CMD="$highest_path/bin/java.exe"
                JAVAC_CMD="$highest_path/bin/javac.exe"
                echo -e "${GREEN}Using Java $highest_version from: $highest_path${NC}"
                "$JAVA_CMD" -version
            else
                echo -e "${RED}No Java installation found${NC}"
                return 1
            fi
            ;;
        3)
            echo -n "Enter full path to Java bin directory (e.g., /cygdrive/c/Program Files/Java/jdk1.8.0_351/bin): "
            read java_path
            if [ -f "$java_path/javac.exe" ]; then
                JAVA_CMD="$java_path/java.exe"
                JAVAC_CMD="$java_path/javac.exe"
                echo -e "${GREEN}Using Java from: $java_path${NC}"
                "$JAVA_CMD" -version
            else
                echo -e "${RED}Invalid Java path${NC}"
                return 1
            fi
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            return 1
            ;;
    esac
    
    return 0
}

# Function to select JDBC driver based on Java version
select_jdbc_driver() {
    local java_version_output=$("$JAVA_CMD" -version 2>&1)
    local java_version=$(echo "$java_version_output" | grep -o '" [0-9]\+' | grep -o '[0-9]\+' | head -1)
    
    if [ -z "$java_version" ]; then
        # Try alternative version detection
        java_version=$(echo "$java_version_output" | head -1 | grep -o '[0-9]' | head -1)
    fi
    
    echo -e "${BLUE}Detected Java version: ${java_version:-unknown}${NC}"
    
    case $java_version in
        8|1.8)
            JDBC_JAR="lib/mssql-jdbc-12.4.1.jre8.jar"
            echo -e "${GREEN}Using JDBC driver for Java 8${NC}"
            ;;
        21|17|11|9|10|12|13|14|15|16|18|19|20)
            JDBC_JAR="lib/mssql-jdbc-12.4.1.jre11.jar"
            echo -e "${GREEN}Using JDBC driver for Java 11+${NC}"
            ;;
        *)
            echo -e "${YELLOW}Unknown Java version, trying Java 11+ driver${NC}"
            JDBC_JAR="lib/mssql-jdbc-12.4.1.jre11.jar"
            ;;
    esac
    
    if [ ! -f "$JDBC_JAR" ]; then
        echo -e "${RED}JDBC driver not found: $JDBC_JAR${NC}"
        echo "Please run ./download-drivers.sh first"
        return 1
    fi
}

# Main execution
find_java_installations
if ! setup_java; then
    exit 1
fi

if ! select_jdbc_driver; then
    exit 1
fi

# Check if JDBS_Connection.ini exists
if [ ! -f "JDBS_Connection.ini" ]; then
    echo -e "${RED}Error: JDBS_Connection.ini not found!${NC}"
    exit 1
fi

# Create classes directory if it doesn'\''t exist
mkdir -p classes

# Convert paths to Windows format for Java
WIN_CLASSES_PATH=$(cygpath -w "$(pwd)/classes")
WIN_JDBC_PATH=$(cygpath -w "$(pwd)/$JDBC_JAR")
WIN_SRC_PATH=$(cygpath -w "$(pwd)/src")

echo -e "${BLUE}Compiling Java files...${NC}"
# Compile with Windows paths
"$JAVAC_CMD" -cp "$WIN_JDBC_PATH" -d "$WIN_CLASSES_PATH" "$WIN_SRC_PATH"/*.java

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Compilation successful!${NC}"
    
    echo -e "${BLUE}Running MSSQL Client Example...${NC}"
    "$JAVA_CMD" -cp "$WIN_CLASSES_PATH;$WIN_JDBC_PATH" MSSQLClientExample
else
    echo -e "${RED}Compilation failed!${NC}"
    exit 1
fi'

print_step "Creating download script for JDBC drivers..."

# download-drivers.sh
create_file "download-drivers.sh" '#!/bin/bash

# Script to download MSSQL JDBC drivers for Cygwin

echo "Downloading MSSQL JDBC drivers for Cygwin..."

# Create lib directory if it doesn'\''t exist
mkdir -p lib

# Download Java 8 compatible driver
echo "Downloading Java 8 driver..."
curl -L -o lib/mssql-jdbc-12.4.1.jre8.jar https://repo1.maven.org/maven2/com/microsoft/sqlserver/mssql-jdbc/12.4.1.jre8/mssql-jdbc-12.4.1.jre8.jar

# Download Java 11+ compatible driver (works with Java 21)
echo "Downloading Java 11+ driver..."
curl -L -o lib/mssql-jdbc-12.4.1.jre11.jar https://repo1.maven.org/maven2/com/microsoft/sqlserver/mssql-jdbc/12.4.1.jre11/mssql-jdbc-12.4.1.jre11.jar

echo "Download complete!"
echo "Files downloaded:"
ls -la lib/'

print_step "Creating Windows batch file as backup..."

# run-windows.bat
create_file "run-windows.bat" '@echo off
title MSSQL JDBC Client Runner (Windows)

echo MSSQL JDBC Client Runner - Windows
echo.

:: Check if JDBC drivers exist
if not exist "lib\\mssql-jdbc-12.4.1.jre8.jar" (
    echo Error: JDBC drivers not found!
    echo Please run download-drivers.sh from Cygwin first
    pause
    exit /b 1
)

:: Check if configuration exists
if not exist "JDBS_Connection.ini" (
    echo Error: JDBS_Connection.ini not found!
    pause
    exit /b 1
)

:: Use Java from PATH
echo Using Java from PATH...
java -version >nul 2>&1
if errorlevel 1 (
    echo Error: Java not found in PATH!
    echo Please ensure Java is installed and in your PATH
    pause
    exit /b 1
)

echo.
echo Compiling Java files...
javac -cp "lib\\mssql-jdbc-12.4.1.jre8.jar" -d classes src\\*.java

if %errorlevel% equ 0 (
    echo Compilation successful!
    echo.
    echo Running MSSQL Client Example...
    java -cp "classes;lib\\mssql-jdbc-12.4.1.jre8.jar" MSSQLClientExample
) else (
    echo Compilation failed!
)

pause'

print_step "Creating Cygwin-specific README..."

# README-CYGWIN.md
create_file "README-CYGWIN.md" '# MSSQL JDBC Client - Cygwin Setup

A Java JDBC client for connecting to Microsoft SQL Server from Cygwin bash on Windows.

## Quick Start

```bash
# 1. Download JDBC drivers
./download-drivers.sh

# 2. Edit configuration file
notepad JDBS_Connection.ini  # or use your favorite editor

# 3. Run the application
./run-cygwin.sh