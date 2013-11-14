@echo off
echo Beginning deployment of HTResearch...
cd /
echo Backing up existing files...
7z a deployment-backup.zip C:\HTRES-DT-JOB1 >nul
cd C:\htresearch_repo_clone\HTResearch
echo Fetching latest changes from Github...
git pull origin master >nul
cd ..
echo Copying new build into IIS directory...
xcopy /sY HTResearch C:\HTRES-DT-JOB1 >nul
echo Resolving static resources..."
xcopy /sY C:\HTRES-DT-JOB1\HTResearch\WebClient\WebClient\static C:\HTRES-DT-JOB1\HTResearch\WebClient\static >nul
echo Deployment complete!