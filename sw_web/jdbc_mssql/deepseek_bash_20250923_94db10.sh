#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Main script
print_step "Starting MSSQL JDBC Client Project Setup..."

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

print_step "Creating run scripts..."

# run.sh for Linux/Mac
create_file "run.sh" '#!/bin/bash

# Script to compile and run MSSQL JDBC Client with Java version selection

# Colors for output
RED=\"\\033[0;31m\"
GREEN=\"\\033[0;32m\"
YELLOW=\"\\033[1;33m\"
NC=\"\\033[0m\" # No Color

echo -e \"${GREEN}MSSQL JDBC Client Runner${NC}\"
echo \"Available Java versions:\"
echo \"1. Java 8\"
echo \"2. Java 21\"
echo -n \"Select Java version (1 or 2): \"
read java_choice

case $java_choice in
    1)
        JAVA_CMD=\"java\"
        JAVAC_CMD=\"javac\"
        JDBC_JAR=\"lib/mssql-jdbc-12.4.1.jre8.jar\"
        JAVA_VERSION=\"8\"
        ;;
    2)
        # Try to find Java 21 specifically
        if command -v java21 &> /dev/null; then
            JAVA_CMD=\"java21\"
            JAVAC_CMD=\"javac21\"
        elif command -v java &> /dev/null && java -version 2>&1 | grep -q \"21\"; then
            JAVA_CMD=\"java\"
            JAVAC_CMD=\"javac\"
        else
            echo -e \"${YELLOW}Java 21 not found in PATH, using default java command${NC}\"
            JAVA_CMD=\"java\"
            JAVAC_CMD=\"javac\"
        fi
        JDBC_JAR=\"lib/mssql-jdbc-12.4.1.jre11.jar\"
        JAVA_VERSION=\"21\"
        ;;
    *)
        echo -e \"${RED}Invalid selection. Using Java 8 as default.${NC}\"
        JAVA_CMD=\"java\"
        JAVAC_CMD=\"javac\"
        JDBC_JAR=\"lib/mssql-jdbc-12.4.1.jre8.jar\"
        JAVA_VERSION=\"8\"
        ;;
esac

echo -e \"${GREEN}Using Java $JAVA_VERSION${NC}\"

# Verify Java installation
if ! command -v $JAVA_CMD &> /dev/null; then
    echo -e \"${RED}Error: $JAVA_CMD not found!${NC}\"
    exit 1
fi

echo \"Java version:\"
$JAVA_CMD -version

# Check if JDBS_Connection.ini exists
if [ ! -f \"JDBS_Connection.ini\" ]; then
    echo -e \"${RED}Error: JDBS_Connection.ini not found!${NC}\"
    echo \"Creating a template configuration file...\"
    cat > JDBS_Connection.ini << EOL
[database]
server=localhost
port=1433
databaseName=master
username=sa
password=your_password_here
trustServerCertificate=true
encrypt=false
loginTimeout=30
EOL
    echo -e \"${YELLOW}Please edit JDBS_Connection.ini with your database credentials${NC}\"
    exit 1
fi

# Check if JDBC driver exists
if [ ! -f \"$JDBC_JAR\" ]; then
    echo -e \"${RED}JDBC driver for Java $JAVA_VERSION not found at $JDBC_JAR${NC}\"
    exit 1
fi

# Create classes directory if it doesn'\''t exist
mkdir -p classes

# Compile Java files
echo \"Compiling Java files with Java $JAVA_VERSION...\"
$JAVAC_CMD -cp \"$JDBC_JAR\" -d classes src/*.java

if [ $? -eq 0 ]; then
    echo -e \"${GREEN}Compilation successful!${NC}\"
    
    # Run the example
    echo \"Running MSSQL Client Example with Java $JAVA_VERSION...\"
    $JAVA_CMD -cp \"classes:$JDBC_JAR\" MSSQLClientExample
else
    echo -e \"${RED}Compilation failed!${NC}\"
    exit 1
fi'

# run.bat for Windows
create_file "run.bat" '@echo off
title MSSQL JDBC Client Runner

echo MSSQL JDBC Client Runner
echo.
echo Available Java versions:
echo 1. Java 8
echo 2. Java 21
echo.
set /p java_choice=\"Select Java version (1 or 2): \"

if \"%java_choice%\"==\"1\" (
    set JAVA_CMD=java
    set JAVAC_CMD=javac
    set JDBC_JAR=lib\\mssql-jdbc-12.4.1.jre8.jar
    set JAVA_VERSION=8
) else if \"%java_choice%\"==\"2\" (
    set JAVA_CMD=java
    set JAVAC_CMD=javac
    set JDBC_JAR=lib\\mssql-jdbc-12.4.1.jre11.jar
    set JAVA_VERSION=21
) else (
    echo Invalid selection. Using Java 8 as default.
    set JAVA_CMD=java
    set JAVAC_CMD=javac
    set JDBC_JAR=lib\\mssql-jdbc-12.4.1.jre8.jar
    set JAVA_VERSION=8
)

echo Using Java %JAVA_VERSION%

:: Check if JDBS_Connection.ini exists
if not exist \"JDBS_Connection.ini\" (
    echo Error: JDBS_Connection.ini not found!
    echo Creating a template configuration file...
    (
        echo [database]
        echo server=localhost
        echo port=1433
        echo databaseName=master
        echo username=sa
        echo password=your_password_here
        echo trustServerCertificate=true
        echo encrypt=false
        echo loginTimeout=30
    ) > JDBS_Connection.ini
    echo Please edit JDBS_Connection.ini with your database credentials
    pause
    exit /b 1
)

:: Check if JDBC driver exists
if not exist \"%JDBC_JAR%\" (
    echo JDBC driver for Java %JAVA_VERSION% not found at %JDBC_JAR%
    pause
    exit /b 1
)

:: Create classes directory if it doesn'\''t exist
if not exist \"classes\" mkdir classes

:: Compile Java files
echo Compiling Java files with Java %JAVA_VERSION%...
%JAVAC_CMD% -cp \"%JDBC_JAR%\" -d classes src\\*.java

if %errorlevel% equ 0 (
    echo Compilation successful!
    
    :: Run the example
    echo Running MSSQL Client Example with Java %JAVA_VERSION%...
    %JAVA_CMD% -cp \"classes;%JDBC_JAR%\" MSSQLClientExample
) else (
    echo Compilation failed!
)

pause'

print_step "Creating download script for JDBC drivers..."

# download-drivers.sh
create_file "download-drivers.sh" '#!/bin/bash

# Script to download MSSQL JDBC drivers

echo "Downloading MSSQL JDBC drivers..."

# Download Java 8 compatible driver
echo "Downloading Java 8 driver..."
wget -O lib/mssql-jdbc-12.4.1.jre8.jar https://repo1.maven.org/maven2/com/microsoft/sqlserver/mssql-jdbc/12.4.1.jre8/mssql-jdbc-12.4.1.jre8.jar

# Download Java 11+ compatible driver (works with Java 21)
echo "Downloading Java 11+ driver..."
wget -O lib/mssql-jdbc-12.4.1.jre11.jar https://repo1.maven.org/maven2/com/microsoft/sqlserver/mssql-jdbc/12.4.1.jre11/mssql-jdbc-12.4.1.jre11.jar

echo "Download complete!"
echo "Files downloaded:"
ls -la lib/'

print_step "Creating README file..."

# README.md
create_file "README.md" '# MSSQL JDBC Client

A Java JDBC client for connecting to Microsoft SQL Server with configuration file support.

## Project Structure
