# Initialize git if not done
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Complete certificate generator with image upload, batch generation, and QR verification"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/certificate-generator.git

# Push to main branch
git branch -M main
git push -u origin main
