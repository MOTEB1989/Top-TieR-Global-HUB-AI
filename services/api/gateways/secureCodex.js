const crypto = require('crypto');

class SecureCodexGateway {
  constructor() {
    this.key = process.env.CODEX_ENCRYPTION_KEY;
  }

  encrypt(data) {
    const cipher = crypto.createCipher('aes-256-cbc', this.key);
    return cipher.update(JSON.stringify(data), 'utf8', 'hex') + cipher.final('hex');
  }

  sanitize(text) {
    return text.replace(/(sk-|ghp_)[A-Za-z0-9]{20,}/g, '[REDACTED]');
  }
}

module.exports = SecureCodexGateway;
