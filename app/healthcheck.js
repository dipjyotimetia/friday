const http = require('http');

const options = {
  host: '0.0.0.0',
  port: process.env.PORT || 3000,
  timeout: 2000,
  path: '/'
};

const request = http.request(options, (res) => {
  console.log(`Health check status: ${res.statusCode}`);
  if (res.statusCode === 200) {
    process.exit(0);
  } else {
    process.exit(1);
  }
});

request.on('error', function(err) {
  console.log('Health check error:', err.message);
  process.exit(1);
});

request.end();