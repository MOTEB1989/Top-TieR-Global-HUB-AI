const crypto = require('crypto');

class SecureLogger {
  log(userId, action) {
    const hash = crypto.createHash('sha256')
      .update(userId + process.env.SALT)
      .digest('hex')
      .slice(0, 16);
    console.log(`[AUDIT] ${hash} ${action} ${Date.now()}`);
  }
}

module.exports = SecureLogger;
