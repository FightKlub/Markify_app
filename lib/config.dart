/// API Configuration for Markify App
class Config {
  // IMPORTANT: Update this URL after deploying to Render
  
  // Current: Local IP address (PC must be running Flask backend)
  static const String apiBaseUrl = 'http://10.244.8.99:5000';
  
  // After Render deployment, change to:
  // static const String apiBaseUrl = 'https://markify-backend-xxxx.onrender.com';
}