@echo off
echo Building and pushing Total Keepers Backend...
echo.

echo Step 1: Building backend image...
podman build -t total-keepers-be:latest .
if %errorlevel% neq 0 (
    echo ERROR: Failed to build backend image
    pause
    exit /b 1
)

echo Step 2: Tagging backend image...
podman tag total-keepers-be:latest totalkeepersregistry.azurecr.io/total-keepers-be:v1.1.3
if %errorlevel% neq 0 (
    echo ERROR: Failed to tag backend image
    pause
    exit /b 1
)

echo Step 3: Pushing backend image to registry...
podman push totalkeepersregistry.azurecr.io/total-keepers-be:v1.1.3
if %errorlevel% neq 0 (
    echo ERROR: Failed to push backend image
    pause
    exit /b 1
)

echo.
echo SUCCESS: Backend image built and pushed successfully!
echo Image: totalkeepersregistry.azurecr.io/total-keepers-be:v1.1.3
pause