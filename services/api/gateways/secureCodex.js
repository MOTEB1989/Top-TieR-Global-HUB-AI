const crypto = require('crypto');

class SecureCodexGateway {
  constructor({ encryptionKey, repositoryId } = {}) {
    this.encryptionKey = this.#resolveKey(encryptionKey);
    this.repositoryId = repositoryId || 'unknown-repo';
  }

  sanitizePayload(payload) {
    const sensitivePatterns = [
      /(ghp_|github_pat_)[A-Za-z0-9]{36}/g,
      /(sk-|pk-)[A-Za-z0-9]{32,}/g,
      /-----BEGIN [A-Z ]+PRIVATE KEY-----[\s\S]+?-----END [A-Z ]+PRIVATE KEY-----/g,
      /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,
    ];

    let serialized = JSON.stringify(payload);
    for (const pattern of sensitivePatterns) {
      serialized = serialized.replace(pattern, '[REDACTED]');
    }
    return JSON.parse(serialized);
  }

  encryptPayload(payload) {
    const iv = crypto.randomBytes(12);
    const cipher = crypto.createCipheriv('aes-256-gcm', this.encryptionKey, iv);
    const serialized = JSON.stringify(payload);
    const encrypted = Buffer.concat([cipher.update(serialized, 'utf8'), cipher.final()]);
    const tag = cipher.getAuthTag();
    return {
      iv: iv.toString('hex'),
      tag: tag.toString('hex'),
      data: encrypted.toString('hex'),
    };
  }

  decryptPayload({ iv, tag, data }) {
    const decipher = crypto.createDecipheriv(
      'aes-256-gcm',
      this.encryptionKey,
      Buffer.from(iv, 'hex'),
    );
    decipher.setAuthTag(Buffer.from(tag, 'hex'));
    const decrypted = Buffer.concat([
      decipher.update(Buffer.from(data, 'hex')),
      decipher.final(),
    ]);
    return JSON.parse(decrypted.toString('utf8'));
  }

  buildSignature(payload) {
    const hmac = crypto.createHmac('sha256', this.encryptionKey);
    hmac.update(`${this.repositoryId}:${payload.iv}:${payload.data}`);
    return hmac.digest('hex');
  }

  #resolveKey(key) {
    const value = key || process.env.CODEX_ENCRYPTION_KEY;
    if (!value) {
      throw new Error('Missing CODEX_ENCRYPTION_KEY');
    }
    if (value.length !== 64) {
      throw new Error('CODEX_ENCRYPTION_KEY must be 32 bytes represented as 64 hex characters');
    }
    return Buffer.from(value, 'hex');
  }
}

module.exports = SecureCodexGateway;
