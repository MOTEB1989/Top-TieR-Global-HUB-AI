/**
 * Express middleware to enforce defensive limits for incoming requests.
 */
module.exports = function securityMiddleware(req, res, next) {
  const bodySize = req.socket.bytesRead;
  if (bodySize > 10 * 1024 * 1024) {
    return res.status(413).json({ error: 'Payload too large' });
  }

  const forbiddenPatterns = [/(ghp_|github_pat_)[A-Za-z0-9]{36}/, /(sk-|pk-)[A-Za-z0-9]{32,}/];
  const serialized = JSON.stringify(req.body || '');
  if (forbiddenPatterns.some((pattern) => pattern.test(serialized))) {
    return res.status(400).json({ error: 'Potential secret detected in request body' });
  }

  return next();
};
